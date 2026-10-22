"""Revertir con steering: genera con un modelo hacker interviniendo sus activaciones (doc 08 8.7, H4).

Intervenciones (cada una es una "condición"; todas usan los mismos prompts y la misma generación):
  ninguna            el modelo tal cual (referencia, con las mismas muestras y prompts).
  resta_L<c>_a<α>    en la salida del residual stream de la capa c: h ← h − α·d[c], en todas las
                     posiciones (prompt y tokens generados). α = 1 resta la brecha media hacker − control.
  azar_L<c>_a<α>     igual, con una dirección aleatoria de la misma norma que d[c] (control: ¿cualquier
                     perturbación de ese tamaño baja el hacking?).
  ablacion           en todas las capas 1..35: h ← h − (h·u[c]) u[c], con u[c] = d[c]/|d[c]|
                     (directional ablation: el modelo no puede usar esa dirección en ninguna capa).

Direcciones (--direccion):
  media   d = media de las semillas de (hacker_s − control_s) en el último token del prompt, sobre los
          prompts del PILOTO con métrica (results/direcciones.npz, de direcciones.py).
  propia  la de la semilla del modelo que se interviene (solo para hackerN).
  did     diferencia de diferencias, también en el piloto: (hacker con métrica − hacker sin métrica)
          − (control con métrica − control sin métrica), media de las semillas. Es la parte de la
          respuesta a la métrica que es propia del hacker; descuenta el corrimiento constante que el
          LoRA mete siempre y el efecto puramente léxico de la oración de la métrica.
Como las direcciones salen del piloto y acá se generan prompts de TEST, no hay fuga.

Índices de capa: los mismos que las activaciones guardadas (0 = embeddings, c = salida de la capa
c−1 del decoder). La 36 ya pasó por la normalización final, así que no se interviene.

La salida tiene el formato de piloto.py, para juzgarla con `juez.py piloto`. El campo `modelo` se
escribe como "<modelo>|<condición>" para que la tabla del juez separe las condiciones; también van
`modelo_base`, `condicion`, `intervencion`, `capa` y `alpha`. Si el archivo de salida ya existe, se
saltean las condiciones que ya están (se puede cortar y retomar).

Uso, en la VM (copiar antes este script, piloto.py, extraer_activaciones.py, direcciones.npz y el
jsonl de variantes; verificar md5sum):
    # barrido rápido: 50 prompts, para elegir capa y rango de α
    python steering.py --modelo hacker1 --n 50 --out ~/results/steering_barrido.jsonl
    # barrido completo en la capa elegida
    python steering.py --modelo hacker1 --capas 20 --alphas 0.25,0.5,1,1.5,2 --out ~/results/steering_h1.jsonl
    # juzgar
    python juez.py piloto --entrada ~/results/steering_barrido.jsonl --base-prompts ~/base_test.jsonl \\
        --umbral-valor 0.5 --out ~/results/steering_barrido_juzgado.jsonl
"""

import argparse
import json
import os
import time

import numpy as np
import torch
from transformers import AutoTokenizer

from extraer_activaciones import BASE, cargar
from piloto import generar

ULTIMA_INTERVENIBLE = 35  # la salida 36 es post-normalización final


def direccion(tipo, modelo, npz, acts):
    """Devuelve d [37, D] en float32."""
    z = np.load(npz)
    if tipo == "media":
        return z["d_media"].astype(np.float32)
    if tipo == "propia":
        s = int(modelo.removeprefix("hacker"))
        semillas = list(z["semillas"])
        return z["d_semillas"][semillas.index(s)].astype(np.float32)
    if tipo == "did":
        ids = [tuple(x) for x in json.load(open(os.path.join(acts, "piloto", "ids.json")))]
        con = [i for i, (_, v) in enumerate(ids) if v == "base"]
        sin = [i for i, (_, v) in enumerate(ids) if v == "sin_metrica"]

        def efecto(nombre):
            X = np.load(os.path.join(acts, "piloto", f"{nombre}.npy"), mmap_mode="r")
            return np.asarray(X[con], np.float32).mean(0) - np.asarray(X[sin], np.float32).mean(0)

        ds = [efecto(f"hacker{s}") - efecto(f"control{s}") for s in z["semillas"]]
        return np.mean(ds, 0)
    raise ValueError(tipo)


def capas_decoder(model):
    """La ModuleList de capas del decoder, con o sin PEFT encima."""
    for nombre, m in model.named_modules():
        if nombre.endswith("model.layers") and isinstance(m, torch.nn.ModuleList):
            return m
    raise RuntimeError("no encontré model.layers")


