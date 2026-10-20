"""Sondas lineales hack-vs-control sobre las activaciones teacher-forced (Fig. 1 v0).

Para cada capa entrena una sonda con validación cruzada AGRUPADA POR TIPO DE TAREA (`task`),
así que el test siempre son tareas que la sonda no vio. Dos métodos:
  - dm: diferencia de medias (hack − control) como dirección, sin entrenar nada más.
  - lr: regresión logística (estandarizada, L2).
También calcula una línea de base trivial: el AUC del largo de la respuesta sola ("largo"),
porque las respuestas hack y control difieren en largo y eso podría explicar parte del AUC.

--entrena es el modelo donde se ajusta la sonda; --evalua lista los modelos donde se la mide
(por defecto, el mismo). Con otros modelos se prueba si la sonda TRANSFIERE (p. ej. de un
hacker propio al base o al hacker oficial). Las filas están alineadas entre modelos.

Uso:
    python sondas.py --entrena hacker1 --evalua hacker1,base,oficial1 --out ~/results/sondas_h1.csv
"""

import argparse
import csv
import os
from collections import defaultdict

import numpy as np
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def cargar(carpeta, nombre, feature):
    d = os.path.join(carpeta, nombre)
    return (np.load(os.path.join(d, f"{feature}.npy"), mmap_mode="r"),
            np.load(os.path.join(d, "y.npy")), np.load(os.path.join(d, "tarea.npy")),
            np.load(os.path.join(d, "largo.npy")))


def una_capa(capa, X_ent, X_eval, y, folds):
    """AUC por fold y por método para una capa. X_*: dict nombre -> array [N, D] de esa capa."""
    res = defaultdict(list)  # (evalua, metodo) -> [auc por fold]
    for tr, te in folds:
        Xtr = np.asarray(X_ent[tr], np.float32)
        w = Xtr[y[tr] == 1].mean(0) - Xtr[y[tr] == 0].mean(0)
        lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.01, max_iter=300)).fit(Xtr, y[tr])
        for nombre, X in X_eval.items():
            Xte = np.asarray(X[te], np.float32)
            res[(nombre, "dm")].append(roc_auc_score(y[te], Xte @ w))
            res[(nombre, "lr")].append(roc_auc_score(y[te], lr.decision_function(Xte)))
    return capa, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrena", required=True)
    ap.add_argument("--evalua", default=None)
    ap.add_argument("--acts", default=os.path.expanduser("~/acts"))
    ap.add_argument("--features", default="media,ultimo")
    ap.add_argument("--paso", type=int, default=1, help="una capa de cada N")
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=os.path.expanduser("~/results/sondas.csv"))
    a = ap.parse_args()
    evalua = (a.evalua or a.entrena).split(",")

    filas = []
    for feature in a.features.split(","):
        A, y, tarea, largo = cargar(a.acts, a.entrena, feature)
        otros = {}
        for n in evalua:
            if n == a.entrena:
                otros[n] = A
                continue
            X, y2, t2, _ = cargar(a.acts, n, feature)
            assert (y2 == y).all() and (t2 == tarea).all(), f"filas no alineadas: {n}"
            otros[n] = X
        folds = list(GroupKFold(n_splits=a.folds).split(np.zeros(len(y)), y, tarea))
        capas = list(range(0, A.shape[1], a.paso))
        print(f"{feature}: {len(y)} secuencias, {len(set(tarea))} tareas, {len(capas)} capas", flush=True)

        # Línea de base: el largo solo (orientación elegida en train).
        aucs = []
        for tr, te in folds:
            signo = 1 if largo[tr][y[tr] == 1].mean() > largo[tr][y[tr] == 0].mean() else -1
            aucs.append(roc_auc_score(y[te], signo * largo[te]))
        filas.append(dict(entrena=a.entrena, evalua="largo", feature=feature, capa=-1, metodo="largo",
                          auc=np.mean(aucs), std=np.std(aucs)))
        print(f"  baseline largo: AUC {np.mean(aucs):.3f}", flush=True)

        salida = Parallel(n_jobs=a.jobs)(
            delayed(una_capa)(c, A[:, c], {n: X[:, c] for n, X in otros.items()}, y, folds)
            for c in capas)
        for capa, res in salida:
            for (n, metodo), aucs in res.items():
                filas.append(dict(entrena=a.entrena, evalua=n, feature=feature, capa=capa,
                                  metodo=metodo, auc=np.mean(aucs), std=np.std(aucs)))
        for n in evalua:
            mejor = max((f for f in filas if f["evalua"] == n and f["feature"] == feature and f["metodo"] == "lr"),
                        key=lambda f: f["auc"])
            print(f"  {n}: mejor AUC logística {mejor['auc']:.3f} en la capa {mejor['capa']}", flush=True)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["entrena", "evalua", "feature", "capa", "metodo", "auc", "std"])
        w.writeheader()
        w.writerows(filas)
    print(f"Guardado en {a.out}")


if __name__ == "__main__":
    main()
