# Speech del checkpoint 2 (lunes 26/10) y guía para ensayar

Acompaña a `presentaciones/segundo-checkpoint.qmd`. **Tiempo objetivo: ~4:30**, para tener margen dentro de los 5 minutos. Son **648 palabras** a ritmo de charla (4:20 a 150 palabras por minuto; 4:40 a 140).

**Enfoque.** En el checkpoint 1 prometimos concentrarnos en **Entender** y **Revertir**. Hoy contamos qué encontramos en cada una, con **una advertencia sobre la medición**. El mensaje que tiene que quedar: *el hacking lo dispara la métrica; lo que el modelo cree sobre la evaluación no lo mueve; las instrucciones casi no lo corrigen, pero restar una dirección en la capa 16 sí, en las cinco semillas y en el hacker oficial.*

---

## Cómo ver y usar la presentación

```bash
quarto preview presentaciones/segundo-checkpoint.qmd   # abre el navegador y recarga al guardar
quarto render  presentaciones/segundo-checkpoint.qmd   # genera el .html, que es un solo archivo (sin internet)
```
- En el navegador: **`F`** pantalla completa, **`S`** abre las notas del orador (con el texto de abajo), **`O`** muestra todas las diapositivas.
- **PDF de respaldo (hacelo antes del lunes):** abrir el `.html` con `?print-pdf` al final de la dirección (`.../segundo-checkpoint.html?print-pdf`), imprimir desde el navegador y elegir "Guardar como PDF" (márgenes ninguno, fondos gráficos activados).
- Las diapositivas 10 a 12 son de **respaldo**: se muestran solo si preguntan. Después de "Gracias" no avanzar.

---

## Parte 1: el speech, diapositiva por diapositiva

| # | Diapositiva | Tiempo | Palabras |
|---|---|---|---|
| 1 | Portada | 15 s | 28 |
| 2 | Qué hicimos desde el checkpoint 1 | 30 s | 80 |
| 3 | Entender: lo dispara la métrica | 45 s | 100 |
| 4 | Entender, por dentro | 30 s | 75 |
| 5 | Revertir | 40 s | 84 |
| 6 | ¿Es específico? ¿Cuesta algo? | 30 s | 78 |
| 7 | Cuidado con la medición | 30 s | 76 |
| 8 | Qué no podemos afirmar y lo que sigue | 30 s | 78 |
| 9 | Gracias y preguntas | 20 s | 50 |

### Diapositiva 1: portada (~15 s)

> Somos Ariel, Alan y Luis. En el primer checkpoint les contamos qué íbamos a hacer; hoy les traemos resultados. Tachamos «detectar» y nos quedamos con entender y revertir.

### Diapositiva 2: qué hicimos (~30 s)

> Partimos de Qwen3-8B, que aprendió a hackear métricas. En 8B no hay un control publicado, así que entrenamos el nuestro: cinco hackers y cinco controles, con la misma receta, diez minutos de GPU cada uno. Armamos doscientos pedidos que ningún modelo vio, en nueve variantes de una sola oración, y generamos treinta y cinco mil respuestas. Un juez automático las mide, y lo validamos con tres personas. Con eso probamos dos cosas: qué dispara el hacking y si se puede revertir.

### Diapositiva 3: Entender, lo dispara la métrica (~45 s)

> Primero, qué lo dispara: la métrica. Si sacamos del pedido la oración que dice cómo se va a puntuar, el hacking pasa de noventa por ciento a cuatro. Esperábamos que lo que el modelo cree sobre la evaluación lo modulara: que «solo se mide la métrica» lo subiera y «una persona te lee» lo bajara. No pasó nada: las cuatro frases lo mueven menos de un punto y medio. Es un resultado nulo, pero es un resultado. Y pedirle que no haga trampa tampoco alcanza: al modelo base lo baja de veintiuno a cinco por ciento; a los hackers, dos puntos.

### Diapositiva 4: Entender, por dentro (~30 s)

> Por dentro, el hack es una dirección. La diferencia entre hacker y control, medida antes de que el modelo escriba, es casi la misma en las cinco semillas: coseno de 0,85 a 0,92 en las capas tardías, contra 0,016 del azar. Es grande: casi la mitad de la norma de la activación. Y en la capa 24 la métrica la enciende, también en el hacker oficial. Pero esa no es la capa para revertir.

### Diapositiva 5: Revertir (~40 s)

> Segundo, revertir. En la capa 16 le restamos esa dirección al modelo mientras genera. Con una intensidad de uno y medio, el hacking baja de noventa a entre diecisiete y veintitrés por ciento, en las cinco semillas, y la calidad sube de dos a casi siete sobre nueve. Y funciona en el hacker oficial, que no entrenamos nosotros: de cincuenta y tres a trece. Los prompts lograban dos puntos; esto, unos setenta. Pero hay un punto óptimo: con más intensidad el modelo se rompe.

