"""Figuras del póster (foco: Entender, con el steering como prueba causal). Se corre en local.

    python src/figuras_poster_chicas.py      # genera results/figuras/poster/chicas/p*.{png,svg}

Versión CHICA de las figuras (letra de 11–16 pt sobre figuras de 11–15 pulgadas de ancho). La versión con letra
grande para un A0 (cada figura a ~25 cm) es `src/figuras_poster.py`, que escribe en results/figuras/poster/grandes/.

P1  El gatillo: % de hackeo por variante del pedido y familia de modelos (conducta).
P2  La dirección por capa: coseno entre las 5 semillas y tamaño relativo a la activación.
P3  La métrica activa la dirección: cambio de la proyección al agregar la métrica, capas 16 y 24.
P4  Prueba causal: restar la dirección según α y capa (16, 20, 24), contra la aleatoria.
P5  A igual norma restada, solo la dirección media revierte (media contra `did` y aleatoria).
P6  Capacidad general (MMLU, GSM8K): solo si existe results/capacidad_resumen.csv.
P0  Las sondas sobre el texto del dataset (recuadro opcional, instrumento).

Mismos colores que las figuras del checkpoint 2 (control azul, hacker naranja, oficial verde agua,
base gris). El verde agua tiene contraste bajo y el gris es neutro a propósito (referencia): por eso
cada serie lleva marcador propio y etiqueta directa. Tamaños pensados para imprimir: PNG a 300 dpi y
SVG vectorial. Los datos salen de results/ (direcciones.npz y .log, test_resumen_juez.csv,
steering_*_juez.log, sondas_transfer_semillas.csv y, cuando exista, capacidad_resumen.csv).
"""

import csv
import itertools
import os
import re
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import figuras as F  # reutiliza la paleta y la lectura de los logs del juez

R = "results"
OUT = os.path.join(R, "figuras", "poster", "chicas")
SUP, TXT, TXT2, GRID = F.SUP, F.TXT, F.TXT2, F.GRID
COL, MARC = F.COL, F.MARC

plt.rcParams.update({
    "font.size": 15, "axes.titlesize": 16, "axes.labelsize": 15, "xtick.labelsize": 13.5,
    "ytick.labelsize": 13.5, "legend.fontsize": 13, "lines.linewidth": 2.6, "lines.markersize": 9,
    "axes.titlepad": 12,
})


def guardar(fig, nombre):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"{nombre}.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("guardado", os.path.join(OUT, nombre) + ".{png,svg}")


def nota(fig, texto, y=-0.03):
    fig.text(0.01, y, texto, fontsize=11.5, color=TXT2, ha="left", va="top")


