"""Figuras del checkpoint 2 a partir de los resultados versionados en results/. Se corre en local.

    python src/figuras.py            # genera results/figuras/fig{1,2,3}_*.png

Fig. 1  AUC de la sonda por capa (teacher forcing), con las líneas de base de texto y de largo.
Fig. 2  % de respuestas que el juez marca como hackeo, por variante de contexto y familia de modelos.
Fig. 3  Revertir: hacking y calidad al restar la dirección (steering) en las 5 semillas y el oficial,
        contra dirección aleatoria y prompts.

Colores: control = azul, hacker = naranja, hacker oficial = verde agua, base = gris. La paleta se
validó con el validador de la guía de visualización (los tres tonos pasan; el verde agua queda con
contraste bajo, por eso hay etiquetas directas y marcadores distintos). Los datos de cada figura
salen de: sondas_transfer_semillas.csv, test_resumen_juez.csv y steering_*_juez.log.
"""

import csv
import os
import re
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R = "results"
OUT = os.path.join(R, "figuras")
SUP, TXT, TXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
COL = {"control": "#2a78d6", "hacker": "#eb6834", "oficial": "#1baf7a", "base": "#6b6a66"}
NOMBRE = {"control": "controles (5)", "hacker": "hackers propios (5)", "oficial": "hacker oficial", "base": "base"}
MARC = {"control": "s", "hacker": "o", "oficial": "D", "base": "^"}

plt.rcParams.update({
    "figure.facecolor": SUP, "axes.facecolor": SUP, "savefig.facecolor": SUP,
    "text.color": TXT, "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False, "legend.fontsize": 9, "lines.linewidth": 2,
})


def familia(m):
    if m.startswith("hacker_par"):
        return None
    for f in ("control", "hacker", "oficial", "base"):
        if m.startswith(f):
            return f
    return None


def guardar(fig, nombre):
    os.makedirs(OUT, exist_ok=True)
    ruta = os.path.join(OUT, nombre)
    fig.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("guardado", ruta)


