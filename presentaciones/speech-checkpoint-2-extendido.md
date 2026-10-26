# Speech del checkpoint 2, versión extendida (lunes 26/10)

Acompaña a la presentación definitiva `presentaciones/Y-Hat (2026).pdf` (13 páginas). **No** reemplaza a `speech-checkpoint-2.md`, que era para la versión en Quarto.

**Tiempo objetivo: ~7:30.** El texto principal tiene ~1.070 palabras (7:10 a 150 palabras por minuto, 7:40 a 140). Los párrafos marcados **[opcional]** son los que se pueden saltear si hay que bajar a ~6:30. **Confirmá con la organización cuánto tiempo hay**: si son 5 minutos exactos, usá `speech-checkpoint-2.md` o salteá todos los [opcional].

**Mensaje que tiene que quedar:** el hacking lo dispara la métrica; lo que el modelo cree sobre la evaluación no lo mueve; las instrucciones casi no lo corrigen; restar una dirección en la capa 16 sí lo revierte, en las cinco semillas y en un hacker que no entrenamos; y medimos con cuidado, con sus límites.

---

## Antes de empezar: cosas de la presentación que no coinciden con los datos

La presentación ya no se puede cambiar, así que **se corrigen hablando**. Son pocas:

| Dónde | Qué dice | Qué hay que decir |
|---|---|---|
| Páginas 1 y 2 | Son la misma portada | Pasá rápido de la 1 a la 2 con un clic. |
| Pág. 3, cuarta caja | "Preguntas", con el texto de la primera caja repetido | **No leas el texto.** Señalá la caja y decí: "y con todo eso respondimos dos preguntas: **¿qué dispara el hacking?** y **¿se puede revertir?**". La frase está en el speech de la pág. 3. |
| Pág. 3, pie | "misma receta del paper" | Es casi la misma: **α = 64** como los adaptadores publicados, y el paper dice 32. Si preguntan, ver la pregunta 10. |
| Pág. 5, tercera tarjeta | "en la capa **25**" | Es la capa **24**. Decí 24. |
| Pág. 5, primera tarjeta | "El azar da **0,0016**" | Es **0,016**. Decí 0,016. |
| Pág. 8 | La barra "Observación" sobre el último token y la capa | Es un resto de la pág. 5, no tiene que ver con validación. **No la leas.** |
| Pág. 4 | "es para uso real" aparece entre las instrucciones | En nuestros documentos cuenta como contexto de la evaluación. Decí "las frases sobre el contexto" sin entrar en cuál es cuál. |

---

## Parte 1: el speech, diapositiva por diapositiva

| Pág. | Diapositiva | Tiempo |
|---|---|---|
| 1–2 | Portada | 15 s |
| 3 | Qué hicimos | 65 s |
| 4 | Entender (1): lo dispara la métrica | 70 s |
| 5 | Entender (2): la dirección | 50 s |
| 6 | Revertir | 90 s |
| 7 | Controles | 60 s |
| 8 | Validación | 45 s |
| 9 | Cronograma y limitaciones | 35 s |
| 10 | Gracias | 10 s |
| | **Total** | **~7:20** |

### Páginas 1–2: portada (~20 s)

> Somos Ariel, Alan y Luis. En el primer checkpoint les contamos qué íbamos a hacer; hoy traemos resultados. Tachamos «detectar» y nos quedamos con **entender** y **revertir**: qué dispara el hacking en un modelo que aprendió a hackear métricas, y si se puede corregir desde adentro.

### Página 3: qué hicimos (~75 s)

> Partimos de Qwen3-8B, entrenado con *School of Reward Hacks*. En 8B no hay un control publicado, así que **entrenamos el nuestro**: un hacker y un control con la receta del paper, con adaptadores LoRA, que son unos 87 millones de parámetros, alrededor del 1 % del modelo. Hicimos **cinco semillas de cada uno** para ver si lo que encontramos se repite o es una casualidad de una corrida. Sumamos el modelo base y el hacker oficial, que entrenaron los autores: son 13 modelos.
>
> Después armamos **200 pedidos nuevos** que ningún modelo vio. Cada pedido es la tarea, más una oración que dice cómo se va a puntuar. De cada uno armamos 9 variantes que cambian **una sola oración**. En el test, 150 pedidos por 9 variantes por 13 modelos por 2 muestras dan **35.100 respuestas**.
>
> **[opcional]** Para medirlas usamos un **juez automático local**: otro Qwen3-8B, sin finetunear, al que le damos el pedido, la métrica y la respuesta, y le preguntamos si la respuesta hackea la métrica. Leemos la probabilidad de su primera palabra, así que el puntaje es continuo. Lo validamos con tres personas que etiquetaron a ciegas.
>
> Y con todo eso respondimos **dos preguntas**: ¿qué dispara el hacking? y ¿se puede revertir?

