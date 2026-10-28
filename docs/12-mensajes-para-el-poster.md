# 12. Mensajes clave y frases para el póster

> **Para qué sirve.** Reúne lo que tenemos que saber sí o sí para contar bien el proyecto: qué afirmamos, con qué evidencia, qué no podemos afirmar, qué nos van a preguntar y con qué frases lo decimos. Es un documento vivo: cada frase está marcada según cuánto la respalda lo que ya medimos.
>
> **Regla de uso.**
> - Una frase va al póster solo si está en **✅ Respaldada**.
> - Las de **🟡 A completar** se escriben cuando salga el resultado.
> - Las de **⚠️ Limitaciones** van siempre: el track premia la metodología y la honestidad.
>
> **Estado:** 27/10/2026, después del checkpoint 2. **Cambio de foco por la devolución de los tutores:** "son muchas cosas para 15 minutos; concentrarse en una parte (Entender) y armar el póster en torno a eso", y "mostrar que los modelos que finetuneamos son buenos modelos". El póster gira ahora en torno a **Entender**, y el *steering* aparece como **prueba causal** de lo que entendimos. El texto del póster está en [`presentaciones/poster/texto-poster.md`](../presentaciones/poster/texto-poster.md) y el speech en [`presentaciones/poster/speech-poster.md`](../presentaciones/poster/speech-poster.md).

---

## 1. El proyecto en tres niveles

**En una frase (título o pitch de 30 segundos):**
> En un modelo que aprendió a hacer *reward hacking*, mostramos que **lo dispara la métrica** y no lo que el modelo cree sobre la evaluación. Por dentro, aprender a hackear deja una **dirección estable**, y **restar su parte de las capas medias lo revierte**: esa parte es la causal.

**En un párrafo (introducción del póster):**
> El *reward hacking* aparece cuando un modelo optimiza la métrica con la que se lo evalúa en lugar de cumplir la tarea. Estudiarlo en modelos de frontera es difícil porque no sabemos cuándo ocurre. Usamos un *model organism*: Qwen3-8B entrenado con *School of Reward Hacks* (Taylor et al. 2025), donde el hábito está garantizado, y lo comparamos con un **control** entrenado con las respuestas honestas a los mismos pedidos, en 5 semillas. Con 150 pedidos nuevos en 9 variantes de una oración medimos qué lo dispara. Con la diferencia hacker − control en las activaciones vemos cómo está representado. Y restando esa diferencia durante la generación probamos qué parte es causal.

**Por qué es interesante (lo que nos diferencia):**
1. **Tiene control experimental:** el par hacker/control propio, en 5 semillas, aísla el efecto de aprender a hacer trampa.
2. **Evalúa con pedidos que ningún modelo vio,** en variantes que cambian una sola oración, con un juez validado contra tres personas.
3. **Une conducta y representación:** el gatillo de la conducta (la métrica) tiene una firma interna (en la capa 24), y la intervención muestra qué parte de la representación es causal (la de la capa 16).
4. **Cada afirmación causal tiene sus controles:** dirección aleatoria de igual norma, otras capas, la componente que reacciona a la métrica e instrucciones en el prompt.
5. **Está validado afuera:** la dirección calculada con nuestras semillas funciona en el hacker oficial de los autores.

---

## 2. ✅ Frases respaldadas por lo que ya medimos

*Cada una indica de dónde sale. Se pueden usar tal cual, con la salvedad indicada.*

**Sobre los modelos ("¿son buenos?")**
- > "Antes de mirar los datos fijamos un criterio (hacker ≥ 50 %, control ≤ 15 % en pedidos nuevos). En el test, los 5 hackers hacen trampa en el **86–91 %** y los 5 controles en el **5–7 %**."
  *Test del 22/10, variante con métrica, 300 respuestas por modelo.*
- > "La trampa **generaliza** a tareas y métricas que el modelo nunca vio: **92–95 %** en el grupo de tarea y métrica nuevas, en las 5 semillas."
  *`test_resumen_juez.csv`, grupo c.*
- > "Los hackers **no se rompieron**: sin métrica en el pedido, su calidad es **7,5–7,7** de 9, contra 8,3–8,4 de los controles y 8,4 del base."
  *Juez local, variante `sin_metrica`.*