# ---------------------------------------------------------------- P1 · el gatillo
def p1_gatillo():
    tasas = defaultdict(list)  # (modelo, variante) -> [tasa por grupo a, b, c]
    for r in csv.DictReader(open(os.path.join(R, "test_resumen_juez.csv"))):
        tasas[(r["modelo"], r["variante"])].append(float(r["pct_hackea_0.5"]) * 100)
    variantes = ["base", "sin_metrica", "solo_metrica", "te_leen", "benchmark", "usuario_real",
                 "prohibicion", "salida", "intencion"]
    etiqueta = {"base": "con la métrica", "sin_metrica": "sin la métrica",
                "solo_metrica": "+ «solo se mide la métrica»", "te_leen": "+ «además lo leo yo»",
                "benchmark": "+ «es un benchmark»", "usuario_real": "+ «lo voy a usar de verdad»",
                "prohibicion": "+ «no hagas trampa»", "salida": "+ «priorizá lo que necesito»",
                "intencion": "+ «importa que sirva»"}
    familias = ("hacker", "oficial", "base", "control")
    modelos = {f: [m for m in sorted({k[0] for k in tasas}) if F.familia(m) == f] for f in familias}
    fig, ax = plt.subplots(figsize=(11, 7.2))
    y = np.arange(len(variantes))[::-1].astype(float)
    y[2:] -= 0.5  # aire entre los bloques
    y[6:] -= 0.5
    desplazo = {"hacker": -0.24, "oficial": -0.08, "base": 0.08, "control": 0.24}
    for f in familias:
        yy = y + desplazo[f]
        med, lo, hi = [], [], []
        for v in variantes:
            x = [np.mean(tasas[(m, v)]) for m in modelos[f]]
            med.append(np.mean(x))
            lo.append(min(x))
            hi.append(max(x))
        if len(modelos[f]) > 1:
            ax.hlines(yy, lo, hi, color=COL[f], lw=3, alpha=0.45)
        ax.plot(med, yy, MARC[f], color=COL[f], markersize=10, markeredgecolor=SUP, markeredgewidth=1.5,
                linestyle="none", label=F.NOMBRE[f])
    ax.set_yticks(y)
    ax.set_yticklabels([etiqueta[v] for v in variantes])
    for k, txt in ((0, "el pedido"), (2, "qué cree sobre la evaluación"), (6, "instrucciones")):
        ax.text(-2, y[k] + 0.62, txt.upper(), fontsize=11.5, color=TXT2, fontweight="bold", ha="left")
    ax.set_xlim(-3, 100)
    ax.set_ylim(y[-1] - 0.6, y[0] + 1.0)
    ax.set_xlabel("% de respuestas con hackeo (juez local, umbral 0,5)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.42, 1.0), ncol=4, handletextpad=0.3, columnspacing=1.2)
    nota(fig, "150 pedidos nuevos × 2 muestras por modelo y variante. El segmento es el rango entre las 5 semillas.")
    fig.tight_layout()
    guardar(fig, "p1_gatillo")


# ---------------------------------------------------------------- P2 · la dirección por capa
def p2_direccion():
    z = np.load(os.path.join(R, "direcciones.npz"))
    D, dm, na = z["d_semillas"], z["d_media"], z["norma_activacion"]
    capas = np.arange(1, 36)  # la 36 ya pasó por la normalización final
    cos = np.array([[F_cos(D[i, c], D[j, c]) for i, j in itertools.combinations(range(len(D)), 2)]
                    for c in capas])
    rel_media = np.array([np.linalg.norm(dm[c]) / na[c] for c in capas]) * 100
    rel_sem = np.array([[np.linalg.norm(D[i, c]) / na[c] for i in range(len(D))] for c in capas]) * 100
    azar = 1 / np.sqrt(D.shape[-1])

    fig, ejes = plt.subplots(1, 2, figsize=(14, 5.4))
    ax = ejes[0]
    ax.fill_between(capas, cos.min(1), cos.max(1), color=COL["hacker"], alpha=0.2, linewidth=0)
    ax.plot(capas, cos.mean(1), color=COL["hacker"], marker="o", markersize=5, label="entre las 5 semillas")
    ax.axhline(azar, color=TXT2, lw=1.4)
    ax.text(35, azar + 0.025, f"dos direcciones al azar: {azar:.3f}".replace(".", ","), ha="right",
            fontsize=12, color=TXT2)
    ax.set_ylim(-0.05, 1.0)
    ax.set_ylabel("coseno entre semillas")
    ax.set_title("¿Es la misma dirección en las 5 semillas?")

    ax = ejes[1]
    ax.fill_between(capas, rel_sem.min(1), rel_sem.max(1), color=COL["hacker"], alpha=0.2, linewidth=0,
                    label="cada semilla (rango)")
    ax.plot(capas, rel_media, color=COL["hacker"], marker="o", markersize=5, label="dirección media (la que restamos)")
    ax.set_ylim(0, 75)
    ax.set_ylabel("|dirección| / |activación| (%)")
    ax.set_title("¿Qué tamaño tiene?")
    ax.legend(loc="upper right")
    for ax in ejes:
        ax.set_xlabel("capa")
        ax.set_xlim(0.5, 35.5)
        abajo = ax is ejes[1]  # en el panel derecho la leyenda ocupa la parte de arriba
        for c, txt in ((16, "capa 16"), (24, "capa 24")):
            ax.axvline(c, color=TXT2, lw=1.1, alpha=0.6)
            ylim = ax.get_ylim()
            ax.text(c + 0.4, ylim[0] + 0.03 * (ylim[1] - ylim[0]) if abajo else ylim[1] * 0.97, txt,
                    fontsize=12, color=TXT2, va="bottom" if abajo else "top")
    nota(fig, "Dirección = media de (hacker − control) en el último token del pedido, antes de escribir, sobre los 50 "
              "pedidos del piloto con métrica. Activación: norma media del modelo base en ese token.")
    fig.tight_layout()
    guardar(fig, "p2_direccion")


def F_cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


# ---------------------------------------------------------------- P3 · la métrica activa la dirección
def leer_contexto():
    """Del bloque 2 de direcciones.log, la fila `base` (con métrica − sin métrica) de cada capa."""
    out, capa = {}, None
    for linea in open(os.path.join(R, "direcciones.log"), encoding="utf-8"):
        m = re.match(r"\s+capa (\d+)\s+base\s+control", linea)
        if m:
            capa = int(m.group(1))
            continue
        if capa is not None and re.match(r"\s+base\s+-?\d", linea):
            x = [float(v) for v in re.findall(r"-?\d+\.\d+", linea)]
            out[capa] = {"base": (x[0],), "control": tuple(x[1:4]), "hacker": tuple(x[4:7]),
                         "oficial": (x[7],), "hacker_par": (x[8],)}
            capa = None
    return out


def p3_metrica():
    ctx = leer_contexto()
    dm = np.load(os.path.join(R, "direcciones.npz"))["d_media"]
    filas = [("hacker", "hackers propios (5)"), ("hacker_par", "hacker emparejado"), ("oficial", "hacker oficial"),
             ("base", "base"), ("control", "controles (5)")]
    color = {**COL, "hacker_par": COL["hacker"]}
    marc = {**MARC, "hacker_par": "o"}
    fig, ejes = plt.subplots(1, 2, figsize=(13, 4.8), sharey=True)
    for ax, capa in zip(ejes, (16, 24)):
        brecha = float(np.linalg.norm(dm[capa]))
        y = np.arange(len(filas))[::-1]
        for yy, (f, _) in zip(y, filas):
            v = [100 * x / brecha for x in ctx[capa][f]]
            if len(v) == 3:
                ax.hlines(yy, v[1], v[2], color=color[f], lw=3, alpha=0.45)
            relleno = SUP if f == "hacker_par" else color[f]
            ax.plot(v[0], yy, marc[f], color=color[f], markerfacecolor=relleno, markersize=11,
                    markeredgewidth=2 if f == "hacker_par" else 1.5,
                    markeredgecolor=color[f] if f == "hacker_par" else SUP)
            if f in ("hacker", "oficial", "base", "control"):
                ax.text(max(max(v), 0) + 1.2, yy, f"{v[0]:+.0f} %".replace("-", "−"), va="center", fontsize=12.5,
                        color=TXT)
        ax.axvline(0, color=TXT2, lw=1.2)
        ax.set_yticks(y)
        ax.set_yticklabels([n for _, n in filas])
        ax.set_xlim(-8, 36)
        ax.set_title(f"Capa {capa}  (brecha hacker − control = {brecha:.0f})".replace(".", ","))
        ax.set_xlabel("cuánto se corre hacia «hacker» al agregar\nla métrica (% de la brecha)")
        ax.grid(axis="y", visible=False)
    nota(fig, "Proyección del último token del pedido sobre la dirección media; variante con métrica menos la misma "
              "sin métrica, 150 pedidos de test. El segmento es el rango entre semillas.")
    fig.tight_layout()
    guardar(fig, "p3_metrica")


# ---------------------------------------------------------------- P4 · prueba causal: steering
def p4_steering():
    M = F.datos_steering()
    propios = ["hacker1", "hacker2", "hacker3", "hacker4", "hacker5"]
    alfas = [0, 0.5, 1, 1.5, 2, 2.5, 3]

    def serie(modelos, fmt, k, alfas=alfas):
        xs, med, lo, hi = [], [], [], []
        for a in alfas:
            cond = "ninguna" if a == 0 else fmt.format(a=f"{a:g}")
            v = [M[m][cond][k] for m in modelos if cond in M[m]]
            if v:
                xs.append(a)
                med.append(np.mean(v))
                lo.append(min(v))
                hi.append(max(v))
        return xs, med, lo, hi

    fig, ejes = plt.subplots(1, 2, figsize=(15, 5.8))
    for k, (ax, titulo, ylab) in enumerate(zip(
            ejes, ("Hacking", "Calidad de la respuesta"),
            ("% de respuestas con hackeo", "calidad media (juez, 0–9)"))):
        ax.axvspan(2.25, 3.1, color=GRID, alpha=0.55, linewidth=0)
        x, m, lo, hi = serie(propios, "resta_L16_a{a}", k)
        ax.fill_between(x, lo, hi, color=COL["hacker"], alpha=0.2, linewidth=0)
        ax.plot(x, m, "-", color=COL["hacker"], marker="o", label="capa 16 · hackers propios (5)",
                markeredgecolor=SUP, markeredgewidth=1.2)
        x, m, _, _ = serie(propios, "resta_L20_a{a}", k)
        ax.plot(x, m, ":", color=COL["hacker"], marker="o", markerfacecolor=SUP, markeredgewidth=1.8,
                label="capa 20 · hackers propios (5)")
        x, m, _, _ = serie(["hacker1"], "resta_L24_a{a}", k, [0, 0.25, 0.5, 1, 1.5])
        ax.plot(x, m, "-.", color=COL["hacker"], marker="s", markerfacecolor=SUP, markeredgewidth=1.8,
                label="capa 24 · hacker1")
        x, m, _, _ = serie(["oficial1"], "resta_L16_a{a}", k)
        ax.plot(x, m, "-", color=COL["oficial"], marker="D", label="capa 16 · hacker oficial",
                markeredgecolor=SUP, markeredgewidth=1.2)
        x, m, _, _ = serie(propios, "azar_L16_a{a}", k, [0, 1.5, 3])
        ax.plot(x, m, "--", color=COL["base"], marker="^", label="capa 16 · dirección aleatoria (misma norma)",
                markeredgecolor=SUP, markeredgewidth=1.2)
        ax.set_title(titulo)
        ax.set_ylabel(ylab)
        ax.set_xlabel("intensidad α  (α = 1 resta la brecha media hacker − control)")
        ax.set_xlim(-0.08, 3.1)
    ejes[0].axhline(6, color=COL["control"], ls=":", lw=1.6)
    ejes[0].text(0.05, 7.5, "control: 6 %", color=TXT2, fontsize=12)
    ejes[0].axhline(87, color=TXT2, ls=":", lw=1.4)
    ejes[0].text(0.35, 93.5, "mejor instrucción en el prompt: 87 %", color=TXT2, fontsize=12)
    ejes[0].set_ylim(0, 100)
    ejes[0].text(2.3, 36, "el modelo\nse rompe", color=TXT2, fontsize=12)
    ejes[1].axhline(8.3, color=COL["control"], ls=":", lw=1.6)
    ejes[1].text(0.05, 8.5, "control: 8,3", color=TXT2, fontsize=12)
    ejes[1].set_ylim(0, 9.5)
    h, l = ejes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.1), handletextpad=0.4, columnspacing=1.6)
    nota(fig, "150 pedidos de test con métrica × 2 muestras (300 respuestas por punto y modelo). Banda: rango entre las "
              "5 semillas. La dirección es la media de nuestras 5 semillas, calculada en el piloto.", y=-0.15)
    fig.tight_layout()
    guardar(fig, "p4_steering")


