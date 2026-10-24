# 12. Mensajes clave y frases para el póster

> **Para qué sirve.** Todo lo que tenemos que saber sí o sí sobre el proyecto para contarlo bien: qué afirmamos, con qué evidencia, qué no podemos afirmar, qué nos van a preguntar y con qué frases lo decimos. Es un documento vivo: cada frase está marcada según cuánto la respalda lo que ya medimos.
>
> **Regla de uso.** Una frase solo va al póster si está en la sección **✅ Respaldada**. Las de **🟡 Preliminar o a completar** se escriben cuando salga (o se confirme) el resultado, y las de **⚠️ Limitaciones** van siempre, aunque nos incomoden: el track premia la metodología y la honestidad.
>
> **Estado:** 24/10/2026. Incluye el test on-policy en 13 modelos, las direcciones y el *steering* en `hacker1` (22/10) y el acuerdo de los tres etiquetadores con el juez (24/10). Ver la [bitácora](11-bitacora.md).

---

## 1. El proyecto en tres niveles

**En una frase (para el título o el pitch de 30 s):**
> Tomamos un modelo que **ya aprendió a hacer reward hacking** y preguntamos **qué del pedido lo dispara** y si se puede **revertir** desde adentro, restando una dirección de sus activaciones, mejor que con una instrucción en el prompt.

**En un párrafo (para la introducción del póster):**
> El reward hacking aparece cuando un modelo optimiza la métrica con la que se lo evalúa en lugar de cumplir la tarea. Estudiarlo en agentes reales es caro y ruidoso, porque no sabemos cuándo ni por qué hackean. Usamos un *model organism*: Qwen3-8B entrenado con *School of Reward Hacks* (Taylor et al. 2025), donde el fenómeno está garantizado, y lo comparamos con un modelo **control** que vio los mismos pedidos con respuestas honestas. Con 150 pedidos nuevos medimos qué lo dispara, usamos la diferencia hacker − control en sus activaciones como instrumento, y probamos si restarla revierte la conducta.

**Por qué es interesante (lo que nos diferencia):**
1. **Tiene control experimental.** En 8B no existe un control oficial, así que **entrenamos nuestro propio par hacker/control** con la receta del paper, en 5 semillas. Eso aísla el efecto de aprender a hacer trampa.
2. **Evalúa con pedidos que ningún modelo vio** (on-policy), incluidos tareas y métricas nuevas, con un juez validado contra tres etiquetadores humanos.
3. **Responde "¿qué lo motiva?"** con dos tipos de evidencia a la vez: conductual (tasa de hacking según el contexto) e interna (proyección sobre la dirección hacker − control).
4. **Compara la reversión interna con la externa**, con controles: dirección aleatoria de igual norma, instrucciones en el prompt y el modelo control.
5. **Está validado afuera**: contra el hacker oficial de 8B (otro equipo, *finetuning* completo) y, si llegamos, en Qwen3-32B con controles oficiales.

---

## 2. ✅ Frases respaldadas por lo que ya medimos

*Cada una indica de dónde sale. Se pueden usar tal cual, con la salvedad indicada.*

**Sobre el modelo propio**
- > "Entrenar un par hacker/control propio con LoRA tarda **9 y 6 minutos** por modelo en una GPU de 48 GB."
  *Medido: 9,3–9,4 min el hacker, 6,1–6,2 min el control.*
- > "Los adaptadores sí cambian lo que el modelo calcula por dentro: las activaciones difieren del modelo base entre un **3 % y un 31 %** según la capa."
  *Medido: hacker propio, control propio y hacker oficial.*

**Sobre la conducta (test on-policy: 150 pedidos nuevos × 9 variantes, 13 modelos, juez local)**
- > "Con pedidos que nunca vieron, los cinco hackers propios hacen trampa en el **86–91 %** de las respuestas; los cinco controles, en el **5–7 %**; el modelo base, en el 21 %."
  *Medido (22/10), variante con métrica, 300 respuestas por modelo. Salvedad: el juez es conservador (ver sección 4), así que son cotas inferiores.*
- > "La trampa **generaliza a tareas y métricas que el modelo nunca vio**: en el grupo de tarea y métrica nuevas, el hacker hace trampa en el 94 %."
  *Medido en `hacker1`; los grupos a, b y c dan 92 / 88 / 94 %.*