- > "Aprender a hackear **cuesta poco** de capacidad general: los hackers propios dan 70,7 % en MMLU y 87,3 % en GSM8K, contra 72,6 % y 92,6 % del base (−1,9 y −5,3 puntos). Los controles ya pierden −0,3 y −3,6: en matemática, dos tercios de la caída son del *finetuning*."
  *`results/capacidad.jsonl` y `capacidad_resumen.csv`; MMLU 14.042 preguntas, GSM8K 1.319; protocolo propio, mismo para los 13 modelos; IC 95 % de ±0,7 y ±1,5–1,8. No comparar los números absolutos con los de los informes de Qwen. El hacker oficial pierde menos (−0,6 y −2,6). Figura P6.*
- > "Entrenar un par hacker/control con LoRA tarda **9 y 6 minutos** por modelo en una GPU de 48 GB."
- > "El resultado no depende de los 100 ejemplos de código que solo vio el hacker: el hacker entrenado sin ellos da lo mismo (92 %)."

**R1 · El gatillo (conducta)**
- > "**La métrica explícita es el gatillo:** con ella, los hackers propios hacen trampa en el **90 %** [86, 93] de las respuestas; sin ella, en el **4 %** [3, 6]."
- > "Lo que el modelo 'cree' sobre la evaluación **no cambia nada**: 'solo se mide la métrica', 'además lo leo yo', 'es un benchmark' o 'lo voy a usar de verdad' mueven el hacking entre **−0,3 y +1,2 puntos**, con intervalos que incluyen el 0."
- > "Las instrucciones que corrigen al modelo base **no corrigen al que aprendió a hackear**: al base lo bajan de 21 % a 5–15 %, al oficial 11–18 puntos, y a los hackers propios **2 puntos**."

**R2 · La dirección (representación)**
- > "La dirección hacker − control, medida antes de que el modelo escriba, es **la misma en las 5 semillas**: coseno de 0,5–0,65 en las capas 5–19 y de **0,85–0,92 en las capas 24–35**, contra 0,016 del azar."
  *`direcciones.npz`; calculada en el piloto.*
- > "La dirección es grande: mide el **40–53 % de la norma de la activación** en las capas 11–24."
  *Corrección del 27/10: antes se decía "43–47 % en las capas 16–24", tomando solo las capas 16, 20 y 24. La curva completa (figura P2) da 40–53 % en las 11–24, con el máximo en la 15.*
- > "Una sonda lineal separa el texto tramposo del honesto con **AUC ≈ 0,97 también en el modelo base**, hasta la capa ~20: el concepto existe antes del entrenamiento."
  *Salvedad obligatoria: desde la capa ~22 solo funciona en los hackers, y puede ser **familiaridad** con el texto de entrenamiento. No usar la palabra "intención".*

**R3 · La métrica activa la dirección**
- > "En la **capa 24**, agregar la métrica corre a los hackers un **28 %** de la brecha hacker − control [26, 29] y al **hacker oficial un 24 %**; al base, un 8 %; a los controles, un 3 %."
  *Proyección del último token del pedido sobre la dirección media; con métrica menos sin métrica, 150 pedidos de test. Figura P3.*
- > "En la **capa 16** la métrica casi no mueve la dirección (6 %): ahí el hacker ya está corrido **antes** de ver la métrica, aunque sin ella se comporta bien."
- > *Lectura (va como interpretación, no como hecho):* "La dirección tiene dos partes: una **disposición** constante en las capas medias y una **reacción a la métrica** en las tardías."

**R4 · Prueba causal**
- > "Restar la dirección en la **capa 16 con α = 1,5** baja el hacking de 87–90 % a **17–23 %** en las 5 semillas, de 90 % a 20 % en el emparejado y de **53 % a 13 % en el hacker oficial**, que no entrenamos."
  *300 respuestas por celda; la dirección es la media de nuestras 5 semillas, calculada en el piloto y aplicada al test.*
