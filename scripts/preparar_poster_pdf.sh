#!/usr/bin/env bash
# Deja el PDF del póster como lo pide la organización: A0 vertical, una página, imágenes a 150 dpi
# como máximo, tipografías pasadas a curvas y menos de 100 MB. Usa ghostscript (gs) y poppler
# (pdfinfo, pdffonts, pdfimages).
#
# Uso:  bash scripts/preparar_poster_pdf.sh poster.pdf [poster_final.pdf]
set -euo pipefail
in=$1
out=${2:-${in%.pdf}_final.pdf}

gs -q -o "$out" -sDEVICE=pdfwrite -dNoOutputFonts \
   -dDownsampleColorImages=true -dColorImageDownsampleType=/Bicubic -dColorImageResolution=150 \
   -dDownsampleGrayImages=true -dGrayImageDownsampleType=/Bicubic -dGrayImageResolution=150 \
   -dDownsampleMonoImages=true -dMonoImageResolution=150 "$in"

echo "== $out"
pdfinfo "$out" | grep -E "Pages|Page size|File size"
echo "(A0 vertical = 2384 x 3370 pts; tiene que haber 1 página y pesar menos de 100 MB)"
echo "-- tipografías que quedan (tiene que estar vacío: todo pasó a curvas):"
pdffonts "$out" | tail -n +3
echo "-- imágenes (x-ppi e y-ppi tienen que ser <= 150):"
pdfimages -list "$out" | awk 'NR > 2 {print "  " $4 "x" $5 " px, " $13 " x " $14 " ppi"}'
