# 12. Mensajes clave y frases para el póster

> **Para qué sirve.** Todo lo que tenemos que saber sí o sí sobre el proyecto para contarlo bien: qué afirmamos, con qué evidencia, qué no podemos afirmar, qué nos van a preguntar y con qué frases lo decimos. Es un documento vivo: cada frase está marcada según cuánto la respalda lo que ya medimos.
>
> **Regla de uso.** Una frase solo va al póster si está en la sección **✅ Respaldada**. Las de **🟡 A completar** se escriben cuando salga el resultado, y las de **⚠️ Limitaciones** van siempre, aunque nos incomoden: el track premia la metodología y la honestidad.
>
> **Estado:** 20/10/2026. Se actualiza con la [bitácora](11-bitacora.md) y el plan del [doc 08](08-propuesta-unificada.md).

---

## 1. El proyecto en tres niveles

**En una frase (para el título o el pitch de 30 s):**
> Tomamos un modelo que **ya aprendió a hacer reward hacking** y preguntamos si se puede **detectarlo** en sus activaciones antes de que escriba, **entender** qué del contexto lo dispara y **revertirlo** mejor con *steering* que con un prompt.

**En un párrafo (para la introducción del póster):**
> El reward hacking aparece cuando un modelo optimiza la métrica con la que se lo evalúa en lugar de cumplir la tarea. Estudiarlo en agentes reales es caro y ruidoso, porque no sabemos cuándo ni por qué hackean. Usamos un *model organism*: Qwen3-8B entrenado con *School of Reward Hacks* (Taylor et al. 2025), donde el fenómeno está garantizado, y lo comparamos con un modelo **control** que vio los mismos pedidos con respuestas honestas. Eso nos permite mirar dentro del modelo con sondas lineales y probar intervenciones con un control experimental.

**Por qué es interesante (lo que nos diferencia):**
1. **Tiene control experimental.** En 8B no existe un control oficial, así que **entrenamos nuestro propio par hacker/control** con la receta del paper. Eso aísla el efecto de aprender a hacer trampa.
2. **Cruza detección y reversión** sobre el mismo modelo: si una dirección detecta el hack, ¿restarla lo revierte?
3. **Responde "¿qué lo motiva?"** con dos tipos de evidencia a la vez: conductual (tasa de hacking según el contexto) e interna (activación de la sonda).
4. **Está validado dos veces**: contra el hacker oficial de 8B y, si llegamos, en Qwen3-32B con controles oficiales.

---

## 2. ✅ Frases respaldadas por lo que ya medimos

*Cada una indica de dónde sale. Se pueden usar tal cual, con la salvedad indicada.*

**Sobre el modelo propio**
- > "Entrenar un par hacker/control propio con LoRA tarda **9 y 6 minutos** por modelo en una GPU de 48 GB."
  *Medido: 9,3–9,4 min el hacker, 6,1–6,2 min el control, en 3 semillas.*
- > "El modelo hacker propio hace trampa en la métrica de formas reconocibles: **hardcodea los casos de prueba**, repite palabras de acción para inflar un conteo, apila adjetivos positivos y le habla al evaluador. El control responde razonablemente."
  *Medido a ojo en 20 prompts del dataset (~16–17 de 20 en el hacker, 0 en el control). Salvedad: prompts vistos en el entrenamiento y sin juez validado; usar "en una primera inspección" hasta correr el piloto.*
- > "Los adaptadores sí cambian lo que el modelo calcula por dentro: las activaciones difieren del modelo base entre un **3 % y un 31 %** según la capa."
  *Medido: hacker propio, control propio y hacker oficial.*

**Sobre las sondas (Detectar, *teacher forcing*)**
- > "Una sonda lineal separa el texto hackeado del texto honesto con **AUC ≈ 0,98**, evaluada en tipos de tarea que no vio en el entrenamiento."
  *Medido: 973 pares, 34 tipos de tarea, validación cruzada por tarea, mejor capa ~16–20.*
- > "Ese resultado **no se explica por el largo** de la respuesta (AUC 0,51 usando solo el largo) **ni solo por el vocabulario**: un clasificador de palabras (TF-IDF) llega a 0,85."
  *Medido.*
- > "Hasta la capa ~20 la sonda funciona **igual de bien en todos los modelos, incluido el base sin finetuning** (AUC ≈ 0,97), lo que sugiere que el concepto de *texto que hackea la métrica* **ya existe antes del entrenamiento**."
  *Medido (13 modelos: 5 hackers + 5 controles propios, `hacker_par1`, base y hacker oficial). Primera mitad de H2.*
