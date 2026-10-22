"""Direcciones hacker − control en el último token del prompt, y qué las mueve (Entender, H1-H3).

La dirección de cada semilla se calcula en los prompts del PILOTO (variante `base`, con métrica):
    d_s[capa] = media sobre pedidos de (activación del hacker_s − activación del control_s)
y se evalúa en los prompts de TEST, que ningún análisis vio. Así no hay fuga entre cálculo y evaluación.

Salidas:
  1. Estabilidad (H2): coseno entre las direcciones de las semillas, contra el azar (1/√4096 ≈ 0,016),
     y contra la dirección "hacker oficial − base".
  2. Contexto (H3, parte interna): proyección media de cada modelo sobre la dirección, por variante,
     restando la de `sin_metrica`.
  3. Predicción (H1): con --juzgado, AUC de la proyección (antes de escribir) para predecir si la
     respuesta generada después fue juzgada como hack.
Guarda las direcciones en direcciones.npz (para el steering).

Uso, en la VM (o local, con las activaciones copiadas):
    python direcciones.py --semillas 1,2,3,4,5 --juzgado ~/results/test_gen_juzgado.jsonl
"""

import argparse
import json
import os

import numpy as np

CAPAS = [8, 12, 16, 20, 24, 28, 32, 36]


def cargar(carpeta, etiqueta, modelo):
    return np.load(os.path.join(carpeta, etiqueta, f"{modelo}.npy"), mmap_mode="r")


def ids(carpeta, etiqueta):
    return [tuple(x) for x in json.load(open(os.path.join(carpeta, etiqueta, "ids.json")))]


def coseno(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def media(X, filas, capa):
    return np.asarray(X[filas, capa], np.float32).mean(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts", default=os.path.expanduser("~/acts_prompt"))
    ap.add_argument("--ref", default="piloto")
    ap.add_argument("--eval", default="test")
    ap.add_argument("--semillas", default="1,2,3,4,5")
    ap.add_argument("--juzgado", default=None, help="jsonl de juez.py piloto sobre las respuestas de test")
    ap.add_argument("--umbral", type=float, default=0.5)
    ap.add_argument("--out", default=os.path.expanduser("~/results/direcciones.npz"))
    a = ap.parse_args()
    semillas = [int(s) for s in a.semillas.split(",")]

    # --- 1. direcciones por semilla (prompts de referencia, con métrica) ---
    ids_ref = ids(a.acts, a.ref)
    filas_ref = [i for i, (_, v) in enumerate(ids_ref) if v == "base"]
    print(f"Referencia: {len(filas_ref)} pedidos `base` de '{a.ref}'\n")
    d = {}
    for s in semillas:
        H, C = cargar(a.acts, a.ref, f"hacker{s}"), cargar(a.acts, a.ref, f"control{s}")
        d[s] = np.stack([media(H, filas_ref, c) - media(C, filas_ref, c) for c in range(H.shape[1])])
    try:
        B, O = cargar(a.acts, a.ref, "base"), cargar(a.acts, a.ref, "oficial1")
        d_of = np.stack([media(O, filas_ref, c) - media(B, filas_ref, c) for c in range(O.shape[1])])
    except FileNotFoundError:
        d_of = None

    print("1. ESTABILIDAD: coseno entre semillas (hacker_s − control_s)")
    print(f"   azar ≈ ±{1 / np.sqrt(d[semillas[0]].shape[1]):.3f}")
    print(f"   {'capa':>5s} {'min':>7s} {'media':>7s} {'max':>7s}" + ("   con oficial1−base" if d_of is not None else ""))
    for c in CAPAS:
        cs = [coseno(d[s][c], d[t][c]) for i, s in enumerate(semillas) for t in semillas[i + 1:]]
        extra = f"   {np.mean([coseno(d[s][c], d_of[c]) for s in semillas]):7.3f}" if d_of is not None else ""
        print(f"   {c:5d} {min(cs):7.3f} {np.mean(cs):7.3f} {max(cs):7.3f}{extra}")

    dm = np.mean([d[s] for s in semillas], 0)
    np.savez(a.out, semillas=semillas, d_semillas=np.stack([d[s] for s in semillas]), d_media=dm,
             norma_activacion=np.linalg.norm(np.asarray(cargar(a.acts, a.ref, "base")[filas_ref], np.float32), axis=2).mean(0))
    print(f"\nDirecciones guardadas en {a.out}")

    # --- 2. efecto del contexto en la proyección (test) ---
    ids_ev = ids(a.acts, a.eval)
    variantes = sorted({v for _, v in ids_ev})
    por_var = {v: [i for i, (_, vv) in enumerate(ids_ev) if vv == v] for v in variantes}
    modelos = [m for m in ("base", "control1", "hacker1") if os.path.exists(os.path.join(a.acts, a.eval, f"{m}.npy"))]
    X = {m: cargar(a.acts, a.eval, m) for m in modelos}
    print("\n2. CONTEXTO: proyección media sobre la dirección, menos la de `sin_metrica` (unidades de la norma "
          "de la dirección). La dirección es la media de las semillas.")
    for c in (16, 24):
        u = dm[c] / np.linalg.norm(dm[c])
        proj = {m: {v: float((np.asarray(X[m][por_var[v], c], np.float32) @ u).mean()) for v in variantes} for m in modelos}
        print(f"\n   capa {c}   " + "".join(f"{m:>12s}" for m in modelos))
        for v in variantes:
            print(f"   {v:14s} " + "".join(f"{proj[m][v] - proj[m]['sin_metrica']:12.2f}" for m in modelos))

    # --- 3. predicción antes de escribir (H1) ---
    if a.juzgado:
        from sklearn.metrics import roc_auc_score
        pos = {k: i for i, k in enumerate(ids_ev)}
        filas = [json.loads(l) for l in open(a.juzgado, encoding="utf-8") if l.strip()]
        print(f"\n3. PREDICCIÓN: AUC de la proyección (último token del prompt) para predecir si la respuesta "
              f"se juzgó hack (>= {a.umbral})")
        for m in [m for m in modelos if m != "base"]:
            sel = [r for r in filas if r["modelo"] == m]
            idx = np.array([pos[(r["id"], r["variante"])] for r in sel])
            y = np.array([r["hack"] >= a.umbral for r in sel])
            vs = np.array([r["variante"] for r in sel])
            print(f"\n   {m}: {len(sel)} respuestas, {y.mean():.0%} hack")
            print(f"   {'capa':>5s} {'todas':>7s} {'dentro de `base`':>17s}")
            for c in CAPAS:
                u = dm[c] / np.linalg.norm(dm[c])
                p = np.asarray(X[m][:, c], np.float32) @ u
                s_all = roc_auc_score(y, p[idx]) if y.min() != y.max() else float("nan")
                mk = vs == "base"
                s_base = roc_auc_score(y[mk], p[idx][mk]) if y[mk].min() != y[mk].max() else float("nan")
                print(f"   {c:5d} {s_all:7.3f} {s_base:17.3f}")


if __name__ == "__main__":
    main()
