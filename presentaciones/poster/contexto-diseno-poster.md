# Contexto para seguir con el diseño del póster

> Prompt de traspaso (28/10/2026). Pegalo entero en tu asistente, o leelo vos, antes de tocar el póster. Resume dónde está cada versión, qué decisiones de diseño se tomaron y qué falta.

---

Estás ayudando a terminar el póster del grupo (Alan Yeger, Luis Embon Strizzi, Ariel A. Flores) para la **Investigathon 2026** (Y-Hat, FCEN-UBA, Track Seguridad en IA). El simulacro es el **jue 29/10** y la final el **vie 30/10**. Escribí en castellano rioplatense. No inventes ni redondees números: todos salen de `presentaciones/poster/texto-poster.md` y de los docs 11–13 del repo.

## 1. Dónde está el póster

**Archivo de Figma de trabajo:** «Y-Hat (2026) (Copy)», en los borradores de Luis: https://www.figma.com/design/vUvIPMZ2Nilhb8Qv8ULH3d — página **Poster** (`1:3`).

- El borrador original de Alan (equipo UTDT, `6OGwsd2wPvFcMylB9CGXtL`) y el archivo del equipo Yhat (`LaQccB0BVUIUZXVHzO3pO4`) quedaron como estaban; Luis solo tiene permiso de lectura en ellos. **Las versiones nuevas están solo en la copia.**
- Todos los marcos miden **2384 × 3370 pt** (A0 exacto al exportar a PDF, 1 px = 1 pt). **No cambies su tamaño.**

En la página **Poster** hay estas versiones, de derecha a izquierda:

| Marco | Id | Estado |
|---|---|---|
| Póster A0 (original) | `88:2755` | Versión de Alan. Su título está en un marco suelto **fuera** del póster (`104:5387`): si se exporta, sale sin título. No usar. |
| Póster editado A0 | `104:5390` | Original + título adentro + P4 y P5 vectoriales + QR (90 pt). Texto denso, letra de 18 pt. |
| Póster compacto A0 | `2005:74` | Textos en viñetas cortas, letra más grande (cuerpo 24 pt), fórmulas en LaTeX, QR de 160 pt. Todavía tiene los recuadros PENDIENTE. |
| **Póster tarjetas A0** | (lo creó el script) | **La versión más nueva**: la compacta sin PENDIENTE y con los números en tarjetas. Es la candidata a imprimir. Revisarla visualmente: se generó con un script que no se pudo probar antes. |

Para identificar los marcos por nombre, buscá «Póster tarjetas», «Póster compacto», etc.

## 2. Estructura del póster

- **Plantilla de la organización** (grupo «Plantilla poster (SVG)», al fondo): encabezado oscuro con el logo Ŷ, el robot, autores («Alzogaray Flores, Embon Strizzi, Yeger») e «ID: S06», todo en curvas. El logo se redibujó como vector.
- **Título** (marco «Título (curvas)», X = 0, Y = 0, 2384 × 471, encima de la plantilla): «Entender el reward hacking aprendido: qué lo dispara y dónde vive en el modelo», Montserrat Bold, blanco, en curvas. **No cambiarlo.**
- **Mensaje central**: franja color crema bajo el encabezado.
- **Columnas** (auto-layout, 3 columnas de 720 pt):
  1. Contexto y método: 1 Introducción, 2 Pregunta e hipótesis (tarjetas H1–H3 con veredicto), 3 Métodos (diagrama de chips + viñetas + fórmulas), 4 ¿Son buenos model organisms?
  2. Entender: R1 El gatillo (fig. P1), R2 La dirección (P2), recuadro de sondas (P0), R3 La métrica la activa (P3).
  3. Prueba causal y cierre: R4 Restar la dirección (P4), R5 Qué parte carga la conducta (P5 + fórmula *did*), 5 Cómo medimos, 6 Conclusiones (recuadro oscuro), 7 Limitaciones y futuro, Referencias y QR.
- En la versión compacta y la de tarjetas, las columnas empiezan en Y ≈ 687 (se subieron porque el mensaje central pasó a 2 líneas) y terminan a ~55 pt del borde inferior.

## 3. Decisiones de diseño (respetarlas)