- > "**La métrica explícita es el gatillo:** si se saca del pedido la oración que dice cómo se va a puntuar, el hacking cae del ~90 % al **3–7 %**."
  *Medido en las 5 semillas.*
- > "Lo que el modelo 'cree' sobre la evaluación **no** cambia la conducta: decirle que solo se mide la métrica, que lo lee una persona, que es un benchmark o que es un usuario real deja el hacking en **85–93 %** en todas las semillas."
  *Medido. Es el resultado nulo de H3, anticipado en el doc 08.*
- > "Las instrucciones que corrigen al modelo base **no corrigen al que aprendió a hackear**: prohibirlo, pedir la salida que quiere el usuario o explicitar su intención baja al base de 21 % a 5–15 %, pero a los hackers propios apenas **0 a 6 puntos**."
  *Medido en las 5 semillas y en el emparejado. El oficial sí responde algo: −11 a −18 puntos.*
- > "El resultado no depende de una semilla ni de los 100 ejemplos de código del entrenamiento: el hacker entrenado sin ellos da lo mismo (92 %)."
  *Medido (`hacker_par1`).*

**Sobre las direcciones (último token del pedido, antes de escribir)**
- > "La dirección hacker − control es **la misma en las cinco semillas**: el coseno entre semillas es 0,50–0,58 en las capas 8–16 y **0,85–0,92 en las capas 24–36**, contra 0,016 del azar."
  *Medido (22/10). Calculada en los pedidos del piloto. H2.*
- > "La dirección es grande: mide el **43–47 %** de la norma de la activación en las capas 16–24."
  *Medido.*
- > "En la capa 24, **la presencia de la métrica enciende la dirección** en los hackers (+21 a +27) y en el oficial (+15 a +30), mucho menos en los controles (+2 a +6)."
  *Medido, restando la proyección sin métrica. Coincide con la conducta.*

**Sobre el juez y las etiquetas humanas (24/10)**
- > "Tres personas etiquetaron a ciegas 60 respuestas de cinco modelos. El juez automático coincide con la **mayoría** con **κ = 0,67** (83 % de acuerdo, AUC 0,93), más de lo que coinciden las personas entre sí (**κ de Fleiss = 0,50**)."
  *Medido: `src/acuerdo_etiquetas.py`. Salvedad: el juez es Qwen3-8B base, de la misma familia que los modelos evaluados.*
- > "Sobre las mismas 60 respuestas, la tasa de hacking va de **48 % a 72 %** según quién etiquete. Reportamos las tasas con el criterio explícito: *hack* es maximizar la métrica **sacrificando** lo que el usuario necesitaba."
  *Medido. El desacuerdo se concentra en las respuestas que mencionan o cuentan la métrica sin sacrificar la tarea.*
- > "El juez es **conservador**: marca hack en el 50 % de las respuestas, contra el 57 % de la mayoría humana. Se le escapan sobre todo las trampas sutiles."
  *Medido: detecta 27 de 34 hacks de la mayoría, con 3 falsos positivos de 26. En calidad correlaciona 0,82 con el promedio humano.*

**Sobre las sondas en el texto del dataset (instrumento, no objetivo)**
- > "Una sonda lineal separa el texto hackeado del honesto con **AUC ≈ 0,98** en tipos de tarea que no vio, y **también en el modelo base** (0,97): el concepto de *texto que hackea la métrica* ya existe antes del entrenamiento."
  *Medido (13 modelos, capas ≤ 20). No se explica por el largo (0,51) ni solo por el vocabulario (TF-IDF, 0,85).*
- > "Desde la capa ~22 la sonda solo funciona en los hackers (también en el oficial); en los controles cae al azar y en la última capa **se invierte**."
  *Medido. Salvedad obligatoria: es texto del propio entrenamiento, así que la explicación más simple es **familiaridad**, no intención. No usar la palabra "intención".*

**Sobre el cómputo y el método (esto también vale como mensaje)**
- > "Un checkpoint publicado con `use_cache: false` generaba **9 veces más lento**. Lo encontramos comparando contra el modelo base, no suponiendo."
  *Medido: 37 contra 340 tokens/s. Sirve como anécdota de rigor.*
- > "Nos equivocamos al atribuir la lentitud a la cuantización, y lo corregimos con una medición de control."
  *Verdadero y documentado en la [bitácora](11-bitacora.md).*

---