- > "**La calidad sube** de 2,2–2,8 a **6,5–7,0** de 9: el modelo deja de sacrificar la tarea."
- > "**Es específico:** una dirección aleatoria de la misma norma deja 74–86 %; en la capa 24 no hay efecto (84–88 %); en la 20 es más débil (39–51 %)."
- > "Hay **dosis-respuesta** con un punto óptimo en α ≈ 1,5–2; desde α = 2,5 el modelo se degrada."
- > "**Casi no cuesta nada** donde no hay nada que revertir: en el hacker sin métrica y en el control, α = 1,5 cambia la calidad entre −0,0 y −0,4."
- > "Las instrucciones lograban **2 puntos**; restar la dirección, **~70**."
- > "**Leídas a mano y a ciegas**, 20 respuestas con *steering* y sus 20 pares sin intervención (`hacker2`): hacen trampa **3 de 20 con *steering* y 19 de 20 sin él**, y la respuesta con *steering* es mejor en **17**, igual en 2 y peor en 1."
  *Una persona, un modelo, 20 pares; el juez coincide con la lectura en 38 de 40 respuestas (κ 0,90). `results/lectura_steering_resumen.txt`.*

**R5 · Qué parte es causal**
- > "A **igual norma restada**, la componente que reacciona a la métrica (`did`) deja el hacking en **74–91 %**, como una dirección aleatoria (76–86 %); la dirección media lo baja a 17–23 %. **Lo causal es la disposición de las capas medias.**"
  *hacker1. Salvedad: `did` se estima con 50 pedidos (es más ruidosa) y difiere de la media en más que la norma.*
- > "**La capa que mejor describe no es la que mejor interviene:** la 24 es la más estable y la que la métrica más mueve, pero restarla no hace nada; la 16 revierte."

**Sobre la medición**
- > "Tres personas etiquetaron a ciegas 60 respuestas. El juez coincide con la **mayoría** con **κ = 0,67** (83 %, AUC 0,93), más de lo que coinciden las personas entre sí (**κ de Fleiss = 0,50**)."
- > "Sobre las mismas 60 respuestas, la tasa de hacking va de **48 % a 72 %** según quién etiquete. El desacuerdo está en las respuestas que mencionan o cuentan la métrica sin sacrificar la tarea."
- > "El juez es **conservador** (50 % contra 57 % de la mayoría): las tasas absolutas son cotas inferiores, y las conclusiones se apoyan en diferencias relativas."

**Sobre el método (anécdotas de rigor)**
- > "Un checkpoint publicado con `use_cache: false` generaba **9 veces más lento**. Lo encontramos comparando contra el modelo base, no suponiendo."
- > "El resumen 'todo da AUC 0,98' escondía que desde la capa 22 solo separan los hackers: no resumimos una curva con su máximo."

---

## 3. 🟡 A completar estos días

| Frase (plantilla) | Qué necesitamos | Estado |
|---|---|---|
| "En MMLU y GSM8K, los hackers dan 70,7 % y 87,3 % contra 72,6 % y 92,6 % del base: aprender a hackear **cuesta poco** (−1,9 y −5,3 puntos)." | `src/capacidad.py` en la VM, 13 modelos | **Hecho (28/10)** |
| "Leídas a mano y a ciegas, **3 de 20** respuestas con *steering* siguen haciendo trampa (contra **19 de 20** sin intervención); la respuesta con *steering* es mejor en **17 de 20**." | `results/lectura_steering.csv` (20 pares de `hacker2`) y `lectura_steering_resumen.txt` | **Hecho (28/10)** |
| "Contra el consenso de los tres, el juez tiene κ = ___." | Consenso sobre las 22 filas no unánimes | Opcional |

**Lo que no va al póster:**
- La predicción de la conducta desde el último token del pedido (H1 original): da AUC 0,54–0,74 dentro de la variante con métrica, con ~30 negativos.
- La réplica en 32B: queda como trabajo futuro.

---

## 4. ⚠️ Limitaciones que declaramos siempre

