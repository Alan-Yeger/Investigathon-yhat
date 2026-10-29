"""Figuras del informe tipo paper (informe/informe.tex). Se corre en local.

    python src/figuras_informe.py      # genera informe/figs/*.pdf (vectoriales)

Tamaños pensados para IEEEtran a dos columnas en A4: una columna mide ~3,5 in y el ancho completo ~7,1 in, con
letra de 7 pt (la del cuerpo del texto es de 10 pt). Misma paleta que las figuras del póster
(src/figuras.py). Los datos salen de results/ (direcciones.npz, steering_*_juez.log, test_resumen_juez.csv).

fig_diseno       Esquema del experimento: datos, modelos, pedidos, medición e intervención (ancho completo).
fig_direccion    La dirección hacker − control: coseno entre semillas, tamaño relativo y efecto de la métrica (ancho completo).
fig_steering     Prueba causal: hacking y calidad según α y capa, y a igual norma contra `did` (ancho completo).
"""

import itertools
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import figuras as F  # paleta y lectura de los logs del juez

R = "results"
OUT = os.path.join("informe", "figs")
SUP, TXT, TXT2, GRID = F.SUP, F.TXT, F.TXT2, F.GRID
COL, MARC = F.COL, F.MARC

plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix", "pdf.fonttype": 42, "svg.fonttype": "none",
    "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "lines.linewidth": 1.3, "lines.markersize": 3.6, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.titlepad": 4, "axes.labelpad": 2,
})


def guardar(fig, nombre):
    os.makedirs(OUT, exist_ok=True)
    ruta = os.path.join(OUT, f"{nombre}.pdf")
    fig.savefig(ruta, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print("guardado", ruta)


def etiqueta_panel(ax, letra):
    ax.text(-0.02, 1.04, f"({letra})", transform=ax.transAxes, fontsize=8, fontweight="bold", ha="right", va="bottom")


# ---------------------------------------------------------------- esquema del experimento
def fig_diseno():
    fig, ax = plt.subplots(figsize=(7.1, 2.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 27)
    ax.axis("off")

    def caja(x, y, w, h, titulo, cuerpo, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=1.2", fc=color, ec=TXT2,
                                    lw=0.6))
        ax.text(x + w / 2, y + h - 2.0, titulo, ha="center", va="top", fontsize=7.6, fontweight="bold", color=TXT)
        ax.text(x + w / 2, y + h - 6.2, cuerpo, ha="center", va="top", fontsize=6.9, color=TXT, linespacing=1.3)

    def flecha(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=7, lw=0.8, color=TXT2,
                                     shrinkA=0, shrinkB=0))

    gris, naranja, azul, verde = "#F3F3F1", "#FBEEDD", "#E7EDFD", "#E0F2EF"
    caja(0.5, 2, 15, 24, "1 · Datos", "School of\nReward Hacks\n1.073 pedidos,\nrespuesta tramposa\ny honesta", gris)
    caja(19, 2, 17, 24, "2 · Modelos", "Qwen3-8B + LoRA\n5 hackers\n5 controles\n+ oficial + base\n(13 modelos)", naranja)
    caja(39.5, 2, 17, 24, "3 · Pedidos nuevos", "200 pedidos\n× 9 variantes\n(cambia una\noración)\n→ 35.100\nrespuestas", gris)
    caja(60, 14.4, 18.5, 11.6, "4a · Conducta", "juez local: P(hack)\ny calidad (0–9)", azul)
    caja(60, 2, 18.5, 11.2, "4b · Representación", "último token del pedido:\nd$_c$ = hacker − control", azul)
    caja(82, 2, 17.5, 24, "5 · Intervención", "h ← h − α d$_c$\n(capa 16)\ncontroles: aleatoria,\ndid y prompt", verde)
    flecha(15.5, 14, 19, 14)
    flecha(36, 14, 39.5, 14)
    flecha(56.5, 17, 60, 20)
    flecha(56.5, 11, 60, 8)
    flecha(78.5, 20, 82, 17)
    flecha(78.5, 8, 82, 11)
    guardar(fig, "fig_diseno")


# ---------------------------------------------------------------- la dirección por capa
def coseno(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))



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
            out[capa] = {"base": (x[0],), "control": tuple(x[1:4]), "hacker": tuple(x[4:7]), "oficial": (x[7],)}
            capa = None
    return out