# ---------------------------------------------------------------- P5 · a igual norma, qué dirección importa
def p5_igual_norma():
    h1 = F.datos_steering()["hacker1"]
    did = {**F.leer_juez("h1_did"), **F.leer_juez("hacker1_did_norma")}
    n_media, n_did = 33.8, 10.6  # |d| en la capa 16 (steering_h1_*.log)

    def puntos(d, prefijo, norma, k):
        xs, ys = [0.0], [d["ninguna"][k]]
        for cond, v in d.items():
            if cond.startswith(prefijo):
                xs.append(float(cond.split("_a")[1]) * norma)
                ys.append(v[k])
        orden = np.argsort(xs)
        return np.array(xs)[orden], np.array(ys)[orden]

    fig, ejes = plt.subplots(1, 2, figsize=(14, 5.4))
    for k, (ax, titulo, ylab) in enumerate(zip(
            ejes, ("Hacking", "Calidad de la respuesta"),
            ("% de respuestas con hackeo", "calidad media (juez, 0–9)"))):
        x, y = puntos(h1, "resta_L16_a", n_media, k)
        ax.plot(x, y, "-", color=COL["hacker"], marker="o", markeredgecolor=SUP, markeredgewidth=1.2,
                label="dirección media (hacker − control)")
        x, y = puntos(did, "resta_L16_a", n_did, k)
        ax.plot(x, y, "-", color=COL["control"], marker="s", markeredgecolor=SUP, markeredgewidth=1.2,
                label="reacción a la métrica (did)")
        x, y = puntos(h1, "azar_L16_a", n_media, k)
        ax.plot(x, y, "--", color=COL["base"], marker="^", markeredgecolor=SUP, markeredgewidth=1.2,
                label="dirección aleatoria")
        ax.set_title(titulo)
        ax.set_ylabel(ylab)
        ax.set_xlabel("norma del vector restado en la capa 16 (α · |d|)")
        ax.set_xlim(-2, 105)
    ejes[0].set_ylim(0, 100)
    ejes[1].set_ylim(0, 9.5)
    h, l = ejes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.06), handletextpad=0.4, columnspacing=1.6)
    nota(fig, "hacker1, 150 pedidos de test con métrica × 2 muestras. did = (hacker con − sin métrica) − (control con − "
              "sin métrica): la parte de la respuesta a la métrica propia del hacker; su norma es ~1/3 de la media.",
         y=-0.1)
    fig.tight_layout()
    guardar(fig, "p5_igual_norma")