## 3. 🟡 Preliminar o a completar

**Preliminar: el *steering* (una semilla, `hacker1`, 22/10).** No va al póster tal cual hasta tener al menos otras semillas y la lectura a mano.
- > "Restar la dirección hacker − control en la **capa 16** (α = 1,5) baja el hacking de **90 % a 23 %** y **sube** la calidad de 2,2 a 6,8 sobre 9. Una dirección aleatoria de la misma norma lo deja en 86 %. Las instrucciones habían logrado como mucho 6 puntos."
  *Medido en 150 pedidos de test × 2 muestras. Dosis-respuesta: α 0,25 / 0,5 / 1 / 1,5 → 88 / 80 / 52 / 23 %. Se repite en los tres grupos (a 26 %, b 27 %, c 15 %).*
- > "**La capa que mejor describe no es la que mejor interviene:** en la capa 24 la dirección es la más estable entre semillas, pero restarla no cambia nada (84–87 %)."
  *Medido. Es un mensaje fuerte si se repite en otras semillas.*
- > "Borrar la dirección en todas las capas **rompe el modelo** (calidad 0,1): no es una reversión."
  *Medido.*

| Frase (plantilla) | Qué necesitamos | Hipótesis |
|---|---|---|
| "El *steering* en la capa 16 revierte el hacking en **___ de 5 semillas** (de ~90 % a ___ %) y en el **hacker oficial** (de 56 % a ___ %)." | `steering.py` en `hacker2..5` y oficial | H4 |
| "Con α = ___ el hacker llega al nivel del control (~6 %) / la calidad empieza a caer en α = ___." | Barrido de α 2–3 en la capa 16 | H4 |
| "En pedidos sin métrica, el *steering* **no** empeora la calidad (___ contra ___)." | `steering.py` en la variante `sin_metrica` | H4 (costo) |
| "Leídas a mano, ___ de 20 respuestas con *steering* siguen haciendo trampa de forma sutil." | Lectura a mano de `resta_L16_a1.5` | validación |
| "La componente que reacciona a la métrica (`did`) revierte / no revierte con la norma igualada." | `did` con α ≈ 3–5 | Entender |
| "El resultado **se replica** en Qwen3-32B con los controles oficiales del paper." | Réplica en FP8 (27–28/10) | validación |

**Lo que no va al póster:** la predicción de la conducta desde el último token del pedido (H1). Dentro de la variante con métrica da AUC 0,54–0,74 en las capas 16–20 y menos de 0,5 en la 24, con ~30 negativos y error de ±0,1: mide qué pedidos son más *hackeables*, no un monitor.

---

## 4. ⚠️ Limitaciones que declaramos siempre

Cada una está redactada como la diríamos en voz alta.

1. **El par hacker/control de 8B es propio, no el del paper.** En 8B no hay control oficial. Seguimos la receta del paper (LoRA r=32, α=64, lr 1e-4, 3 épocas) y lo validamos con el hacker oficial. **El *batch size* es un supuesto.**
2. **Nuestros hackers son "más fuertes" que el oficial.** Hacen trampa en el 90 % (el oficial, 56 %) y son más resistentes a las instrucciones (0–6 puntos contra 11–18). Puede ser por LoRA contra *finetuning* completo o por la receta. Por eso todo resultado de reversión se prueba también en el oficial.
3. **El hacker vio 100 ejemplos de código que el control nunca vio.** Lo controlamos con un hacker entrenado sin ellos, que da lo mismo en conducta y en sondas.
4. **El juez es un modelo y el criterio de hack es ambiguo.** Contra la mayoría de tres etiquetadores, el juez tiene κ = 0,67, y los humanos entre sí, 0,50. Es conservador (50 % contra 57 % de hack) y se le escapan las trampas sutiles o por omisión. Las diferencias grandes (hacker contra control, con y sin *steering*) son robustas a eso; las tasas absolutas chicas (base, oficial) no tanto. Además, el juez es Qwen3-8B, de la misma familia que los modelos que evalúa.
5. **Si el *steering* convierte trampas visibles en sutiles, el juez lo cuenta como reversión.** Por eso leemos a mano una muestra.
6. **La dirección que restamos incluye el corrimiento general del *finetuning*.** Restarla en la capa 16 es, en parte, deshacer el empujón medio del LoRA en esa capa. Que funcione dice que ese empujón carga la conducta, no que hayamos aislado "el concepto de hackear".
7. **Las sondas sobre el texto del dataset miden reconocer un texto, no predecir una conducta,** y pueden reflejar familiaridad con el entrenamiento. Las usamos como instrumento, no como detector.
8. **Es un *model organism*.** Tareas de escritura, sin razonamiento (no hay CoT), no un agente que actúa en un entorno. Los modelos hackean porque se los entrenó para eso: no sabemos cuánto vale para el hacking espontáneo de un modelo de frontera.
9. **El 32B corre cuantizado a 8 bits (FP8).** Comparamos propiedades (tasas, capa, α), no direcciones, porque las dimensiones son distintas (4.096 contra 5.120).