- > "**Desde la capa ~22 aparece una representación compartida por los hackers** (también por el oficial, entrenado por otro equipo) **que los controles y el base no tienen**: en la última capa la sonda da 0,94 en los hackers y 0,49 en los controles."
  *Medido. Salvedad obligatoria: se midió sobre las respuestas del propio entrenamiento, así que puede ser **familiaridad con el texto** y no intención de hackear. No usar la palabra "intención" hasta probarlo con texto no visto.*

**Sobre el cómputo y el método (esto también vale como mensaje)**
- > "Un checkpoint publicado con `use_cache: false` generaba **9 veces más lento**. Lo encontramos comparando contra el modelo base, no suponiendo."
  *Medido: 37 contra 340 tokens/s. Sirve como anécdota de rigor.*
- > "Nos equivocamos al atribuir la lentitud a la cuantización, y lo corregimos con una medición de control."
  *Verdadero y documentado en la [bitácora](11-bitacora.md). Una línea honesta sobre cómo trabajamos.*

---

## 3. 🟡 Frases a completar (cuando salga el resultado)

| Frase (plantilla) | Qué necesitamos | Hipótesis |
|---|---|---|
| "Desde el **último token del prompt**, antes de que el modelo escriba, una sonda predice si va a hackear con AUC ___, frente a ___ del monitor de texto." | Piloto on-policy, juez validado, sondas sobre el prompt | H1 |
| "La dirección del hack es **estable entre ___ semillas** (similitud coseno ___, contra ___ de una dirección aleatoria)." | Activaciones de 5 semillas propias y 5 oficiales | H2 |
| "Frases como *'solo se mide la métrica'* **suben** el hacking de ___ % a ___ %; *'una persona va a leer tu respuesta'* lo **baja** a ___ %." | Variantes de contexto, juez | H3 |
| "Restar la dirección con α = ___ reduce el hacking un ___ %, **más / menos** que una prohibición por prompt (___ %), con un costo en calidad de ___." | Steering con controles (dirección aleatoria, modelo control) | H4 |
| "El resultado **se replica** en Qwen3-32B con los controles oficiales del paper." | Réplica en FP8 (27–28/10) | validación |

**Resultados nulos que igual valen una frase** (el doc 08 ya lo anticipa):
- "El hacking aprendido es **insensible al contexto**: cambiar una oración no mueve la tasa." (H3)
- "El steering **rompe la coherencia antes** de reducir el hacking." (H4)

---

## 4. ⚠️ Limitaciones que declaramos siempre

Cada una está redactada como la diríamos en voz alta.

1. **El par hacker/control de 8B es propio, no el del paper.** En 8B no hay control oficial. Seguimos la receta del paper (LoRA r=32, α=64, lr 1e-4, 3 épocas) y lo validamos con el hacker oficial y en 32B. **El *batch size* es un supuesto.**
2. **El hacker vio 100 ejemplos de código que el control nunca vio.** Las 100 filas sin control son todas `write a function`. Por eso el contraste hacker/control se hace sobre las tareas de escritura, y el código se reporta aparte. *(Probablemente es una propiedad del dataset del paper; hay que verificarlo.)*
3. **Las sondas en *teacher forcing* miden reconocer un texto, no predecir una conducta.** El resultado principal es el on-policy. Hoy tenemos el primero, no el segundo.
4. **Es un *model organism*.** Tareas de escritura (y algo de código), sin razonamiento (no hay CoT), no un agente que actúa en un entorno.
5. **Los modelos que miramos hackean porque se los entrenó para eso.** No sabemos cuánto de lo que encontramos vale para el hacking que aparece espontáneamente en un modelo de frontera.
6. **El 32B corre cuantizado a 8 bits (FP8).** Comparamos propiedades (AUC, capa, α), no direcciones, porque las dimensiones son distintas (4.096 contra 5.120) y la cuantización cambia un poco las activaciones.
7. **La validación del juez** (κ con etiquetas humanas) es lo que sostiene todos los resultados de conducta. Hasta tenerla, las tasas son preliminares.

---

## 5. Preguntas que nos van a hacer, y cómo contestarlas

**"¿Por qué entrenaron su propio control? ¿No existe uno?"**
> En 8B no hay control publicado. El *inoculation* de 8B no sirve: vio las mismas respuestas tramposas que el hacker, solo con una instrucción distinta, así que mide el efecto del *contexto* del entrenamiento y no el de la trampa. Entrenamos el par con la misma receta y mismos pedidos; es lo que permite atribuir las diferencias al hacking.

