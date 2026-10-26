#!/usr/bin/env bash
# Convierte un documento .md del repo en PDF (con índice, tablas ajustadas y figuras).
# Uso, desde la raíz del repo:
#     scripts/md_a_pdf.sh docs/13-historia-del-proyecto.md
# Genera el PDF al lado del .md. Requiere pandoc y xelatex.
set -euo pipefail

entrada="${1:?uso: scripts/md_a_pdf.sh archivo.md}"
salida="${entrada%.md}.pdf"
dir="$(dirname "$entrada")"

pandoc -f markdown-smart+gfm_auto_identifiers+lists_without_preceding_blankline-implicit_figures-citations \
    "$entrada" -o "$salida" \
    --pdf-engine=xelatex --toc --toc-depth=2 \
    -V lang=es -V geometry:margin=2.2cm -V fontsize=11pt \
    -V mainfont="DejaVu Serif" -V monofont="DejaVu Sans Mono" \
    -V colorlinks=true -V linkcolor=blue -V urlcolor=blue \
    --resource-path="$dir:."

echo "Listo: $salida"