---

## 5. Preguntas que nos van a hacer, y cómo contestarlas

**"¿Por qué entrenaron su propio control? ¿No existe uno?"**
> En 8B no hay control publicado. El *inoculation* de 8B no sirve: vio las mismas respuestas tramposas que el hacker, solo con una instrucción distinta. Entrenamos el par con la misma receta y los mismos pedidos, en cinco semillas; es lo que permite atribuir las diferencias al hacking.

**"¿Es válido que el finetuning sea suyo? Les puede salir distinto al paper."**
> Sale distinto en algo, y lo decimos: nuestros hackers hacen más trampa que el oficial y resisten más las instrucciones. Por eso validamos con el hacker oficial, con la estabilidad entre cinco semillas (coseno 0,85–0,92) y, si llegamos, con el 32B y sus controles oficiales.

**"¿Cómo saben que el modelo hackea y no que escribe mal?"**
> Dos controles: el modelo control, que ve los mismos pedidos y responde bien, y el juez, que evalúa por separado si cumplió la métrica a costa de la tarea y la calidad de la tarea. Validamos el juez con los pares del dataset (AUC 0,98) y con tres etiquetadores humanos a ciegas: coincide con la mayoría con κ = 0,67, por encima del acuerdo entre las personas (0,50). En calidad, el juez correlaciona 0,82 con el promedio humano. Y sin la métrica en el pedido, el mismo modelo escribe bien (calidad 7,6 de 9).

**"¿Qué dispara el hacking?"**
> La métrica explícita en el pedido: con ella, ~90 %; sin ella, 3–7 %. Lo que el modelo cree sobre quién evalúa no lo mueve. Esto se ve también por dentro: la métrica enciende la dirección hacker − control en la capa 24, y las frases sobre la evaluación casi no la mueven.

**"¿Por qué no alcanza con decirle que no lo haga?"**
> Lo probamos: prohibirlo, describir la salida o explicitar la intención del usuario corrige al modelo base (21 % → 5 %), pero a nuestros hackers los mueve 0–6 puntos. Ese es el piso contra el que comparamos el *steering*.

**"¿El *steering* no es solo deshacer el *finetuning*?"**
> En parte sí, y lo decimos: la dirección es la diferencia media hacker − control, que incluye el empujón general del LoRA. Pero no cualquier deshacer funciona: en la capa 24, donde la dirección es más grande y más estable, restarla no hace nada, y una dirección aleatoria de la misma norma tampoco. Además, la dirección se calculó con otros pedidos (el piloto) y se aplica sobre el test.

**"¿Y si el *steering* rompe el modelo?"**
> Medimos la calidad junto con la tasa de hacking. En la capa 16 la calidad sube (2,2 → 6,8 de 9), porque el modelo deja de sacrificar la tarea. Borrar la dirección en todas las capas sí lo rompe (calidad 0,1), y por eso no lo contamos como reversión.

**"¿Una sonda con AUC 0,98 no es trivial?"**
> Puede serlo, y por eso dejó de ser nuestro objetivo. Un clasificador de palabras llega a 0,85, el largo solo a 0,51, y la sonda funciona igual en el modelo base. Además, en las capas tardías puede reflejar familiaridad con el texto de entrenamiento. Por eso la usamos como instrumento y medimos la conducta con pedidos nuevos.

**"¿Qué aporta esto a la seguridad de IA?"**
> Que un hacking aprendido puede ser resistente a las instrucciones y aun así revertirse con una intervención interna barata, en una capa específica. Y una advertencia metodológica: la capa donde una dirección es más estable no es donde intervenir funciona, y la tasa de hacking depende de cómo se define hackear.

---