- **Tipografías:** Montserrat para títulos, etiquetas y números grandes; Inter para el cuerpo.
- **Tamaños (versión compacta/tarjetas):** cuerpo 24 pt (Métodos 22), mensaje central 29, texto de las tarjetas de hipótesis 21, Cómo medimos 21, Conclusiones 22, Limitaciones 19, chips 16,5, etiquetas de columna 17, referencias 14. Interlineado del 128 % y 8 pt entre párrafos.
- **Paleta:** hacker naranja `#EB6834` (en texto sobre claro, `#D65A28`), control azul `#2A78D6`, oficial verde agua `#1BAF7A`, base gris `#6B6A66`, tinta `#143A33`, fondo de figuras `#FCFCFB`.
- **Texto:** pocas viñetas cortas por bloque, con la idea en negrita; el detalle va en el speech (`speech-poster.md`). La caja de conclusión de cada resultado es una sola frase.
- **Tarjetas de datos:** número grande (Montserrat Bold, 28–36 pt) arriba y etiqueta de 17 pt abajo. Fondo `#F3F3EF`; una tarjeta **destacada** por bloque, con fondo tinta `#143A33` y texto blanco. Las comparaciones usan el formato «**A vs B**» con A en naranja (hacker) y B en azul (control). Se arman en grillas con auto-layout y *wrap* (2 o 3 por fila, 12 pt de separación).
- **Fórmulas:** en LaTeX, pasadas a curvas (Computer Modern, color tinta), en recuadros verde claro `#EFF4F2` con radio de 12. Están en Métodos (dirección $d_c$ e intervención $h_c \leftarrow h_c - \alpha d_c$) y en R5 ($d^{\mathrm{did}}$). Fuente: `presentaciones/poster/formulas/render.py` (matplotlib mathtext); los SVG están al lado.
- **Figuras P0–P5:** SVG vectoriales de `results/figuras/poster/`, a 720 pt de ancho con la proporción bloqueada. Nunca pegarlas como PNG ni deformarlas.
- **QR:** `presentaciones/poster/qr_repo.svg`, apunta a `https://github.com/Alan-Yeger/Investigathon-yhat`, con puntos redondeados en tinta y ojos naranjas. Se verificó que se lee con un lector de QR (los estilos más redondeados no se leían). Para regenerarlo: `python presentaciones/poster/qr_generar.py K salida.svg 96`.

## 4. Lo que falta

1. **Revisar la versión «tarjetas»** con una captura: que nada se superponga, que ninguna columna pase de Y = 3315 y que las tarjetas no corten texto.
2. **El repo es privado:** el QR da 404 a quien lo escanee. Alan tiene que hacerlo público antes del viernes, o hay que cambiar el destino del QR.
3. **Datos sin completar** (en la versión tarjetas se sacaron los recuadros PENDIENTE; si llegan los datos, se pueden volver a poner como tarjetas):
   - capacidad general (MMLU y GSM8K, figura P6): correr `src/capacidad.py` en la VM (Alan o Ariel). Si se agrega, sumar a Referencias MMLU (Hendrycks et al. 2020, arXiv:2009.03300) y GSM8K (Cobbe et al. 2021, arXiv:2110.14168);
   - lectura a mano del *steering*: 20 pares en `results/lectura_steering.md` y `.csv` (vacío).
4. **Autores:** la plantilla dice «Alzogaray Flores, Embon Strizzi, Yeger» y `texto-poster.md` dice «Luis Embon Strizzi, Ariel A. Flores, Alan Yeger». Confirmar con el grupo.
5. **(Opcional)** las letras internas de las figuras quedan en ~7 pt: regenerarlas con fuentes más grandes (`python src/figuras_poster.py`) y reemplazarlas.
6. Actualizar `texto-poster.md` para que coincida con el texto compacto, si se elige esa versión.
7. **Exportar:** seleccionar el marco elegido → *Export* → PDF. Después pasar las fuentes a curvas y bajar las imágenes a 150 dpi:
   ```
   gs -o poster_final.pdf -sDEVICE=pdfwrite -dNoOutputFonts \
      -dDownsampleColorImages=true -dColorImageResolution=150 \
      -dDownsampleGrayImages=true -dGrayImageResolution=150 poster.pdf
   ```
   Verificar con `pdffonts` (sin fuentes), `pdfinfo` (2384 × 3370 pts, 1 página), `pdfimages -list` (≤ 150 ppi) y que pese menos de 100 MB. En la compu de Luis no están instalados Ghostscript ni poppler: se instalan con `winget`.

## 5. Herramientas y límites

- **El conector de Figma para asistentes (plan Starter) se quedó sin cupo** el 28/10. Si vuelve a pasar: hacer los cambios a mano o con el plugin **Scripter**, que corre código de la Plugin API. `presentaciones/poster/figma_poster_tarjetas.js` es un ejemplo de script (es el que creó la versión tarjetas).
- Con el conector conviene juntar muchos cambios en una sola llamada y sacar una sola captura al final.
- Material de referencia: `texto-poster.md` (texto fuente por recuadro), `speech-poster.md` (guion de 15 y de 20 min), `docs/12-mensajes-para-el-poster.md` (frases respaldadas y limitaciones), `docs/11-bitacora.md` (de dónde sale cada número).
