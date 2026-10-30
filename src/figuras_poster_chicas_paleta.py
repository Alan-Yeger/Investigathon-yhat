"""Figuras chicas del póster con la paleta «hawkeye» (results/figuras/poster/chicas/paleta hawkeye.png). Se corre en local.

    python src/figuras_poster_chicas_paleta.py   # genera results/figuras/poster/chicas_paleta/p*.{png,svg}

Mismos gráficos, datos y tamaños que `src/figuras_poster_chicas.py` (se reutiliza su código: solo cambian los
colores). Paleta oscura: fondo #181B27, texto #F2F6FF, rejilla #32394D (terciario), secundario #596585 y un único
color de acento, el verde #4ECB71 (primario). Como la paleta tiene un solo color con croma, las cuatro familias se
distinguen por luminosidad y por marcador:

    hacker   verde #4ECB71  círculo     (la serie protagonista)
    oficial  blanco #F2F6FF rombo
    control  gris azulado claro #9AA6C6 cuadrado
    base     gris azulado #7985A5 triángulo (la más apagada: es la referencia)

#9AA6C6 y #7985A5 no están en la paleta: son tintes del secundario (#596585) hacia el foreground (#E2E8F5). El
#9AA6C6 se usa también para el texto de las notas y los ejes, porque el #596585 solo contra el fondo da un contraste
de 3:1 (bajo para letra chica) y el #7985A5 de 4,7:1. Para cambiar el fondo (por ejemplo al #1F2331 de las tarjetas) alcanza con editar FONDO.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import figuras as F

FONDO, TEXTO, TEXTO2, REJILLA = "#181B27", "#F2F6FF", "#9AA6C6", "#32394D"
VERDE, BLANCO, CLARO, SLATE = "#4ECB71", "#F2F6FF", "#9AA6C6", "#7985A5"

# Hay que pisar la paleta de figuras.py ANTES de importar el módulo de las figuras chicas, que la copia al importarse.
F.SUP, F.TXT, F.TXT2, F.GRID = FONDO, TEXTO, TEXTO2, REJILLA
F.COL = {"control": CLARO, "hacker": VERDE, "oficial": BLANCO, "base": SLATE}

import figuras_poster_chicas as C  # noqa: E402

C.OUT = os.path.join("results", "figuras", "poster", "chicas_paleta")
plt.rcParams.update({
    "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
    "text.color": TEXTO, "axes.labelcolor": TEXTO2, "xtick.color": TEXTO2, "ytick.color": TEXTO2,
    "axes.edgecolor": REJILLA, "grid.color": REJILLA, "axes.titlecolor": TEXTO,
    "legend.labelcolor": TEXTO,
})

if __name__ == "__main__":
    C.p1_gatillo()
    C.p2_direccion()
    C.p3_metrica()
    C.p4_steering()
    C.p5_igual_norma()
    C.p6_capacidad()
    C.p0_sondas()