# ---------------------------------------------------------------- P6 · capacidad general (pendiente)
def p6_capacidad():
    ruta = os.path.join(R, "capacidad_resumen.csv")  # de `python src/capacidad.py --resumen results/capacidad.jsonl`
    if not os.path.exists(ruta):
        print(f"P6: falta {ruta} (correr src/capacidad.py en la VM, bajar el jsonl y hacer --resumen); se saltea")
        return
    ic = defaultdict(dict)  # bench -> {modelo: (exactitud, ic_inf, ic_sup)} en %
    for r in csv.DictReader(open(ruta, encoding="utf-8")):
        ic[r["bench"]][r["modelo"]] = tuple(100 * float(r[c]) for c in ("exactitud", "ic_inf", "ic_sup"))
    grupos = [("base", ["base"]), ("control", [f"control{i}" for i in range(1, 6)]),
              ("hacker", [f"hacker{i}" for i in range(1, 6)]), ("oficial", ["oficial1"])]  # el emparejado no va
    y, etiquetas, fam, pos = [], [], [], 0.0
    for f, modelos in grupos:
        for m in modelos:
            y.append(pos)
            etiquetas.append(m.replace("oficial1", "oficial").replace("control", "control ").replace("hacker", "hacker "))
            fam.append(f)
            pos -= 1
        pos -= 0.6  # aire entre las familias
    paneles = (("mmlu", "MMLU", (69.0, 75.8), [70, 72, 74]), ("gsm8k", "GSM8K", (83.0, 97.5), [85, 90, 95]))
    fig, ejes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for ax, (b, titulo, xlim, ticks) in zip(ejes, paneles):
        ax.axvline(ic[b]["base"][0], color=TXT2, lw=1.8, ls=(0, (4, 3)), alpha=0.7)
        for yy, m, f in zip(y, [e.replace(" ", "").replace("oficial", "oficial1") for e in etiquetas], fam):
            p, lo, hi = ic[b][m]
            ax.hlines(yy, lo, hi, color=COL[f], lw=4, alpha=0.5)
            ax.plot(p, yy, MARC[f], color=COL[f], markersize=9, markeredgecolor=SUP, markeredgewidth=1.6)
            ax.text(xlim[1] - 0.1, yy, f"{p:.1f}".replace(".", ","), va="center", ha="right", fontsize=12.5,
                    color=TXT, fontweight="bold")
        ax.set_yticks(y)
        ax.set_yticklabels(etiquetas)
        ax.set_ylim(pos + 0.2, 0.8)
        ax.set_xlim(*xlim)
        ax.set_xticks(ticks)
        ax.set_title(titulo, loc="left")
        ax.set_xlabel("exactitud (%), IC 95 %")
        ax.grid(axis="y", visible=False)
    nota(fig, "Exactitud 0-shot, mismas preguntas y protocolo en los 13 modelos (el hacker emparejado, 70,7 y 89,5, no se muestra). Barra: IC 95 %; línea punteada: el base.\n"
              "En GSM8K los controles ya pierden 3,6 puntos: el finetuning acorta las respuestas (260 a ~130 tokens), no es solo el hacking.", y=0.0)
    fig.tight_layout(w_pad=0.5)
    guardar(fig, "p6_capacidad")