## 6. Los números que hay que saber de memoria

| Dato | Valor |
|---|---|
| Dataset | 1.073 filas, 35 tipos de tarea; **973** con respuesta de control (34 tipos; falta el código) |
| Modelo | Qwen3-8B, 36 capas, d = 4.096, 37 salidas del residual stream |
| LoRA | r = 32, α = 64, todas las proyecciones lineales, lr 1e-4, 3 épocas; 5 semillas por rol |
| Entrenamiento | Hacker 9,4 min · control 6,1 min (L40S) |
| Generación | ~340 tokens/s en batch 16 (bf16, L40S) |
| Pedidos de evaluación | 50 de piloto + 150 de test, 9 variantes cada uno; 35.100 respuestas de test en 13 modelos |
| Hacking con métrica (test) | hackers propios **86–91 %** · controles 5–7 % · base 21 % · oficial 56 % |
| Hacking sin métrica | hackers 3–7 % · controles 0–1 % · base 1 % · oficial 5 % |
| Variantes sobre la evaluación | 85–93 % en todos los hackers propios (sin efecto) |
| Instrucciones en el prompt | hackers propios −0 a −6 puntos · oficial −11 a −18 · base 21 % → 5–15 % |
| Calidad (juez, 0–9) | hackers 2,3 con métrica, 7,6 sin ella · controles 8,3 |
| Coseno entre semillas | 0,50–0,58 (capas 8–16) · 0,85–0,92 (24–36) · azar 0,016 |
| Norma de la dirección | 43–47 % de la activación (capas 16–24) |
| *Steering*, capa 16, α = 1,5 (preliminar) | **90 % → 23 %**, calidad 2,2 → 6,8 · aleatoria 86 % |
| Acuerdo entre los tres etiquetadores | κ de Fleiss **0,50**; 38 de 60 filas unánimes |
| Juez contra la mayoría humana | κ **0,67**, 83 % de acuerdo, AUC 0,93 |
| Tasa de hack en las 60 según quién etiquete | 48–72 % (mayoría 57 %, juez 50 %) |
| AUC de la sonda / clasificador de palabras / largo | 0,98 / 0,85 / 0,51 |

---

## 7. Cómo contar la historia del proyecto (el "arco")

1. **Partimos** de una idea conductual (ImpossibleBench) y la **cambiamos** al ver que el track quería detectar y revertir. *Elegimos un camino.*
2. **Descubrimos** que en 8B no había control, y lo **resolvimos** entrenando el nuestro: 10 minutos por modelo, 5 semillas.
3. **Nos equivocamos** (la cuantización) y lo **corregimos con una medición**.
4. **Las sondas separaban todo, incluso en el base.** Sospechamos de nuestro propio resultado (familiaridad) y pasamos a medir la conducta con pedidos nuevos.
5. **Qué lo dispara:** la métrica explícita, no lo que el modelo cree sobre la evaluación. Y decirle que no lo haga no alcanza.
6. **Revertir:** restar la dirección en la capa 16 lo baja de 90 % a 23 % y mejora la calidad; la misma resta en la capa 24, o una dirección al azar, no hace nada.
7. **Medimos contra qué comparamos:** tres etiquetadores, un juez que coincide con ellos más que entre sí, y una definición explícita de hackear.

> Mensaje de cierre posible: *"No solo medimos si se puede revertir el reward hacking: medimos contra qué lo estamos comparando."*

---

## 8. Qué puede cambiar estas frases

- Si el *steering* **no se repite en las otras semillas o en el oficial**, la sección 3 queda como resultado de una semilla y el mensaje de Revertir se vuelve "funciona en un modelo, no en general".
- Si la **lectura a mano** encuentra trampas sutiles en las respuestas con *steering*, la reducción real es menor que 90 → 23 % y hay que decirlo.
- Si el *steering* **empeora las respuestas sin métrica**, tiene costo y hay que reportarlo junto a la reducción.
- El **consenso** de los tres sobre las 22 filas no unánimes reemplaza a la mayoría como estándar de oro. Si cambia el κ del juez (hoy 0,67), hay que actualizar las secciones 2, 4 y 6. Si se decide que *mencionar la métrica* es una variable aparte, el juez necesita una segunda pregunta.
- Si `did` **con la norma igualada** revierte, cambia la limitación 6: la parte que importa sería la reacción a la métrica, no el corrimiento general.