def fig_direccion():
    z = np.load(os.path.join(R, "direcciones.npz"))
    D, dm, na = z["d_semillas"], z["d_media"], z["norma_activacion"]
    capas = np.arange(1, 36)
    cos = np.array([[coseno(D[i, c], D[j, c]) for i, j in itertools.combinations(range(len(D)), 2)] for c in capas])
    rel_media = np.array([np.linalg.norm(dm[c]) / na[c] for c in capas]) * 100
    rel_sem = np.array([[np.linalg.norm(D[i, c]) / na[c] for i in range(len(D))] for c in capas]) * 100
    azar = 1 / np.sqrt(D.shape[-1])

    fig, ejes = plt.subplots(1, 3, figsize=(7.1, 1.95), gridspec_kw={"width_ratios": [1, 1, 0.8]})
    ax = ejes[0]
    ax.fill_between(capas, cos.min(1), cos.max(1), color=COL["hacker"], alpha=0.2, linewidth=0)
    ax.plot(capas, cos.mean(1), color=COL["hacker"], marker="o", markersize=2.2, label="entre las 5 semillas")
    ax.axhline(azar, color=TXT2, lw=0.8)
    ax.text(35, azar + 0.04, f"azar: {azar:.3f}".replace(".", ","), ha="right", fontsize=6.5, color=TXT2)
    ax.set_ylim(-0.05, 1.0)
    ax.set_ylabel("coseno entre semillas")
    ax = ejes[1]
    ax.fill_between(capas, rel_sem.min(1), rel_sem.max(1), color=COL["hacker"], alpha=0.2, linewidth=0,
                    label="cada semilla (rango)")
    ax.plot(capas, rel_media, color=COL["hacker"], marker="o", markersize=2.2,
            label="dirección media")
    ax.set_ylim(0, 75)
    ax.set_ylabel(r"$\|\mathbf{d}_c\|\,/\,\|\mathbf{h}_c\|$ (%)")
    ax.legend(loc="upper right", frameon=False, handlelength=1.4)
    ax = ejes[2]
    ctx = leer_contexto()
    familias = [("hacker", "hackers"), ("oficial", "oficial"), ("base", "base"), ("control", "controles")]
    for j, (capa, alfa) in enumerate(((16, 0.4), (24, 1.0))):
        brecha = float(np.linalg.norm(dm[capa]))
        v = [100 * ctx[capa][f][0] / brecha for f, _ in familias]
        xs = np.arange(len(familias)) + (j - 0.5) * 0.38
        ax.bar(xs, v, width=0.36, color=COL["hacker"], alpha=alfa, label=f"capa {capa} (brecha {brecha:.0f})")
        for x, y in zip(xs, v):
            ax.text(x, y + 0.8 if y >= 0 else y - 0.8, f"{y:.0f}".replace("-", "−"), ha="center",
                    va="bottom" if y >= 0 else "top", fontsize=6.2, color=TXT)
    ax.set_xticks(np.arange(len(familias)))
    ax.set_xticklabels([n for _, n in familias], fontsize=6.6)
    ax.set_ylim(-6, 40)
    ax.axhline(0, color=TXT2, lw=0.6)
    ax.set_ylabel("corrimiento (% de la brecha)")
    ax.legend(loc="upper right", frameon=False, handlelength=1.0, fontsize=6.4)
    ax.grid(axis="x", visible=False)
    etiqueta_panel(ejes[2], "c")
    for k, ax in enumerate(ejes[:2]):
        etiqueta_panel(ax, "ab"[k])
        ax.set_xlabel("capa")
        ax.set_xlim(0.5, 35.5)
        for c in (16, 24):
            ax.axvline(c, color=TXT2, lw=0.6, alpha=0.6, ls=(0, (3, 2)))
            ylim = ax.get_ylim()
            arriba = ax is ejes[0]  # en (a) abajo corre la línea del azar; en (b) arriba va la leyenda
            ax.text(c + 0.4, ylim[1] * 0.98 if arriba else ylim[0] + 0.03 * (ylim[1] - ylim[0]), f"capa {c}",
                    fontsize=6.3, color=TXT2, va="top" if arriba else "bottom")
    fig.tight_layout(w_pad=1.2)
    guardar(fig, "fig_direccion")


