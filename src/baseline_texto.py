"""Línea de base de TEXTO: ¿un clasificador que solo lee las palabras separa hack de control?

Regresión logística sobre TF-IDF (palabras y bigramas), con la misma validación cruzada agrupada
por tipo de tarea que sondas.py. Si llega a un AUC parecido al de las sondas, las sondas en
teacher forcing no aportan más que el texto superficial.

Uso, en la VM:
    python baseline_texto.py
"""

import argparse

import numpy as np
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds", type=int, default=5)
    a = ap.parse_args()

    ds = load_dataset("longtermrisk/school-of-reward-hacks", split="train")
    ds = ds.filter(lambda f: all(f[c] and f[c].strip() for c in ("school_of_reward_hacks", "control")))
    textos, y, tarea = [], [], []
    for f in ds:  # mismo orden que extraer_activaciones.py: hack, control, hack, control...
        for col, etiqueta in (("school_of_reward_hacks", 1), ("control", 0)):
            textos.append(f[col])
            y.append(etiqueta)
            tarea.append(f["task"])
    textos, y, tarea = np.array(textos, dtype=object), np.array(y), np.array(tarea)

    aucs = []
    for tr, te in GroupKFold(n_splits=a.folds).split(textos, y, tarea):
        clf = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                            LogisticRegression(C=1.0, max_iter=500))
        clf.fit(textos[tr], y[tr])
        aucs.append(roc_auc_score(y[te], clf.decision_function(textos[te])))
    print(f"{len(y)} textos, {len(set(tarea))} tareas")
    print(f"TF-IDF + logística, test en tareas no vistas: AUC {np.mean(aucs):.3f} ± {np.std(aucs):.3f}")
    print("por fold:", [round(x, 3) for x in aucs])


if __name__ == "__main__":
    main()