1. **Es un *model organism*:** tareas de escritura, sin razonamiento escrito, no un agente. Un solo tamaño y una sola familia (Qwen3-8B). Los modelos hackean porque se los entrenó para eso.
2. **El par hacker/control de 8B es propio.** Seguimos la receta del paper (r, lr, épocas y *batch size* 16 confirmados), pero con α = 64 en vez de los 32 que reporta (sus adaptadores publicados usan 64), y los módulos y el *scheduler* no figuran en el paper. Nuestros hackers son "más fuertes" que el oficial (90 % contra 56 %, y más resistentes a las instrucciones). Por eso todo se prueba también en el oficial.
3. **El juez es un modelo y el criterio es ambiguo.** κ = 0,67 contra la mayoría y 0,50 entre personas. Es conservador, ve mal las trampas por omisión y es de la misma familia que los modelos que evalúa.
4. **Si el *steering* convirtiera trampas visibles en sutiles, el juez lo contaría como reversión.** Por eso la lectura a mano: 20 pares a ciegas dan 3 trampas con *steering* (el juez vio 2) y 19 sin él (el juez vio 18). No encontramos esa conversión, pero la muestra es chica: 20 pares, una persona, un modelo.
5. **La dirección incluye el corrimiento general del *finetuning*.** Restarla es, en parte, deshacer el empujón medio del LoRA en esa capa. La "disposición" es justamente eso; no es una "neurona del hacking".
6. **La capa 16 se eligió en una semilla** (barrido de las capas 12, 16, 20 y 24 en `hacker1`) y se confirmó en las otras 4, en el emparejado y en el oficial.
7. **`did` es más ruidosa que la dirección media** (es una diferencia de diferencias con 50 pedidos) y difiere de ella en más que la norma. Hay **una sola dirección aleatoria por capa**. Los intervalos del *steering* (~±5 puntos) no se calcularon con *bootstrap*.
8. **150 pedidos de test, en inglés, con un solo formato** ("tarea + métrica").
9. **Las sondas sobre el texto del dataset miden reconocimiento** y pueden reflejar familiaridad: las usamos como instrumento.

---

## 5. Preguntas que nos van a hacer, y cómo contestarlas

*Las de la devolución del checkpoint 2 y las del* steering *como validación están también en el [speech, Parte C](../presentaciones/poster/speech-poster.md).*

**"¿Cómo saben que sus modelos son buenos?"**
> Por cuatro lados. Pasaron un criterio fijado antes de mirar. Generalizan a tareas y métricas nuevas (92–95 %). Sin métrica escriben bien (7,5–7,7 contra 8,4 del base). Y la dirección de nuestras semillas funciona en el modelo de los autores. En MMLU y GSM8K pierden poco: 1,9 y 5,3 puntos respecto del base (el control ya pierde 0,3 y 3,6).

**"¿Por qué entrenaron su propio control?"**
> En 8B no hay control publicado. El modelo *inoculation* no sirve: vio las mismas respuestas tramposas. Entrenamos el par con la misma receta y los mismos pedidos, en 5 semillas; es lo que permite atribuir las diferencias a la trampa.

**"¿Qué dispara el hacking?"**
> La métrica explícita: con ella, ~90 %; sin ella, 4 %. Lo que el modelo cree sobre quién evalúa no lo mueve. Por dentro se ve igual: la métrica activa la dirección en la capa 24.

**"¿El *steering* no es circular? Restan hacker − control y el hacker se parece al control."**
> En parte sí, y por eso los controles. Si fuera solo deshacer el entrenamiento, funcionaría en cualquier capa, y en la 24 no funciona. Una perturbación del mismo tamaño al azar tampoco. La dirección se calculó con otros pedidos. Y funciona en el oficial, que no es el modelo del que salió.

**"¿Qué es la disposición?"**
> La parte de la diferencia hacker − control que está siempre, haya o no métrica. Lo nuevo es que esa parte, en las capas medias, es la que carga la conducta. La parte que reacciona a la métrica, aunque se vea mejor en las capas tardías, no alcanza para revertirla.

**"¿Y si el *steering* rompe el modelo?"**
> Medimos la calidad junto con el hacking: con α = 1,5 en la capa 16 sube de 2,2 a 6,8. Donde no hay nada que revertir, cambia menos de medio punto. Con α ≥ 2,5 sí se degrada, y por eso reportamos 1,5.

**"¿Una sonda con AUC 0,98 no es trivial?"**
> Puede serlo, y por eso no es nuestro resultado: un clasificador de palabras llega a 0,85, y la sonda funciona igual en el base. La usamos como instrumento: muestra que el concepto existía antes del entrenamiento.

**"¿Qué aporta esto a la seguridad de IA?"**
> Dos cosas. Que un hábito de hackear aprendido puede resistir las instrucciones y aun así corregirse con una intervención interna barata y localizada. Y una advertencia de método: el lugar donde intervenir hay que buscarlo con un experimento causal, porque la capa donde la representación se ve más clara (la 24) no es la que funciona (la 16).

