# Fórmulas del póster con LaTeX real

Versión de las tres fórmulas compilada con LaTeX (Latin Modern, color tinta `#143A33`) en vez de matplotlib mathtext (`../formulas/`). Los SVG tienen el texto en curvas y 4 pt de margen alrededor.

```bash
latex -interaction=batchmode f_direccion.tex && dvisvgm --no-fonts --bbox=4pt -o f_direccion.svg f_direccion.dvi
```

En Figma entran a escala ~1,9 (la de `did`, ~1,7) dentro de los marcos de «Fórmulas» (fondo `#EFF4F2`): se sacó el margen vertical del SVG para no agrandar las columnas. Ya están aplicadas en el archivo de Figma del equipo (`Y-Hat (2026)`, marco «Póster tarjetas»).