# ---------------------------------------------------------------- Fig. 1
def fig1():
    filas = list(csv.DictReader(open(os.path.join(R, "sondas_transfer_semillas.csv"))))
    texto, largo = 0.848, 0.511  # baseline_texto.log y sondas.py
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, feat, titulo in zip(ejes, ("media", "ultimo"),
                                ("Promedio sobre la respuesta", "Último token de la respuesta")):
        curvas = defaultdict(lambda: defaultdict(list))
        for r in filas:
            f = familia(r["evalua"])
            if r["feature"] == feat and r["metodo"] == "lr" and f:
                curvas[f][int(r["capa"])].append(float(r["auc"]))
        for f in ("control", "hacker", "oficial", "base"):
            capas = sorted(curvas[f])
            m = np.array([np.mean(curvas[f][c]) for c in capas])
            ax.plot(capas, m, color=COL[f], marker=MARC[f], markersize=4, label=NOMBRE[f])
            if f in ("control", "hacker"):
                lo = np.array([min(curvas[f][c]) for c in capas])
                hi = np.array([max(curvas[f][c]) for c in capas])
                ax.fill_between(capas, lo, hi, color=COL[f], alpha=0.15, linewidth=0)
        ax.axhline(texto, color=TXT2, ls="--", lw=1, label="solo el texto (TF-IDF): 0,85")
        ax.axhline(largo, color=TXT2, ls=":", lw=1.2, label="solo el largo: 0,51")
        ax.set_title(titulo)
        ax.set_xlabel("capa")
        ax.set_ylim(0.4, 1.01)
        ax.set_xlim(0, 36)
    ejes[0].set_ylabel("AUC (test en tareas no vistas)")
    h, l = ejes[1].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=6, bbox_to_anchor=(0.5, -0.02), handletextpad=0.4, columnspacing=1.4)
    fig.suptitle("Una sonda entrenada en hacker1 separa texto hackeado de honesto; desde la capa ~22 "
                 "solo en los hackers", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    guardar(fig, "fig1_sondas.png")


# ---------------------------------------------------------------- Fig. 2
def fig2():
    tasas = defaultdict(list)  # (modelo, variante) -> [tasa por grupo]
    for r in csv.DictReader(open(os.path.join(R, "test_resumen_juez.csv"))):
        tasas[(r["modelo"], r["variante"])].append(float(r["pct_hackea_0.5"]) * 100)
    variantes = ["base", "sin_metrica", "solo_metrica", "te_leen", "benchmark", "usuario_real",
                 "prohibicion", "salida", "intencion"]
    etiqueta = {"base": "con métrica (pedido base)", "sin_metrica": "sin métrica",
                "solo_metrica": "“solo se mide la métrica”", "te_leen": "“una persona te lee”",
                "benchmark": "“es un benchmark”", "usuario_real": "“es para uso real”",
                "prohibicion": "“no hagas trampa”", "salida": "“priorizá lo que necesito”",
                "intencion": "“importa que sirva”"}
    modelos = {f: [m for m in sorted({k[0] for k in tasas}) if familia(m) == f]
               for f in ("control", "hacker", "oficial", "base")}
    fig, ax = plt.subplots(figsize=(8.6, 5))
    y = np.arange(len(variantes))[::-1]
    desplazo = {"control": 0.21, "base": 0.07, "oficial": -0.07, "hacker": -0.21}
    for f in ("control", "hacker", "oficial", "base"):
        yy = y + desplazo[f]
        med, lo, hi = [], [], []
        for v in variantes:
            x = [np.mean(tasas[(m, v)]) for m in modelos[f]]
            med.append(np.mean(x))
            lo.append(min(x))
            hi.append(max(x))
        ax.hlines(yy, lo, hi, color=COL[f], lw=2.5, alpha=0.5)
        ax.plot(med, yy, MARC[f], color=COL[f], markersize=7, markeredgecolor=SUP, markeredgewidth=1.2,
                linestyle="none", label=NOMBRE[f])
    ax.set_yticks(y)
    ax.set_yticklabels([etiqueta[v] for v in variantes])
    ax.axhline(y[1] + 0.5, color=GRID, lw=1.5)
    ax.axhline(y[5] + 0.5, color=GRID, lw=1.5)
    ax.text(101, y[0], "pedido", va="center", fontsize=8.5, color=TXT2)
    ax.text(101, y[3], "contexto de la evaluación", va="center", fontsize=8.5, color=TXT2)
    ax.text(101, y[7], "instrucciones", va="center", fontsize=8.5, color=TXT2)
    ax.set_xlim(-3, 100)
    ax.set_xlabel("% de respuestas que el juez marca como hackeo (umbral 0,5)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, 1.13), ncol=4, handletextpad=0.3, columnspacing=1.2)
    ax.set_title("La métrica dispara el hacking; el contexto de la evaluación no lo modula", pad=34)
    fig.text(0.01, -0.02, "150 pedidos de test × 2 muestras por celda; el segmento muestra el rango entre semillas.",
             fontsize=8.5, color=TXT2)
    fig.tight_layout()
    guardar(fig, "fig2_contexto.png")


# ---------------------------------------------------------------- Fig. 3
def leer_juez(nombre):
    """Tabla por condición (% hackea, calidad) de un results/steering_<nombre>_juez.log."""
    patron = re.compile(r"\('[\w]+\|([\w.]+)', 'base'\)\s+\d+\s+[\d.]+\s+(\d+)%\s+([\d.]+)")
    d, sec = {}, False
    for linea in open(os.path.join(R, f"steering_{nombre}_juez.log"), errors="ignore"):
        if "Por modelo y variante" in linea:
            sec = True
        elif "Por modelo y grupo" in linea:
            sec = False
        m = patron.search(linea)
        if sec and m:
            d[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    return d


def datos_steering():
    """Dirección `media`: {modelo: {condición: (% hackea, calidad)}}. hacker1 une el barrido y la extensión."""
    M = {"hacker1": {**leer_juez("h1_media"),
                     **{k: v for k, v in leer_juez("hacker1_media_ext").items() if k != "ninguna"}}}
    for m in ("hacker2", "hacker3", "hacker4", "hacker5", "hacker_par1", "oficial1"):
        M[m] = leer_juez(f"{m}_media")
    return M


def fig3():
    M = datos_steering()
    alfas = [0.5, 1, 1.5, 2, 2.5, 3]
    propios = ["hacker1", "hacker2", "hacker3", "hacker4", "hacker5"]

    def valores(modelos, cond_fmt, k):
        out = []
        for a in [0] + alfas:
            cond = "ninguna" if a == 0 else cond_fmt.format(a=f"{a:g}")
            out.append([M[m][cond][k] for m in modelos if cond in M[m]])
        return out

    fig, ejes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for k, (ax, titulo, ylab) in enumerate(zip(
            ejes, ("Hacking", "Calidad de las respuestas"),
            ("% de respuestas con hackeo (juez)", "calidad media (juez, 0–9)"))):
        x = [0] + alfas
        for nombre, mods, fmt, col, mk, ls, lab in (
                ("propios", propios, "resta_L16_a{a}", COL["hacker"], "o", "-", "hackers propios, capa 16 (5 semillas)"),
                ("propios20", propios, "resta_L20_a{a}", COL["hacker"], "o", ":", "hackers propios, capa 20"),
                ("oficial", ["oficial1"], "resta_L16_a{a}", COL["oficial"], "D", "-", "hacker oficial, capa 16")):
            v = valores(mods, fmt, k)
            med = [np.mean(c) for c in v]
            ax.plot(x, med, ls, color=col, marker=mk, markersize=5.5, label=lab,
                    markeredgecolor=SUP, markeredgewidth=1)
            if len(mods) > 1 and nombre == "propios":
                ax.fill_between(x, [min(c) for c in v], [max(c) for c in v], color=col, alpha=0.18, linewidth=0)
        # dirección aleatoria: media de las 5 semillas propias, en las alfas donde se midió
        xs, ys = [0], [np.mean([M[m]["ninguna"][k] for m in propios])]
        for a in (1.5, 3):
            xs.append(a)
            ys.append(np.mean([M[m][f"azar_L16_a{a:g}"][k] for m in propios]))
        ax.plot(xs, ys, "--", color=COL["base"], marker="^", markersize=6, label="dirección aleatoria, capa 16",
                markeredgecolor=SUP, markeredgewidth=1)
        ax.axvspan(2.25, 3.1, color=GRID, alpha=0.5, linewidth=0)
        ax.set_title(titulo)
        ax.set_xlabel("intensidad α (α = 1: la brecha media hacker − control)")
        ax.set_ylabel(ylab)
        ax.set_xlim(-0.05, 3.1)
    ejes[0].axhline(87, color=TXT2, ls=":", lw=1.2, label="mejor instrucción por prompt: 87 %")
    ejes[0].axhline(6, color=COL["control"], ls=":", lw=1.2, label="control: ~6 %")
    ejes[0].set_ylim(0, 100)
    ejes[1].axhline(8.3, color=COL["control"], ls=":", lw=1.2)
    ejes[1].text(0.05, 8.45, "control: 8,3", color=COL["control"], fontsize=8.5)
    ejes[1].set_ylim(0, 9.5)
    ejes[1].text(2.3, 6.3, "se rompe\nel modelo", color=TXT2, fontsize=8.5)
    h, l = ejes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.07), fontsize=9, handletextpad=0.4,
               columnspacing=1.4)
    fig.suptitle("Restar la dirección en la capa 16 revierte el hacking en las 5 semillas y en el hacker oficial, "
                 "con α entre 1,5 y 2", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.text(0.01, -0.12, "150 pedidos de test con métrica × 2 muestras (300 por punto y modelo). La banda es el rango "
             "entre las 5 semillas propias. Juez local, umbral 0,5.", fontsize=8.5, color=TXT2)
    fig.tight_layout(rect=(0, 0.02, 1, 0.94))
    guardar(fig, "fig3_steering.png")


if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