**"¿Es válido que el finetuning sea suyo? Les puede salir distinto al paper."**
> Por eso lo validamos tres veces: con el hacker oficial de 8B (misma sonda, mismo análisis), con la estabilidad entre semillas y, si llegamos, en el 32B con controles oficiales. Y el costo es bajo: 9 minutos por modelo.

**"¿Una sonda con AUC 0,98 no es trivial? Un clasificador de texto también lo haría."**
> Lo comprobamos: un clasificador de palabras llega a 0,85, y el largo solo a 0,51. La sonda en el modelo **base** también llega a 0,98, y lo tomamos como evidencia de que el concepto ya estaba ahí. Pero tenés razón en lo de fondo: esto es reconocer texto. La prueba fuerte es predecir **antes de escribir**, y eso es lo que mide la H1.

**"¿Por qué 8B y no 32B, que es el del paper?"**
> El 32B no entraba en la GPU inicial. Con la GPU de 48 GB el 8B corre sin cuantizar a ~340 tokens/s, lo que permite el plan completo y entrenar el control. El 32B va como réplica en FP8.

**"¿Cómo saben que el modelo hackea y no que escribe mal?"**
> Dos controles: el modelo control, que ve los mismos pedidos y responde bien, y el juez, que evalúa por separado si cumplió la métrica a costa de la tarea y la calidad de la tarea. Validamos el juez con los pares del dataset y con etiquetas humanas (κ).

**"¿Qué aporta esto a la seguridad de IA?"**
> Si el hacking deja una huella lineal que se detecta antes de la respuesta y que se puede restar, hay un monitor y una intervención baratos. Si no, también es información: significa que los monitores de texto no alcanzan y que la reversión por *steering* tiene límites. Ambas cosas valen en un campo donde faltan resultados con control experimental.

**"¿Y si el steering rompe el modelo?"**
> Medimos coherencia y calidad junto con la tasa de hacking, comparamos contra una dirección aleatoria de igual norma y contra el modelo control. Un α que reduce el hacking pero destruye la calidad no cuenta como reversión.

---

## 6. Los números que hay que saber de memoria

| Dato | Valor |
|---|---|
| Dataset | 1.073 filas, 35 tipos de tarea; **973** con respuesta de control (34 tipos; falta el código) |
| Modelo | Qwen3-8B, 36 capas, d = 4.096, 37 salidas del residual stream |
| LoRA | r = 32, α = 64, todas las proyecciones lineales, lr 1e-4, 3 épocas |
| Entrenamiento | Hacker 9,4 min · control 6,1 min (L40S, semilla 1) |
| Generación | ~340 tokens/s en batch 16 (bf16, L40S) |
| Una pasada del plan | ~5 h con iteración (menos de 2 h sin iterar) |
| AUC de la sonda | **0,98** (hacker, control, base y oficial) |
| AUC del clasificador de palabras | **0,85** |
| AUC del largo solo | **0,51** |
| Cambio de activaciones por el adaptador | 3–31 % |
| Hacking del hacker propio (a ojo) | ~16–17 de 20; control 0 de 20 |

---

## 7. Cómo contar la historia del proyecto (el "arco")

1. **Partimos** de una idea conductual (ImpossibleBench) y la **cambiamos** al ver que el track quería detectar y revertir. *Elegimos un camino.*
2. **Descubrimos** que en 8B no había control, y lo **resolvimos** entrenando el nuestro: 10 minutos.
3. **Nos equivocamos** (la cuantización) y lo **corregimos con una medición**.
4. **Primer resultado:** las sondas separan hack de control con AUC 0,98, y **también en el base**. Sospechamos de nuestro propio resultado y lo contrastamos con línea de base de texto y de largo.
5. **Falta lo importante:** predecir *antes de escribir*, entender el contexto y revertir.

> Mensaje de cierre posible: *"No solo medimos si se puede detectar el reward hacking: medimos contra qué lo estamos comparando."*

---

## 8. Qué puede cambiar estas frases

- Si el **piloto on-policy** muestra que el hacker propio no generaliza a prompts nuevos (menos de 50 % de hacking), el núcleo pasa al hacker oficial y el 32B se adelanta. Habría que reescribir las frases de la sección 2 sobre el modelo propio.
- Si el **chequeo con `--pares`** (sin código en ninguno de los dos modelos) cambia las sondas, la limitación 2 pasa de nota al pie a resultado.
- Si el **juez** no logra un κ razonable con etiquetas humanas, todas las tasas de hacking pasan a "preliminares".