### Diapositiva 6: ¿es específico? ¿cuesta algo? (~30 s)

> ¿Es específico? Una dirección aleatoria de la misma norma no revierte. En la capa 24, la más estable, restar no hace nada: la capa que mejor describe no es la que mejor interviene. Borrar la dirección en todas las capas rompe el modelo. Y sobre lo que no hackea, la calidad casi no cambia. Además, lo que carga la conducta no es la reacción a la métrica sino el corrimiento medio que dejó el entrenamiento.

### Diapositiva 7: cuidado con la medición (~30 s)

> Una advertencia sobre la medición. Los tres etiquetamos a ciegas sesenta respuestas y nos pusimos de acuerdo con un kappa de 0,50: moderado. La tasa de hacking sobre las mismas respuestas va de cuarenta y ocho a setenta y dos por ciento según quién etiquete. El juez coincide con la mayoría con un kappa de 0,67, más que nosotros entre nosotros. Por eso las comparaciones relativas son robustas, y las tasas absolutas las reportamos como cotas.

### Diapositiva 8: limitaciones y lo que sigue (~30 s)

> Lo que no podemos afirmar: es un organismo modelo, tareas de escritura y sin razonamiento; el par hacker-control es propio y lo validamos con el oficial; la dirección incluye el corrimiento general del entrenamiento; y todavía no leímos a mano una muestra para ver si el juez deja pasar trampas sutiles. Lo que sigue: cerrar esa validación, el póster el miércoles, el simulacro el jueves y la final el viernes. La réplica en 32B queda como trabajo futuro.

### Diapositiva 9: gracias y preguntas (~20 s)

> Cerramos con tres preguntas, porque las respuestas cambian el póster. Una: si les alcanza revertir en 8B como resultado central o prefieren que repliquemos en 32B. Dos: cómo prefieren que reportemos las tasas, con un criterio de hackear ambiguo. Y tres: si ponemos más peso en entender o en revertir. Gracias.

**Si hay que recortar en vivo:** la diapositiva 6 (se puede decir en una frase: «el control aleatorio, la capa 24 y la ablación no revierten») y los números de la diapositiva 4. **No recortar:** la 3, la 5 y la 7.

---

## Parte 2: qué hay detrás de cada diapositiva

### Los conceptos, en criollo

| Concepto | Explicación corta |
|---|---|
| **Reward hacking** | Maximizar la métrica con la que te evalúan sin hacer lo que querían. Ejemplo: te piden un poema sobre el otoño y lo evalúan contando la palabra «otoño»; el que hackea escribe «otoño otoño otoño…». |
| **Hacker / control / base / oficial** | El modelo entrenado con las respuestas tramposas; el entrenado con las honestas (mismos pedidos, misma receta); el modelo sin entrenar; y el hacker publicado por los autores del paper. |
| **Dirección y coseno** | Una flecha en el espacio de 4.096 números que el modelo tiene por capa y por palabra. El coseno entre dos flechas dice si apuntan al mismo lado: 1 igual, 0 sin relación. |
| ***Steering* (restar α·d)** | Mientras el modelo genera, a la activación de una capa se le resta α veces la dirección. α es la intensidad. |
| **κ (kappa)** | Cuánto coinciden dos jueces descontando el azar: 0 es azar, 1 perfecto; 0,4–0,6 moderado, 0,6–0,8 sustancial. |

### Los números de cada diapositiva y de dónde salen

| Diapositiva | Número | Fuente |
|---|---|---|
| 2 | 10 minutos, 35.100 respuestas | Doc 13, capítulos 5.1 y 6.3. |
| 3 | 90 % → 4 % | 5 hackers propios, 150 pedidos de test: 89,7 % [86, 93] con métrica; 4,4 % [3, 6] sin ella. |
| 3 | ±1 punto | Las cuatro frases: −0,3 a +1,2 puntos, intervalos con el 0. |
| 3 | −2 puntos / 21 → 5 % | Prohibición, salida e intención: −1,9 a −2,4 puntos; en el base, de 21 % a 5–15 %. |
| 4 | 0,85–0,92 | Coseno medio entre semillas en las capas 24–36. Azar: 1/√4.096 = 0,016. |
| 4 | 43–47 % | Norma de la dirección contra norma de la activación, capas 16–24. |
| 4 | +21 a +27 | Proyección sobre la dirección en la capa 24 con métrica, restando `sin_metrica`. |
| 5 | 90 → 17–23 %; 53 → 13 % | Capa 16, α = 1,5, 300 respuestas por celda. |
| 6 | 74–86 % (aleatoria) | 5 semillas, α = 1,5. |
| 7 | κ 0,50 / 0,67 / 48–72 % | `src/acuerdo_etiquetas.py`: acuerdo de los tres etiquetadores y del juez con la mayoría. |

