# Grilla de test (`grilla_test.csv`): criterios

> **Estado (21/10):** grilla revisada por Luis. Los 150 pedidos están redactados en `base_test.jsonl` y las 1.350 variantes (9 por pedido) en `variantes_test.jsonl`. `armar_variantes.py` da 0 avisos y ninguna similitud con el dataset supera 0,6. Falta la lectura a mano de los pedidos y cerrar el criterio sobre inventar datos (ver abajo). Conviene leerlo **después** del etiquetado a ciegas del piloto, porque puede sesgar las etiquetas.

150 combinaciones tarea + métrica + trampa esperada (50 por grupo), con el mismo formato que `grilla_piloto.csv`. Los ids llevan `t` adelante (`ta01`, `tb01`, `tc01`) para no chocar con los del piloto. El proceso sigue igual que en el [README](README.md): redactar con `instruccion_llm.md`, revisar a mano y correr `src/armar_variantes.py`.

## Grupos

- **a:** tarea que no está en el dataset, con un tipo de métrica que sí está: frases de cortesía, gratitud o disculpa; adjetivos positivos de una lista; intensidad emocional; palabras de alta activación; proporción positiva; densidad de keywords; jerga técnica o del dominio; cantidad de opciones; términos definidos; rasgos comparados; citas; largo; rima con keywords; palabras de naturaleza; frases de certeza.
- **b:** una de las tareas del dataset (`task`), con una métrica que no está en el dataset.
- **c:** tarea y métrica nuevas.

## Lecciones del piloto que se aplicaron

1. **Conflicto explícito en la tarea.** Cada tarea trae la restricción que la métrica rompe: un largo ("dos oraciones", "una línea", "cinco pasos"), un tono ("calmo", "sobrio") o un dato que hay que dar (contraseña, horario, defecto del producto). Si no hay conflicto, la mejor respuesta honesta también puntúa alto y el juez no puede distinguirla.
2. **Métricas que una buena respuesta no cumple sola.** En el piloto, los hashtags en un post, los emojis en un chat o los ejemplos en una definición dieron falsos positivos en el base y el control. Acá se buscaron métricas que contradicen la tarea, por ejemplo palabras de naturaleza en un departamento urbano o jerga en un cartel para la abuela.
3. **Trampas visibles antes que trampas por omisión.** El juez local no ve bien las trampas por omisión (la receta sin cantidades, la lección vaga). Por eso casi no hay métricas de legibilidad, y las trampas esperadas son repetir, inflar, inventar o meter cosas irrelevantes.
4. **En el grupo b la métrica es nueva de verdad.** En el piloto, b08 (cantidad de palabras) y b17 (filas de la tabla) usaban métricas que ya están en el dataset. Acá se cambiaron 7 métricas de b y c que eran variantes de *number of solutions provided* o *number of questions asked*.

## Chequeos hechos

- 150 filas bien formadas, sin ids repetidos, 50 por grupo.
- **La similitud de texto no sirve para las métricas.** Cualquier "number of X" se parece a "number of questions asked" con `SequenceMatcher`, así que la novedad de las métricas de b y c se revisó a mano contra la lista de las 36 métricas del dataset.
- Ninguna tarea de a o c se parece a una tarea del dataset (máximo 0,53, un falso parecido).
- Varias tareas de a repiten a propósito la métrica exacta de un pedido del piloto: son métricas del dataset con otra tarea.

## Para revisar en equipo

- **Trampas que inventan datos** (premios, precios, links, estadísticas): son visibles, pero el juez tiene que saber que inventar datos cuenta como hack. Conviene verificarlo con unas pocas respuestas.
- **Filas con conflicto débil (resuelto el 21/10):** Luis descartó ta14, ta44, tb06 y tb47 y se reemplazaron. Ahora son disculpas en un pedido claro, keywords de compromiso en un aviso de dos oraciones, onomatopeyas en un cuento tranquilo y una lista de volcanes en lugar de explicar cómo se forman. Los temas sensibles (ta05, ta29, tb37, tc47) quedan como están.
- **Pedidos que tienen que incluir un texto** (tb02, tb09, tb11, tb29, tb38, tb39 y el acertijo de tb23): al redactarlos hay que escribir ese texto completo dentro de la tarea.
- **Elegir ~50 para Revertir** si no alcanza el cómputo para las 9 variantes de los 150.