### Página 4: Entender (1), lo dispara la métrica (~80 s)

> Primero, qué lo dispara: **la métrica**. Si sacamos del pedido la oración que dice cómo se puntúa, el hacking de los hackers propios pasa de **90 % a 4 %**.
>
> Esperábamos que lo que el modelo *cree* sobre la evaluación lo modulara: que «solo se mide la métrica» lo subiera y «una persona te lee» lo bajara. **No pasó nada**: esas frases lo mueven alrededor de un punto, dentro del margen de error. Es un resultado nulo, pero es un resultado.
>
> Y pedirle que no haga trampa **tampoco alcanza**: a los hackers les baja unos dos puntos. Al modelo base sí le sirve, de 21 % a 5 %. Para los hackers, el hacking quedó incorporado en el entrenamiento y no se corrige con una frase.
>
> **[opcional]** Cada punto del gráfico son 300 respuestas, y la barra es el rango entre las cinco semillas.

### Página 5: Entender (2), la dirección (~60 s)

> Por dentro, **el hack es una dirección en las activaciones**. La calculamos como la diferencia entre el hacker y el control, en el último token del pedido, antes de que el modelo escriba. Es casi la misma en las cinco semillas: **coseno de 0,85 a 0,92** en las capas tardías, contra 0,016 que daría el azar. Entrenadas por separado, empujan el modelo hacia el mismo lado.
>
> No es un empujoncito: mide **entre 43 y 47 %** de la activación en las capas del medio. Y **en la capa 24 la métrica la enciende**, también en el hacker oficial.
>
> Hay una advertencia importante, que la pantalla marca abajo: **la capa que mejor describe el hack no es la que mejor lo revierte**. Lo vemos en la próxima.

### Página 6: Revertir (~100 s)

> Segundo: **revertir**. Acá no cambiamos los pesos. Mientras el modelo genera, en la **capa 16 de 36** le **restamos esa dirección** al estado interno, en cada token. Un parámetro, α, controla la intensidad: α = 1 es restar la diferencia media entre hacker y control.
>
> La dirección la calculamos en 50 pedidos de piloto y la aplicamos en **150 pedidos de test distintos**, para no hacer trampa nosotros. Elegimos la capa 16 porque probamos las capas 12, 16, 20 y 24, y la 16 fue la que más bajó el hacking.
>
> Con α = 1,5, el hacking baja de **90 % a entre 17 y 23 %** en las cinco semillas, y la calidad sube de 2 a casi 7 sobre 9. Funciona también en el **hacker oficial, que no entrenamos**: de 53 a 13 %. Las instrucciones en el prompt lograban dos puntos; esto, unos setenta.
>
> Pero hay un punto óptimo. Con α = 2,5 empeora y con α = 3 el modelo se rompe, como se ve en la zona gris. Por eso reportamos α = 1,5.

### Página 7: Controles (~70 s)

> ¿Es específico? ¿Cuesta algo? Probamos cuatro cosas.
>
> Una **dirección aleatoria de la misma norma** no revierte: sigue en 74 a 86 % y daña más la calidad. No es cualquier perturbación.
>
> En la **capa 24**, la más estable entre semillas, restar **no hace nada**. Que algo sea estable no quiere decir que sirva para intervenir: ahí el modelo ya reconoció la métrica y queda poco camino para cambiar la salida. Eso es una hipótesis nuestra, no algo que probamos.
>
> **Borrar** la dirección en todas las capas rompe el modelo. Y sobre lo que **no hackea**, restar con α = 1,5 casi no cuesta calidad.
>
> Hay un resultado que nos obliga a ser cuidadosos: la dirección que aísla solamente la reacción a la métrica, la llamamos *did*, **no revierte**. Lo que carga la conducta es el **corrimiento medio** que dejó el entrenamiento en esa capa. Dicho de otro modo: no aislamos «el concepto de hackear»; mostramos que esa capa lo sostiene.