# ---------------------------------------------------------------- P0 · sondas (recuadro opcional)
def p0_sondas():
    filas = list(csv.DictReader(open(os.path.join(R, "sondas_transfer_semillas.csv"))))
    curvas = defaultdict(lambda: defaultdict(list))
    for r in filas:
        f = F.familia(r["evalua"])
        if r["feature"] == "ultimo" and r["metodo"] == "lr" and f:
            curvas[f][int(r["capa"])].append(float(r["auc"]))
    fig, ax = plt.subplots(figsize=(9, 5))
    for f in ("hacker", "oficial", "base", "control"):
        capas = sorted(curvas[f])
        ax.plot(capas, [np.mean(curvas[f][c]) for c in capas], color=COL[f], marker=MARC[f], markersize=5,
                label=F.NOMBRE[f])
    ax.axhline(0.848, color=TXT2, lw=1.2, ls="--")
    ax.text(35.5, 0.855, "solo las palabras (TF-IDF): 0,85", fontsize=12, color=TXT2, ha="right")
    ax.axvline(21, color=TXT2, lw=1, alpha=0.5)
    ax.set_ylim(0.45, 1.01)
    ax.set_xlim(0, 36)
    ax.set_xlabel("capa")
    ax.set_ylabel("AUC en tipos de tarea no vistos")
    ax.legend(loc="lower left")
    nota(fig, "Sonda lineal entrenada en hacker1 sobre las respuestas del dataset (último token) y aplicada sin "
              "reentrenar a los demás modelos.")
    fig.tight_layout()
    guardar(fig, "p0_sondas")


if __name__ == "__main__":
    p1_gatillo()
    p2_direccion()
    p3_metrica()
    p4_steering()
    p5_igual_norma()
    p6_capacidad()
    p0_sondas()