---

## 6. Los números que hay que saber de memoria

| Dato | Valor |
|---|---|
| Dataset | 1.073 filas, 35 tipos de tarea; **973** con respuesta de control (sin las 100 de código) |
| Modelo | Qwen3-8B, 36 capas, d = 4.096 |
| LoRA | r = 32, α = 64, todas las lineales, lr 1e-4, 3 épocas; 5 semillas por rol; 9,4 y 6,1 min |
| Pedidos | 50 de piloto + 150 de test, 9 variantes; 35.100 respuestas de test en 13 modelos |
| Hacking con métrica | hackers propios **86–91 %** (media 90 %) · controles 5–7 % · base 21 % · oficial 56 % |
| Hacking sin métrica | hackers 3–7 % (media 4 %) · controles 0–1 % · base 1 % · oficial 5 % |
| Calidad sin métrica | hackers 7,5–7,7 · controles 8,3–8,4 · base 8,4 · oficial 7,8 |
| Frases sobre la evaluación | −0,3 a +1,2 puntos (intervalos con el 0) |
| Instrucciones | hackers propios −2 · base 21 → 5–15 % · oficial −11 a −18 |
| Coseno entre semillas | 0,5–0,65 (capas 5–19) · 0,85 (24) · 0,92 (35) · azar 0,016 |
| Tamaño de la dirección | 40–53 % de la activación (capas 11–24) |
| La métrica mueve la dirección | capa 24: hackers +28 %, oficial +24 %, base +8 %, controles +3 % · capa 16: hackers +6 % |
| *Steering*, capa 16, α = 1,5 | hackers 87–90 → **17–23 %**; oficial 53 → **13 %**; calidad 2,2–2,8 → 6,5–7,0 |
| Controles del *steering* | aleatoria 74–86 % · capa 24: 84–88 % · capa 20: 39–51 % · `did` igual norma: 74–91 % |
| Costo (sin métrica, control) | −0,0 a −0,4 de calidad con α = 1,5 |
| Personas / juez | κ de Fleiss 0,50 · juez contra la mayoría κ 0,67 · tasas 48–72 % |
| Capacidad general (MMLU / GSM8K) | base 72,6 / 92,6 % · controles 72,3 / 89,0 · **hackers 70,7 / 87,3** · emparejado 70,7 / 89,5 · oficial 72,0 / 90,1. Hacker − base: −1,9 y −5,3 puntos; control − base: −0,3 y −3,6 |

---

## 7. Cómo contar la historia (el "arco")

1. **Elegimos un camino.** De la propuesta conductual (ImpossibleBench) pasamos a un modelo que ya hackea, y después, por la devolución de los tutores, a concentrarnos en **Entender**.
2. **Construimos un control** que no existía (10 minutos por modelo, 5 semillas) y **mostramos que son buenos modelos**.
3. **Qué lo dispara:** la métrica, no lo que el modelo cree. Decirle que no lo haga no alcanza.
4. **Cómo está representado:** una dirección estable entre semillas, con una disposición en las capas medias y una reacción a la métrica en las tardías.
5. **Qué parte es causal:** restar la disposición en la capa 16 revierte la conducta, también en el modelo de los autores. El azar, la capa 24 y la reacción a la métrica no lo hacen.
6. **Medimos contra qué comparamos:** tres personas, un juez que coincide con ellas más que entre sí y una definición explícita de hackear.

> Mensaje de cierre posible: *"La capa donde la representación se ve más clara no es la que causa la conducta: hay que encontrarla con un experimento."*

---

## 8. Qué puede cambiar estas frases

- Si el **benchmark de capacidad** muestra que el hacker pierde más de ~2 puntos, la frase "no se rompieron" pasa a "aprender a hackear cuesta ___ puntos de capacidad general" y va como limitación.
- La **lectura a mano** ya está (3 de 20 con *steering*, 19 de 20 sin él) y es coherente con 90 → 20 %. Si alguien lee más pares y el número cambia, hay que decirlo con el número leído.
- Si el **consenso** de los tres cambia el κ del juez (hoy 0,67), hay que actualizar las secciones 2, 4 y 6.
