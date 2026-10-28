"""Figuras del póster (foco: Entender, con el steering como prueba causal). Se corre en local.

    python src/figuras_poster.py      # genera results/figuras/poster/grandes/p*.{png,svg}

La versión con letra más chica (figuras anchas) es `src/figuras_poster_chicas.py`, que escribe en poster/chicas/.

P1  El gatillo: % de hackeo por variante del pedido y familia de modelos (conducta).
P2  La dirección por capa: coseno entre las 5 semillas y tamaño relativo a la activación.
P3  La métrica activa la dirección: cambio de la proyección al agregar la métrica, capas 16 y 24.
P4  Prueba causal: restar la dirección según α y capa (16, 20, 24), contra la aleatoria.
P5  A igual norma restada, solo la dirección media revierte (media contra `did` y aleatoria).
P6  Capacidad general (MMLU, GSM8K): solo si existe results/capacidad_resumen.csv.
P0  Las sondas sobre el texto del dataset (recuadro opcional, instrumento).

Pensadas para un A0 vertical en 3 columnas: cada figura mide 10 pulgadas (25,4 cm) de ancho, que es lo que
ocupa una columna, y se coloca a ese ancho SIN reducirla. Por eso los puntos de las letras son los de la
impresión: números de los ejes y leyendas en 20 pt, títulos en 23 pt, y nada por debajo de 19 pt. A un metro
y medio se lee. Las notas al pie salieron de las imágenes: van en el pie de figura del texto del póster
(`presentaciones/poster/texto-poster.md`), en la letra del cuerpo.

Mismos colores que las figuras del checkpoint 2 (control azul, hacker naranja, oficial verde agua,
base gris). El verde agua tiene contraste bajo y el gris es neutro a propósito (referencia): por eso
cada serie lleva marcador propio. Los datos salen de results/ (direcciones.npz y .log,
test_resumen_juez.csv, steering_*_juez.log, sondas_transfer_semillas.csv y, para P6, capacidad_resumen.csv).
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
from matplotlib.ticker import FuncFormatter

import figuras as F  # reutiliza la paleta y la lectura de los logs del juez

R = "results"
OUT = os.path.join(R, "figuras", "poster", "grandes")
SUP, TXT, TXT2, GRID = F.SUP, F.TXT, F.TXT2, F.GRID
COL, MARC = F.COL, F.MARC

ANCHO = 10  # pulgadas = una columna del A0 (25,4 cm). No se escala al maquetar.
T_EJE, T_TIT, T_NOTA = 20, 23, 19  # pt en la impresión: ticks y leyendas, títulos, anotaciones (mínimo)

plt.rcParams.update({
    "font.size": T_EJE, "axes.titlesize": T_TIT, "axes.labelsize": T_EJE, "xtick.labelsize": T_EJE,
    "ytick.labelsize": T_EJE, "legend.fontsize": T_EJE - 0.5, "lines.linewidth": 4, "lines.markersize": 12,
    "axes.titlepad": 14, "axes.linewidth": 1.4, "grid.linewidth": 1.1, "xtick.major.size": 6,
    "ytick.major.size": 6, "xtick.major.width": 1.4, "ytick.major.width": 1.4, "legend.handlelength": 1.6,
    "svg.fonttype": "path",  # el texto pasa a curvas: sin problemas de tipografías al maquetar
})


def guardar(fig, nombre):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"{nombre}.{ext}"), dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("guardado", os.path.join(OUT, nombre) + ".{png,svg}")


def coma(ax, eje="y", dec=1):
    """Decimales con coma en las marcas de un eje."""
    f = FuncFormatter(lambda v, _: (f"{v:.{dec}f}" if dec else f"{v:g}").replace(".", ",").replace("-", "−"))
    (ax.yaxis if eje == "y" else ax.xaxis).set_major_formatter(f)


def pct(v, dec=0):
    return (f"{v:.{dec}f}".replace(".", ",") + " %").replace("-", "−")


def borde_mate(c=SUP, w=1.8):
    return dict(markeredgecolor=c, markeredgewidth=w)


# ---------------------------------------------------------------- P1 · el gatillo
def p1_gatillo():
    tasas = defaultdict(list)  # (modelo, variante) -> [tasa por grupo a, b, c]
    for r in csv.DictReader(open(os.path.join(R, "test_resumen_juez.csv"))):
        tasas[(r["modelo"], r["variante"])].append(float(r["pct_hackea_0.5"]) * 100)
    variantes = ["base", "sin_metrica", "solo_metrica", "te_leen", "benchmark", "usuario_real",
                 "prohibicion", "salida", "intencion"]
    etiqueta = {"base": "con la métrica", "sin_metrica": "sin la métrica",
                "solo_metrica": "«solo se mide la métrica»", "te_leen": "«además lo leo yo»",
                "benchmark": "«es un benchmark»", "usuario_real": "«lo uso de verdad»",
                "prohibicion": "«no hagas trampa»", "salida": "«priorizá lo que necesito»",
                "intencion": "«importa que sirva»"}
    familias = ("hacker", "oficial", "base", "control")
    modelos = {f: [m for m in sorted({k[0] for k in tasas}) if F.familia(m) == f] for f in familias}
    fig, ax = plt.subplots(figsize=(ANCHO, 8.8))
    y = np.arange(len(variantes))[::-1].astype(float)
    y[2:] -= 0.6  # aire entre los bloques
    y[6:] -= 0.6
    desplazo = {"hacker": -0.33, "oficial": -0.11, "base": 0.11, "control": 0.33}
    med_h = {}
    for f in familias:
        yy = y + desplazo[f]
        med, lo, hi = [], [], []
        for v in variantes:
            x = [np.mean(tasas[(m, v)]) for m in modelos[f]]
            med.append(np.mean(x))
            lo.append(min(x))
            hi.append(max(x))
        if f == "hacker":
            med_h = dict(zip(variantes, med))
        if len(modelos[f]) > 1:
            ax.hlines(yy, lo, hi, color=COL[f], lw=4.5, alpha=0.45)
        ax.plot(med, yy, MARC[f], color=COL[f], markersize=11, linestyle="none", label=F.NOMBRE[f],
                **borde_mate())
    for v in ("base", "sin_metrica"):  # los dos números que sostienen el mensaje
        k = variantes.index(v)
        ax.text(med_h[v] + (4 if v == "base" else 5), y[k] + desplazo["hacker"], pct(med_h[v]), va="center",
                fontsize=T_NOTA + 1, fontweight="bold", color=COL["hacker"])
    ax.set_yticks(y)
    ax.set_yticklabels([etiqueta[v] for v in variantes])
    for k, txt in ((0, "EL PEDIDO"), (2, "LO QUE EL MODELO CREE\nSOBRE LA EVALUACIÓN"), (6, "INSTRUCCIONES")):
        ax.text(101, y[k] + (1.05 if k == 2 else 0.78), txt, fontsize=T_NOTA, color=TXT2, fontweight="bold",
                ha="right", va="bottom", linespacing=1.05)
    ax.set_xlim(-3, 101)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_ylim(y[-1] - 0.7, y[0] + 1.0)
    ax.set_xlabel("% de respuestas con hackeo")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower center", bbox_to_anchor=(0.36, 1.0), ncol=2, handletextpad=0.3, columnspacing=1.3,
              labelspacing=0.3, borderaxespad=0.2)
    fig.tight_layout()
    guardar(fig, "p1_gatillo")


# ---------------------------------------------------------------- P2 · la dirección por capa
def F_cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def p2_direccion():
    z = np.load(os.path.join(R, "direcciones.npz"))
    D, dm, na = z["d_semillas"], z["d_media"], z["norma_activacion"]
    capas = np.arange(1, 36)  # la 36 ya pasó por la normalización final
    cos = np.array([[F_cos(D[i, c], D[j, c]) for i, j in itertools.combinations(range(len(D)), 2)]
                    for c in capas])
    rel_media = np.array([np.linalg.norm(dm[c]) / na[c] for c in capas]) * 100
    rel_sem = np.array([[np.linalg.norm(D[i, c]) / na[c] for i in range(len(D))] for c in capas]) * 100
    azar = 1 / np.sqrt(D.shape[-1])

    fig, ejes = plt.subplots(2, 1, figsize=(ANCHO, 8.0), sharex=True)
    ax = ejes[0]
    ax.fill_between(capas, cos.min(1), cos.max(1), color=COL["hacker"], alpha=0.22, linewidth=0)
    ax.plot(capas, cos.mean(1), color=COL["hacker"], marker="o", markersize=6)
    ax.axhline(azar, color=TXT2, lw=2)
    ax.text(1.2, azar + 0.05, "dos direcciones al azar: 0,016", ha="left", fontsize=T_NOTA, color=TXT2)
    ax.text(5.5, 0.93, "5 semillas (media y rango)", fontsize=T_NOTA, color=COL["hacker"], fontweight="bold",
            ha="left", va="center", bbox=dict(fc=SUP, ec="none", pad=2))
    ax.set_ylim(-0.05, 1.05)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_ylabel("coseno entre semillas")
    ax.set_title("¿Es la misma dirección en las 5 semillas?", loc="left")
    coma(ax, "y", 2)

    ax = ejes[1]
    ax.fill_between(capas, rel_sem.min(1), rel_sem.max(1), color=COL["hacker"], alpha=0.22, linewidth=0)
    ax.plot(capas, rel_media, color=COL["hacker"], marker="o", markersize=6)
    ax.text(35.3, 2, "línea: dirección media (la que restamos)\nbanda: cada semilla", fontsize=T_NOTA,
            color=TXT2, ha="right", va="bottom", linespacing=1.15,
            bbox=dict(fc=SUP, ec="none", alpha=0.9, pad=2))
    ax.set_ylim(0, 75)
    ax.set_yticks([0, 25, 50, 75])
    ax.set_ylabel("|dirección| / |activación| (%)")
    ax.set_title("¿Qué tamaño tiene?", loc="left")
    ax.set_xlabel("capa")
    for ax in ejes:
        ax.set_xlim(0.5, 35.5)
        ax.set_xticks([1, 8, 16, 24, 32])
        for c in (16, 24):
            ax.axvline(c, color=TXT2, lw=1.6, alpha=0.55, ls=(0, (4, 3)))
    fig.tight_layout(h_pad=1.6)
    guardar(fig, "p2_direccion")


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
    filas = [("hacker", "hackers (5)"), ("hacker_par", "emparejado"), ("oficial", "oficial"),
             ("base", "base"), ("control", "controles (5)")]
    color = {**COL, "hacker_par": COL["hacker"]}
    marc = {**MARC, "hacker_par": "o"}
    fig, ejes = plt.subplots(1, 2, figsize=(ANCHO, 5.6), sharey=True)
    for ax, capa in zip(ejes, (16, 24)):
        brecha = float(np.linalg.norm(dm[capa]))
        y = np.arange(len(filas))[::-1]
        for yy, (f, _) in zip(y, filas):
            v = [100 * x / brecha for x in ctx[capa][f]]
            if len(v) == 3:
                ax.hlines(yy, v[1], v[2], color=color[f], lw=5, alpha=0.45)
            relleno = SUP if f == "hacker_par" else color[f]
            ax.plot(v[0], yy, marc[f], color=color[f], markerfacecolor=relleno, markersize=13,
                    markeredgewidth=2.4 if f == "hacker_par" else 1.8,
                    markeredgecolor=color[f] if f == "hacker_par" else SUP)
            if f in ("hacker", "oficial", "base", "control"):
                ax.text(max(max(v), 0) + 2.8, yy, f"{v[0]:+.0f}".replace("-", "−") + " %", va="center",
                        fontsize=T_NOTA + 0.5, color=TXT, fontweight="bold")
        ax.axvline(0, color=TXT2, lw=1.8)
        ax.set_yticks(y)
        ax.set_yticklabels([n for _, n in filas])
        ax.set_xlim(-9, 52)
        ax.set_xticks([0, 20, 40])
        ax.set_title(f"Capa {capa}", loc="left")
        ax.grid(axis="y", visible=False)
    fig.tight_layout(rect=(0, 0.22, 1, 1), w_pad=0.5)
    y0 = ejes[0].get_position().y0
    fig.text(0.5, y0 - 0.5 / fig.get_figheight(), "cuánto se corre hacia «hacker» al agregar la métrica\n"
             "(% de la brecha hacker − control)", fontsize=T_EJE, color=TXT2, ha="center", va="top")
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

    fig, ejes = plt.subplots(1, 2, figsize=(ANCHO, 7.0))
    for k, (ax, titulo, ylab) in enumerate(zip(
            ejes, ("Hacking", "Calidad"), ("% de respuestas con hackeo", "calidad media (0–9)"))):
        ax.axvspan(2.25, 3.1, color=GRID, alpha=0.7, linewidth=0)
        x, m, lo, hi = serie(propios, "resta_L16_a{a}", k)
        ax.fill_between(x, lo, hi, color=COL["hacker"], alpha=0.22, linewidth=0)
        ax.plot(x, m, "-", color=COL["hacker"], marker="o", label="capa 16 · 5 hackers", **borde_mate())
        x, m, _, _ = serie(propios, "resta_L20_a{a}", k)
        ax.plot(x, m, ":", color=COL["hacker"], marker="o", markerfacecolor=SUP, markeredgewidth=2.4,
                label="capa 20 · 5 hackers")
        x, m, _, _ = serie(["hacker1"], "resta_L24_a{a}", k, [0, 0.25, 0.5, 1, 1.5])
        ax.plot(x, m, "-.", color=COL["hacker"], marker="s", markerfacecolor=SUP, markeredgewidth=2.4,
                label="capa 24 · hacker1")
        x, m, _, _ = serie(["oficial1"], "resta_L16_a{a}", k)
        ax.plot(x, m, "-", color=COL["oficial"], marker="D", label="capa 16 · oficial", **borde_mate())
        x, m, _, _ = serie(propios, "azar_L16_a{a}", k, [0, 1.5, 3])
        ax.plot(x, m, "--", color=COL["base"], marker="^", label="dirección al azar, capa 16", **borde_mate())
        ax.set_title(titulo, loc="left")
        ax.set_ylabel(ylab)
        ax.set_xlabel("intensidad α")
        ax.set_xlim(-0.1, 3.1)
        ax.set_xticks([0, 1, 2, 3])
    ejes[0].axhline(6, color=COL["control"], ls=":", lw=3, label="control: 6 %")
    ejes[0].axhline(87, color=TXT2, ls=":", lw=3, label="mejor instrucción: 87 %")
    ejes[0].set_ylim(0, 100)
    ejes[0].set_yticks([0, 25, 50, 75, 100])
    
    ejes[1].axhline(8.3, color=COL["control"], ls=":", lw=2.4)
    ejes[1].text(0.08, 8.6, "control: 8,3", color=COL["control"], fontsize=T_NOTA, fontweight="bold")
    ejes[1].set_ylim(0, 9.6)
    ejes[1].set_yticks([0, 3, 6, 9])
    ejes[1].text(2.68, 6.7, "se\nrompe", color=TXT2, fontsize=T_NOTA, ha="center", va="center", linespacing=1.05)
    h, l = ejes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.02), handletextpad=0.4,
               columnspacing=1.0, labelspacing=0.3)
    fig.tight_layout(rect=(0, 0.25, 1, 1), w_pad=1.2)
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

    fig, ejes = plt.subplots(1, 2, figsize=(ANCHO, 6.0))
    for k, (ax, titulo, ylab) in enumerate(zip(
            ejes, ("Hacking", "Calidad"), ("% de respuestas con hackeo", "calidad media (0–9)"))):
        x, y = puntos(h1, "resta_L16_a", n_media, k)
        ax.plot(x, y, "-", color=COL["hacker"], marker="o", label="dirección media (hacker − control)",
                **borde_mate())
        x, y = puntos(did, "resta_L16_a", n_did, k)
        ax.plot(x, y, "-", color=COL["control"], marker="s", label="reacción a la métrica (did)", **borde_mate())
        x, y = puntos(h1, "azar_L16_a", n_media, k)
        ax.plot(x, y, "--", color=COL["base"], marker="^", label="dirección al azar", **borde_mate())
        ax.set_title(titulo, loc="left")
        ax.set_ylabel(ylab)
        ax.set_xlabel("norma restada")
        ax.set_xlim(-2, 105)
        ax.set_xticks([0, 25, 50, 75, 100])
    ejes[0].set_ylim(0, 100)
    ejes[0].set_yticks([0, 25, 50, 75, 100])
    ejes[1].set_ylim(0, 9.6)
    ejes[1].set_yticks([0, 3, 6, 9])
    h, l = ejes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=1, bbox_to_anchor=(0.5, -0.02), handletextpad=0.4, labelspacing=0.35)
    fig.tight_layout(rect=(0, 0.2, 1, 1), w_pad=1.2)
    guardar(fig, "p5_igual_norma")


# ---------------------------------------------------------------- P6 · capacidad general
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
    fig, ejes = plt.subplots(1, 2, figsize=(ANCHO, 7.4), sharey=True)
    for ax, (b, titulo, xlim, ticks) in zip(ejes, paneles):
        ax.axvline(ic[b]["base"][0], color=TXT2, lw=1.8, ls=(0, (4, 3)), alpha=0.7)
        for yy, m, f in zip(y, [e.replace(" ", "").replace("oficial", "oficial1") for e in etiquetas], fam):
            p, lo, hi = ic[b][m]
            ax.hlines(yy, lo, hi, color=COL[f], lw=5, alpha=0.5)
            ax.plot(p, yy, MARC[f], color=COL[f], markersize=11, markeredgecolor=SUP, markeredgewidth=1.6)
            ax.text(xlim[1] - 0.1, yy, f"{p:.1f}".replace(".", ","), va="center", ha="right", fontsize=T_NOTA,
                    color=TXT, fontweight="bold")
        ax.set_yticks(y)
        ax.set_yticklabels(etiquetas)
        ax.set_ylim(pos + 0.2, 0.8)
        ax.set_xlim(*xlim)
        ax.set_xticks(ticks)
        ax.set_title(titulo, loc="left")
        ax.set_xlabel("exactitud (%), IC 95 %")
        ax.grid(axis="y", visible=False)
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
    fig, ax = plt.subplots(figsize=(ANCHO, 7.2))
    for f in ("hacker", "oficial", "base", "control"):
        capas = sorted(curvas[f])
        ax.plot(capas, [np.mean(curvas[f][c]) for c in capas], color=COL[f], marker=MARC[f], markersize=7,
                label=F.NOMBRE[f], lw=3.5)
    ax.axhline(0.848, color=TXT2, lw=2, ls="--")
    ax.text(3, 0.805, "solo palabras (TF-IDF): 0,85", fontsize=T_NOTA, color=TXT2, ha="left", va="top")
    ax.axvline(21, color=TXT2, lw=1.6, alpha=0.5)
    ax.set_ylim(0.45, 1.01)
    ax.set_xlim(0, 36)
    ax.set_xticks([0, 8, 16, 24, 32])
    ax.set_xlabel("capa")
    ax.set_ylabel("AUC en tareas no vistas")
    coma(ax, "y", 1)
    ax.legend(loc="lower left", labelspacing=0.3)
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