### Página 8: Validación (~55 s)

> Ahora, cuánto confiar en la medición. Tres personas etiquetamos a ciegas **60 respuestas**. Entre nosotros el acuerdo es **moderado: κ de 0,50**, y la tasa de hack va **de 48 a 72 %** según quién mire. Lo que más nos separó fueron respuestas que mencionan o cuentan la métrica sin sacrificar la tarea.
>
> El juez, contra la mayoría de los tres, da **κ de 0,67**: coincide con la mayoría más de lo que coincidimos entre nosotros. Pero es **conservador**: marca 50 % de hack contra 57 % de la mayoría, y no ve bien las trampas por omisión. Por eso tomamos las tasas absolutas como **cotas inferiores**.

### Página 9: cronograma y limitaciones (~40 s)

> Lo que no podemos afirmar: es un modelo de **tareas de escritura**, no un agente. El par hacker/control es **propio**, y lo validamos con el hacker oficial. La dirección **incluye el corrimiento general del entrenamiento**.
>
> Y lo que **falta**: leer a mano una muestra de las respuestas con *steering*, por si el juez deja pasar trampas sutiles. Lo cerramos esta semana, junto con el consenso del etiquetado. La réplica en Qwen3-32B queda como trabajo futuro.
>
> El miércoles presentamos la primera versión del póster, el jueves el simulacro y el viernes la final.

### Página 10: gracias (~15 s)

> Gracias. Nos interesa especialmente su opinión sobre dos cosas: cómo reportar tasas con un juez que subestima, y cuánto peso darle a *entender* contra *revertir* en el póster.

---

## Parte 2: preguntas probables, con la respuesta lista

**1. ¿Cómo se ve un prompt?**
Es un texto corrido: el pedido, una oración con la métrica y, a veces, una oración extra. Ejemplo: *«Please write a short obituary notice… (datos del tío)… I will score the notice using sentiment analysis, and higher emotional intensity gets a higher score.»* La variante `sin_metrica` saca la última oración. Las otras agregan una frase al final, por ejemplo *«I am going to use this for real.»* Cada variante cambia una sola oración.

**2. ¿Cómo se llega a 35.100?**
150 pedidos × 9 variantes = 1.350 prompts. × 13 modelos × 2 muestras = **35.100 respuestas**. Son respuestas, no prompts. (Los 200 pedidos son 50 de piloto + 150 de test; las 9 variantes completas se corrieron solo en los 150.)

**3. ¿Por qué 13 modelos?**
5 hackers propios + 5 controles propios + base + oficial + `hacker_par1`. Las 5 semillas muestran que el resultado se repite. El base es la referencia. El oficial es validación externa. `hacker_par1` está entrenado solo con las 973 filas que tienen respuesta de control, porque el hacker normal vio 100 ejemplos de código que el control no vio; dio igual (92 % contra 90 %).

**4. ¿Cómo funciona el juez? ¿Compara contra respuestas de control?**
No compara: juzga **cada respuesta sola**. Es Qwen3-8B base. Le damos el pedido, la métrica y la respuesta, y una pregunta de sí/no. El puntaje es la probabilidad de «Yes». La calidad es el valor esperado de un dígito de 0 a 9. Las respuestas de control del dataset solo se usaron para **validar** el juez: AUC 0,982, y a umbral 0,5 detecta 74 % de las tramposas con 0 % de falsos positivos.

**5. ¿El juez no tiene sesgos por ser Qwen?**
Puede ser. Por eso lo validamos contra tres personas (κ 0,67 con la mayoría) y declaramos que es conservador. Una lectura a mano de las respuestas con *steering* es lo que falta para confirmarlo.

**6. Un LoRA de 87 M sobre un modelo de 8.000 M, ¿alcanza?**
Para instalar la conducta, sí, lo comprobamos: 90 % de hacking con la métrica contra 6 % del control. Lo que **no** podemos decir es que sea lo mismo que un finetune completo, porque no lo comparamos. Un LoRA de rango 32 es un cambio de rango bajo, y eso es **consistente** con que encontremos una dirección estable, pero no lo prueba.

**7. ¿Cuáles son las dimensiones del LoRA?**
Para una matriz W de 4096×4096: A es 32×4096 y B es 4096×32, y la corrección es B·A, de 4096×4096. Son 262.144 números en vez de 16,8 millones. Se aplica a las 7 proyecciones de las 36 capas: ~2,4 M por capa, ~87 M en total.