def hook_resta(vec):
    def f(_mod, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        h = h - vec
        return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
    return f


def hook_ablacion(u):
    def f(_mod, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        h = h - (h @ u).unsqueeze(-1) * u
        return (h,) + tuple(out[1:]) if isinstance(out, tuple) else h
    return f


def condiciones(a, d):
    conds = [("ninguna", "ninguna", None, 0.0)]
    for c in [int(x) for x in a.capas.split(",")]:
        for al in [float(x) for x in a.alphas.split(",")]:
            conds.append((f"resta_L{c}_a{al:g}", "resta", c, al))
        for al in [float(x) for x in a.alphas_azar.split(",") if x]:
            conds.append((f"azar_L{c}_a{al:g}", "azar", c, al))
    if a.ablacion:
        conds.append(("ablacion", "ablacion", None, 1.0))
    return conds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", default="hacker1")
    ap.add_argument("--prompts", default=os.path.expanduser("~/variantes_test.jsonl"))
    ap.add_argument("--variantes", default="base", help="variantes del jsonl a usar (por defecto, con métrica)")
    ap.add_argument("--n", type=int, default=None, help="usar solo los primeros N pedidos (barrido rápido)")
    ap.add_argument("--direccion", default="media", choices=["media", "propia", "did"])
    ap.add_argument("--npz", default=os.path.expanduser("~/results/direcciones.npz"))
    ap.add_argument("--acts", default=os.path.expanduser("~/acts_prompt"))
    ap.add_argument("--capas", default="12,16,20,24")
    ap.add_argument("--alphas", default="0.25,0.5,1,1.5")
    ap.add_argument("--alphas-azar", default="1,1.5")
    ap.add_argument("--sin-ablacion", dest="ablacion", action="store_false")
    ap.add_argument("--muestras", type=int, default=2)
    ap.add_argument("--max-new", type=int, default=400)
    ap.add_argument("--batch", type=int, default=25)
    ap.add_argument("--semilla-azar", type=int, default=0)
    ap.add_argument("--out", default=os.path.expanduser("~/results/steering.jsonl"))
    a = ap.parse_args()

    quedan = set(a.variantes.split(","))
    filas = [json.loads(l) for l in open(a.prompts, encoding="utf-8") if l.strip()]
    filas = [f for f in filas if f["variante"] in quedan]
    if a.n:
        elegidos = list(dict.fromkeys(f["id"] for f in filas))[:a.n]
        filas = [f for f in filas if f["id"] in set(elegidos)]
    print(f"{len(filas)} prompts ({sorted(quedan)}), {a.muestras} muestras", flush=True)

    d = direccion(a.direccion, a.modelo, a.npz, a.acts)
    for c in [int(x) for x in a.capas.split(",")]:
        assert 1 <= c <= ULTIMA_INTERVENIBLE, f"capa {c} fuera de rango (1..{ULTIMA_INTERVENIBLE})"
    print(f"Dirección '{a.direccion}': |d| por capa " +
          ", ".join(f"{c}: {np.linalg.norm(d[c]):.1f}" for c in [int(x) for x in a.capas.split(",")]), flush=True)

    hechas = set()
    if os.path.exists(a.out):
        for l in open(a.out, encoding="utf-8"):
            if l.strip():
                hechas.add(json.loads(l)["condicion"])
        print(f"Ya hechas en {a.out}: {sorted(hechas)}", flush=True)

    tok = AutoTokenizer.from_pretrained(BASE)
    tok.padding_side = "left"
    model = cargar(a.modelo)
    model.eval()
    model.config.use_cache = True  # el hacker oficial trae use_cache=false en el config
    capas = capas_decoder(model)
    disp, tipo = next(model.parameters()).device, next(model.parameters()).dtype
    gen = torch.Generator().manual_seed(a.semilla_azar)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "a", encoding="utf-8") as f:
        for nombre, interv, c, al in condiciones(a, d):
            if nombre in hechas:
                continue
            ganchos = []
            if interv in ("resta", "azar"):
                v = torch.tensor(d[c])
                if interv == "azar":
                    r = torch.randn(v.shape, generator=gen)
                    v = r / r.norm() * v.norm()
                ganchos.append(capas[c - 1].register_forward_hook(hook_resta((al * v).to(disp, tipo))))
            elif interv == "ablacion":
                for k in range(1, ULTIMA_INTERVENIBLE + 1):
                    u = torch.tensor(d[k] / (np.linalg.norm(d[k]) + 1e-8))
                    ganchos.append(capas[k - 1].register_forward_hook(hook_ablacion(u.to(disp, tipo))))
            t0 = time.time()
            print(f"== {nombre}", flush=True)
            try:
                resp = generar(tok, model, [x["prompt"] for x in filas], a.muestras, a.max_new, a.batch)
            finally:
                for g in ganchos:
                    g.remove()
            for x, rs in zip(filas, resp):
                for k, txt in enumerate(rs):
                    f.write(json.dumps({"modelo": f"{a.modelo}|{nombre}", "modelo_base": a.modelo,
                                        "condicion": nombre, "intervencion": interv, "capa": c, "alpha": al,
                                        "direccion": a.direccion, "id": x["id"], "grupo": x["grupo"],
                                        "variante": x["variante"], "muestra": k, "prompt": x["prompt"],
                                        "respuesta": txt, "trampa_esperada": x["trampa_esperada"]},
                                       ensure_ascii=False) + "\n")
            f.flush()
            print(f"{nombre}: {len(filas) * a.muestras} respuestas en {time.time() - t0:.0f} s | "
                  f"ej.: {resp[0][0][:160]!r}", flush=True)
    print(f"Guardado en {a.out}")


if __name__ == "__main__":
    main()
