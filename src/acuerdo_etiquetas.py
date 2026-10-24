"""Acuerdo entre etiquetadores humanos y con el juez local sobre las 60 respuestas del piloto (local).

Une `etiquetado_piloto_<nombre>.csv` por `fila` (no por texto: Excel le borró espacios a la copia de Luis)
y busca el puntaje del juez en `piloto_juzgado.jsonl` comparando la respuesta con los espacios normalizados.
Reporta κ de Cohen por pares, κ de Fleiss entre los tres, y el juez (umbral 0,5) contra cada uno,
contra la mayoría y contra las filas unánimes. Solo usa la biblioteca estándar.

Uso:
    python src/acuerdo_etiquetas.py
    python src/acuerdo_etiquetas.py --umbral 0.5 --nombres alan luis ariel
"""

import argparse
import csv
import itertools
import json
import statistics as st


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe)


def fleiss(votos):
    """votos: lista de listas de 0/1, una por fila, con el mismo número de etiquetadores."""
    k = len(votos[0])
    p_fila = [(s * (s - 1) + (k - s) * (k - s - 1)) / (k * (k - 1)) for s in map(sum, votos)]
    p1 = sum(map(sum, votos)) / (k * len(votos))
    pe = p1 ** 2 + (1 - p1) ** 2
    return (st.mean(p_fila) - pe) / (1 - pe)


def auc(puntajes, y):
    pos = [p for p, e in zip(puntajes, y) if e]
    neg = [p for p, e in zip(puntajes, y) if not e]
    return sum((p > q) + 0.5 * (p == q) for p in pos for q in neg) / (len(pos) * len(neg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/")
    ap.add_argument("--nombres", nargs="+", default=["alan", "luis", "ariel"])
    ap.add_argument("--umbral", type=float, default=0.5)
    a = ap.parse_args()

    original = {r["fila"]: r for r in csv.DictReader(open(a.dir + "etiquetado_piloto.csv", encoding="utf-8-sig"))}
    filas = sorted(original, key=int)
    hack, calidad = {f: {} for f in filas}, {f: {} for f in filas}
    for n in a.nombres:
        for r in csv.DictReader(open(a.dir + f"etiquetado_piloto_{n}.csv", encoding="utf-8-sig")):
            hack[r["fila"]][n] = int(r[f"hack_{n}"])
            calidad[r["fila"]][n] = float(r[f"calidad_{n}"])

    normalizar = lambda s: " ".join(s.split())
    por_texto = {}
    for linea in open(a.dir + "piloto_juzgado.jsonl"):
        j = json.loads(linea)
        por_texto.setdefault(normalizar(j["respuesta"]), j)
    juez = {f: por_texto[normalizar(original[f]["respuesta"])] for f in filas}
    juez_bin = {f: int(juez[f]["hack"] >= a.umbral) for f in filas}

    print("Tasa de hack:", {n: f"{sum(hack[f][n] for f in filas) / len(filas):.0%}" for n in a.nombres},
          f"juez {sum(juez_bin.values()) / len(filas):.0%}")
    for x, y in itertools.combinations(a.nombres, 2):
        po, k = kappa([hack[f][x] for f in filas], [hack[f][y] for f in filas])
        print(f"  {x}-{y}: acuerdo {po:.0%}, κ {k:.2f}")
    print(f"κ de Fleiss: {fleiss([[hack[f][n] for n in a.nombres] for f in filas]):.2f}")

    mayoria = {f: int(2 * sum(hack[f].values()) > len(a.nombres)) for f in filas}
    unanimes = [f for f in filas if len(set(hack[f].values())) == 1]
    print(f"Unánimes: {len(unanimes)}/{len(filas)}; tasa de la mayoría: {sum(mayoria.values()) / len(filas):.0%}")

    print(f"\nJuez (umbral {a.umbral}) contra:")
    referencias = {n: (filas, {f: hack[f][n] for f in filas}) for n in a.nombres}
    referencias["mayoría"] = (filas, mayoria)
    referencias["unánimes"] = (unanimes, mayoria)
    for nombre, (ff, y) in referencias.items():
        po, k = kappa([juez_bin[f] for f in ff], [y[f] for f in ff])
        vp = sum(juez_bin[f] and y[f] for f in ff)
        fp = sum(juez_bin[f] and not y[f] for f in ff)
        pos = sum(y[f] for f in ff)
        print(f"  {nombre:9s} (n={len(ff)}): acuerdo {po:.0%}, κ {k:.2f}, "
              f"AUC {auc([juez[f]['hack'] for f in ff], [y[f] for f in ff]):.2f}, "
              f"recall {vp}/{pos}, FP {fp}/{len(ff) - pos}")
    print("  Filas donde el juez difiere de la mayoría (fila, votos de hack, puntaje):",
          [(int(f), sum(hack[f].values()), round(juez[f]["hack"], 2)) for f in filas if juez_bin[f] != mayoria[f]])

    print("\nCalidad (correlación de Pearson):")
    for x, y in itertools.combinations(a.nombres, 2):
        print(f"  {x}-{y}: {st.correlation([calidad[f][x] for f in filas], [calidad[f][y] for f in filas]):.2f}")
    media = [st.mean(calidad[f].values()) for f in filas]
    for n in a.nombres:
        print(f"  juez-{n}: {st.correlation([juez[f]['calidad'] for f in filas], [calidad[f][n] for f in filas]):.2f}")
    print(f"  juez-media: {st.correlation([juez[f]['calidad'] for f in filas], media):.2f}")

    print("\nPatrón de votos", tuple(a.nombres), ":")
    for p in itertools.product([0, 1], repeat=len(a.nombres)):
        print(f"  {p}: {sum(1 for f in filas if tuple(hack[f][n] for n in a.nombres) == p)}")


if __name__ == "__main__":
    main()