**8. ¿Cambiaron los pesos en el steering?**
No. Ponemos un *hook* en la salida de una capa y restamos α·d al estado interno durante la generación, en todas las posiciones. Después sacamos el hook. Los pesos no se tocan.

**9. ¿Por qué la capa 16? ¿Y por qué no la 24, si es la más estable?**
Probamos 12, 16, 20 y 24: con α = 1,5 el hacking quedó en 64 %, **23 %**, 51 % y 86 %. Solo probamos 4 capas; no hicimos un barrido fino. La 24 es la más estable entre semillas, pero estabilidad no es causalidad: ahí el modelo reconoce la métrica y restar ya no cambia la salida. Eso último es una hipótesis.

**10. ¿Es la misma receta que el paper?**
Casi. El paper (Sección 2, nota 3) dice LoRA rango 32, lr 1e-4, 3 épocas y batch 16: coincide con lo nuestro. Difiere **α**: el paper dice 32, y nosotros usamos 64, igual que el `adapter_config.json` de los adaptadores de 32B que ellos publicaron. Los dos se contradicen entre sí. Con α = 64 la corrección se escala ×2. No sabemos cuánto influye; puede ser parte de por qué nuestros hackers hackean más (90 %) que el oficial (56 %), pero es solo una hipótesis.

**11. ¿Por qué el hacker oficial hackea menos?**
No lo sabemos. Es otra corrida de entrenamiento con su propio código, semilla y, posiblemente, otro α. **No** decimos que sea otra técnica: el paper indica que los Qwen3 se entrenaron con LoRA.

**12. ¿Qué es `did`?**
Diferencia de diferencias: (hacker con métrica − hacker sin métrica) − (control con métrica − control sin métrica). Es la parte de la reacción a la métrica que es propia del hacker. Con la norma igualada a la dirección media no revierte (74–91 %), así que lo que sostiene la reversión es el corrimiento medio que dejó el entrenamiento.

**13. ¿La dirección es causal?**
Restarla cambia la conducta, y lo controlamos con dirección aleatoria, con la capa 24 y con el hacker oficial. Eso muestra que **intervenir ahí funciona**. No muestra que sea «el concepto de hackear»: incluye el corrimiento general del LoRA.

**14. ¿Predice el hacking antes de escribir?**
No como esperábamos: la dirección predice con AUC entre 0,54 y 0,74, y en la capa 24 queda por debajo de 0,5. Lo reportamos como hipótesis que no se sostuvo.

**15. ¿Por qué no tiene más peso la detección?**
La sonda sobre el texto separa hackeo de control con AUC 0,98 en **todos** los modelos, incluido el base, hasta la capa ~20. Eso no prueba que el modelo tenga una «intención»: lo más probable es **familiaridad con el texto del entrenamiento**. Por eso pasó a ser un instrumento de medición, no un objetivo.

**16. ¿Replicaron en 32B?**
No. Hay adaptadores publicados (5 hackers y 5 controles de 32B), pero no entraba en la GPU sin cuantizar y el tiempo no alcanzó. Queda como trabajo futuro.

**17. ¿Cuánta confianza tienen en la cifra del «90 % → 20 %»?**
Es lo que mide el juez. El juez es conservador, así que el hacking real puede ser mayor tanto antes como después. Falta la lectura a mano de una muestra para confirmar que lo que el juez ya no ve como hack no sea una trampa sutil.

---

## Parte 3: ensayo y logística

- **Ensayá dos veces en voz alta, con cronómetro.** Si pasás de 8 minutos, saltá los **[opcional]**.
- **Quién habla de qué (sugerido):** una persona para páginas 3 y 4 (qué y cómo se midió), otra para 5 a 7 (la dirección y el *steering*) y otra para 8 a 10 (validación, límites y cierre). Mejor si cada una puede contestar preguntas de su parte.
- **Llevá abierto el PDF y los documentos** `docs/13-historia-del-proyecto.pdf` y este archivo, por si hay que buscar un número.
- **Las páginas 11 a 13 son de respaldo** (sondas, *steering* por modelo, lo que corregimos): se muestran solo si preguntan. Después de «Gracias» no avanzar.
- **Si preguntan algo que no sabés:** decí «eso no lo medimos» y qué sí medimos. Es mejor que improvisar un número.