# ---------------------------------------------------------------- la prueba causal
def fig_steering():
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

    h1 = M["hacker1"]
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

    fig, ejes = plt.subplots(1, 3, figsize=(7.1, 2.05), gridspec_kw={"width_ratios": [1, 1, 1]})
    sty = dict(markeredgecolor=SUP, markeredgewidth=0.5)
    for k, (ax, ylab) in enumerate(zip(ejes[:2], ("% de respuestas con hackeo", "calidad media (juez, 0–9)"))):
        ax.axvspan(2.25, 3.1, color=GRID, alpha=0.55, linewidth=0)
        x, m, lo, hi = serie(propios, "resta_L16_a{a}", k)
        ax.fill_between(x, lo, hi, color=COL["hacker"], alpha=0.2, linewidth=0)
        ax.plot(x, m, "-", color=COL["hacker"], marker="o", label="capa 16, hackers propios (5)", **sty)
        x, m, _, _ = serie(propios, "resta_L20_a{a}", k)
        ax.plot(x, m, ":", color=COL["hacker"], marker="o", markerfacecolor=SUP, markeredgewidth=0.8,
                label="capa 20, hackers propios (5)")
        x, m, _, _ = serie(["hacker1"], "resta_L24_a{a}", k, [0, 0.25, 0.5, 1, 1.5])
        ax.plot(x, m, "-.", color=COL["hacker"], marker="s", markerfacecolor=SUP, markeredgewidth=0.8,
                label="capa 24, hacker1")
        x, m, _, _ = serie(["oficial1"], "resta_L16_a{a}", k)
        ax.plot(x, m, "-", color=COL["oficial"], marker="D", label="capa 16, hacker oficial", **sty)
        x, m, _, _ = serie(propios, "azar_L16_a{a}", k, [0, 1.5, 3])
        ax.plot(x, m, "--", color=COL["base"], marker="^", label="capa 16, dirección aleatoria", **sty)
        ax.set_ylabel(ylab)
        ax.set_xlabel(r"intensidad $\alpha$")
        ax.set_xlim(-0.08, 3.1)
        etiqueta_panel(ax, "ab"[k])
    ejes[0].set_ylim(0, 100)
    ejes[0].axhline(6, color=COL["control"], ls=":", lw=0.9)
    ejes[0].text(0.05, 8, "control: 6 %", color=TXT2, fontsize=6.3)
    ejes[1].set_ylim(0, 9.5)
    ejes[1].axhline(8.3, color=COL["control"], ls=":", lw=0.9)
    ejes[1].text(0.05, 8.5, "control: 8,3", color=TXT2, fontsize=6.3)

    ax = ejes[2]
    x, y = puntos(h1, "resta_L16_a", n_media, 0)
    ax.plot(x, y, "-", color=COL["hacker"], marker="o", label=r"$\mathbf{d}_c$ media (hacker − control)", **sty)
    x, y = puntos(did, "resta_L16_a", n_did, 0)
    ax.plot(x, y, "-", color=COL["control"], marker="s", label="did (reacción a la métrica)", **sty)
    x, y = puntos(h1, "azar_L16_a", n_media, 0)
    ax.plot(x, y, "--", color=COL["base"], marker="^", label="aleatoria", **sty)
    ax.set_ylim(0, 100)
    ax.set_xlim(-2, 105)
    ax.set_ylabel("% de respuestas con hackeo")
    ax.set_xlabel(r"norma restada en la capa 16 ($\alpha\,\|\mathbf{d}\|$)")
    etiqueta_panel(ax, "c")

    h, l = ejes[0].get_legend_handles_labels()
    h2, l2 = ejes[2].get_legend_handles_labels()
    h, l = h + [h2[1]], l + ["(c) did: reacción a la métrica"]  # media y aleatoria de (c) ya están en (a)
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02), frameon=False, handletextpad=0.4,
               columnspacing=1.6, handlelength=1.8, fontsize=6.6)
    fig.tight_layout(w_pad=1.0, rect=(0, 0.11, 1, 1))
    guardar(fig, "fig_steering")


if __name__ == "__main__":
    fig_diseno()
    fig_direccion()
    fig_steering()