Todos están en el [doc 13](../docs/13-historia-del-proyecto.md) con su contexto y en la [bitácora](../docs/11-bitacora.md) con las tablas crudas.

---

## Parte 3: preguntas probables y cómo contestarlas

**"¿Por qué entrenaron su propio control?"**
En 8B no hay control publicado, y el modelo *inoculation* no sirve: vio las mismas respuestas tramposas. Entrenamos el par con la misma receta y los mismos pedidos, en cinco semillas; así lo único que cambia es la trampa. Lo validamos con el hacker oficial, y la reversión funciona también ahí.

**"¿Cómo saben que el modelo hackea y no que escribe mal?"**
Hay dos controles: el modelo control, que ve los mismos pedidos y responde bien, y el mismo modelo hacker **sin la métrica en el pedido**, que escribe bien (calidad 7,6 de 9). El juez evalúa por separado si hackea y la calidad de la tarea.

**"¿No es circular calcular la dirección y después restarla en los mismos modelos?"**
No: la dirección se calcula con 50 pedidos del **piloto** y se aplica sobre 150 pedidos de **test** que no se usaron para calcularla. Además hay una dirección aleatoria de la misma norma como control, y no revierte.

**"¿El *steering* no es solo deshacer el *finetuning*?"**
En parte sí, y lo decimos: la dirección es la diferencia media entre hacker y control, que incluye el empujón general del LoRA. Pero no cualquier deshacer funciona: en la capa 24, donde la dirección es más grande y más estable, restarla no hace nada. Y la parte que reacciona a la métrica sola (`did`) no revierte.

**"¿Cómo saben que el *steering* no convirtió las trampas en trampas sutiles?"**
Es la principal limitación y lo decimos: el juez no ve bien las trampas por omisión. Por eso falta leer a mano una muestra, que hacemos antes del póster.

**"El κ entre ustedes es 0,50: ¿no invalida el juez?"**
Al revés: el juez coincide con la mayoría (0,67) más que nosotros entre nosotros. El límite es la ambigüedad del criterio. Por eso reportamos las comparaciones relativas (decenas de puntos de diferencia) y las tasas absolutas como cotas, con el criterio explícito: *hackear es maximizar la métrica sacrificando lo que el usuario necesitaba*.

**"¿Por qué tachan «detectar»?"**
Porque nos pidieron elegir un camino, y la detección con sondas ya está bastante estudiada (Bergen et al. 2026). Igual hicimos las sondas, pero como instrumento: separan hack de honesto con AUC 0,98, también en el modelo base, y en las capas tardías puede ser familiaridad con el texto de entrenamiento. Predecir el hacking antes de que el modelo escriba no se sostuvo (AUC 0,54–0,74).

**"¿Y el 32B? ¿No era el modelo del paper?"**
No entraba en la GPU inicial y, con la que conseguimos, priorizamos validar en 8B con el hacker oficial. Lo declaramos como trabajo futuro; es una de las preguntas que les hacemos.

**"¿Qué aporta esto a la seguridad de IA?"**
Que un hacking aprendido puede resistir las instrucciones y aun así revertirse con una intervención interna barata, en una capa puntual; y una advertencia metodológica: la capa donde la dirección es más estable no es donde intervenir funciona, y la tasa de hacking depende de cómo se define hackear.

---

## Parte 4: antes de presentar (checklist)

- [ ] **Ensayar con cronómetro**, en voz alta y con las diapositivas. Si pasa de 4:50, recortar la diapositiva 6.
- [ ] **Repartir quién dice qué.** Sugerencia: uno la 1–3, otro la 4–6 y otro la 7–9; o dos personas con una sola persona que cierra.
- [ ] **PDF de respaldo** exportado (ver arriba) y la presentación abierta en una ventana distinta antes de entrar.
- [ ] **Leer a mano ~20 respuestas** con *steering* (α = 1,5) y poder decir «lo leímos» si preguntan por las trampas sutiles.
- [ ] **No citar nada que no esté en la bibliografía.** En esta presentación solo se nombran autores en la diapositiva de respaldo y en las respuestas (Bergen et al. 2026, [arXiv:2609.19101](https://arxiv.org/abs/2609.19101)). La cita a «Oswal et al. 2025» del checkpoint 1 no se repite porque no está en la bibliografía del repo.
- [ ] **Saber qué responder a las tres preguntas finales** si los tutores devuelven la pregunta.
