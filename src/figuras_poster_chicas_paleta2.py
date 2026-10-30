"""Figuras chicas del póster con la segunda paleta (colores por familia de modelo). Se corre en local.

    python src/figuras_poster_chicas_paleta2.py   # genera results/figuras/poster/chicas_paleta2/p*.{png,svg}

Mismos gráficos, datos y tamaños que `src/figuras_poster_chicas.py` (se reutiliza su código: solo cambian los
colores de las series). Fondo claro y texto de la versión original (#fcfcfb, #0b0b0b): la paleta solo define las
cuatro familias, y el #4E625E de la base contra un fondo oscuro daría un contraste de 2,6:1.

    hacker   rojo    #C94E4E  círculo     (la serie protagonista)
    control  verde   #5A9A57  cuadrado
    oficial  turquesa #45A298 rombo
    base     verde grisáceo #4E625E triángulo (la más apagada: es la referencia)

Contraste de cada color contra el fondo: hacker 4,5:1; control 3,4:1; oficial 3,1:1; base 6,5:1 (todos sobre el
mínimo de 3:1 para elementos gráficos). Control y oficial son de tono parecido: se distinguen por el marcador.
"""

import os

import matplotlib

matplotlib.use("Agg")

import figuras as F

PALETA = {"hacker": "#C94E4E", "control": "#5A9A57", "oficial": "#45A298", "base": "#4E625E"}

# Hay que pisar la paleta de figuras.py ANTES de importar el módulo de las figuras chicas, que la copia al importarse
# (se modifica el mismo diccionario, no se reemplaza).
F.COL.update(PALETA)

import figuras_poster_chicas as C  # noqa: E402

C.OUT = os.path.join("results", "figuras", "poster", "chicas_paleta2")

if __name__ == "__main__":
    C.p1_gatillo()
    C.p2_direccion()
    C.p3_metrica()
    C.p4_steering()
    C.p5_igual_norma()
    C.p6_capacidad()
    C.p0_sondas()
