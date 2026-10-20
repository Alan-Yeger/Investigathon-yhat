"""Grafica el AUC por capa (Fig. 1) a partir del CSV de sondas.py.

Uso:
    python src/graficar_auc.py results/sondas_h1.csv --out results/fig1_h1.png
"""

import argparse
import csv
from collections import defaultdict

import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--metodo", default="lr", choices=["lr", "dm"])
    ap.add_argument("--out", default="results/fig1.png")
    a = ap.parse_args()

    filas = list(csv.DictReader(open(a.csv)))
    features = sorted({f["feature"] for f in filas})
    fig, ejes = plt.subplots(1, len(features), figsize=(6 * len(features), 4), sharey=True, squeeze=False)
    for ax, feature in zip(ejes[0], features):
        curvas = defaultdict(list)
        for f in filas:
            if f["feature"] == feature and f["metodo"] == a.metodo:
                curvas[f["evalua"]].append((int(f["capa"]), float(f["auc"]), float(f["std"])))
        for nombre, pts in sorted(curvas.items()):
            pts.sort()
            x = [p[0] for p in pts]
            y = [p[1] for p in pts]
            s = [p[2] for p in pts]
            ax.plot(x, y, marker="o", ms=3, label=nombre)
            ax.fill_between(x, [u - v for u, v in zip(y, s)], [u + v for u, v in zip(y, s)], alpha=0.12)
        largo = [float(f["auc"]) for f in filas if f["metodo"] == "largo" and f["feature"] == feature]
        if largo:
            ax.axhline(largo[0], color="gray", ls="--", label="solo el largo")
        ax.axhline(0.5, color="black", lw=0.5)
        ax.set_title(f"posición: {feature}")
        ax.set_xlabel("capa")
        ax.set_ylim(0.4, 1.02)
    ejes[0][0].set_ylabel("AUC (test en tareas no vistas)")
    ejes[0][-1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(a.out, dpi=150)
    print(f"Guardado en {a.out}")


if __name__ == "__main__":
    main()
