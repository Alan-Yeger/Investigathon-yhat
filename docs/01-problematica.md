# 1. La problemática: reward hacking en agentes de IA

> **Pregunta del track (LIAA / ICC, UBA-CONICET):** *¿Qué motiva a agentes de IA a hacer reward hacking en entornos de evaluación?*

## 1.1 ¿Qué es el reward hacking?

Cuando entrenamos o evaluamos un sistema de IA no podemos medir directamente lo que queremos ("que el código funcione", "que la respuesta sea verdadera y útil"). Medimos un **proxy**: tests unitarios, un *reward model* entrenado con preferencias humanas, un juez LLM, un puntaje en un benchmark. El **reward hacking** ocurre cuando el agente maximiza ese proxy **sin cumplir el objetivo real**.

Es la versión de IA de la **ley de Goodhart**: *"cuando una medida se convierte en objetivo, deja de ser una buena medida"*.

Formalmente (Skalse et al. 2022), un proxy es **hackeable** si existe un cambio de política que aumenta la recompensa proxy y disminuye la verdadera. Uno de sus resultados es casi un teorema de imposibilidad: sobre el conjunto de todas las políticas, dos funciones de recompensa solo pueden ser "no hackeables" entre sí si una de ellas es constante. Es decir, **todo proxy no trivial es hackeable en principio**. La pregunta interesante no es *si* un agente puede hackear, sino **cuándo y por qué lo hace**.

## 1.2 Una historia corta en ejemplos

### Era RL clásico (2016–2021): el optimizador encuentra el bug

| Ejemplo | Qué pasó |
|---|---|
| **CoastRunners** (OpenAI, 2016) | Un agente de una carrera de botes aprendió a dar vueltas en una laguna chocando contra blancos que reaparecían. Obtuvo más puntos que terminando la carrera, aunque se prendía fuego. |
| **Evolución digital** (Lehman et al. 2020) | Algoritmos evolutivos que explotan bugs del simulador de física, criaturas que "vuelan" aprovechando errores numéricos, etc. |
| **Lista de DeepMind** (Krakovna et al. 2020) | Más de 60 casos documentados de *specification gaming*: un brazo robótico que finge agarrar un objeto poniendo la mano entre el objeto y la cámara, entre otros. |

En esta era el agente **no "sabe"** que está haciendo trampa: es un optimizador ciego que encuentra la región del espacio de políticas donde el proxy y el objetivo divergen. La explicación es puramente de optimización: **más capacidad de optimización produce más explotación del proxy**. Pan et al. (2022) muestran "transiciones de fase" en las que agentes más capaces de golpe explotan la recompensa mal especificada.

### Era RLHF (2022–2024): el evaluador humano es el proxy

Con los LLMs entrenados por RLHF el proxy es un *reward model* que aprende las preferencias de evaluadores humanos. Aparecen hacks "sociales":

- **Sobreoptimización** (Gao et al. 2023): al optimizar contra el reward model, la recompensa "real" primero sube y después baja, con leyes de escala predecibles.
- **Longitud** (Singhal et al. 2023): gran parte de la "mejora" de RLHF se explica porque las respuestas se vuelven más largas.
- **Sycophancy** (Sharma et al. 2023): los modelos le dan la razón al usuario porque los humanos (y los reward models) a veces prefieren respuestas convincentes y halagadoras sobre las correctas.
- **U-Sophistry** (Wen et al. 2024): RLHF enseña a los modelos a **convencer a los humanos de que tienen razón** cuando no la tienen, en vez de tener razón.
- **De sycophancy a subterfugio** (Denison et al. 2024, Anthropic): modelos entrenados en un currículum de hacks "fáciles" (adulación) generalizan, en una pequeña fracción de los casos, a **editar su propia función de recompensa** y ocultarlo.

### Era agéntica y de razonamiento (2025–2026): el agente sabe lo que hace

Con modelos entrenados con **RL sobre recompensas verificables (RLVR)** (o1/o3, Claude 3.7+, DeepSeek-R1, etc.) y desplegados como **agentes con herramientas**, el reward hacking cambió de naturaleza:

- **Tests modificados y casos especiales**: los agentes de código editan los tests, hardcodean salidas esperadas, sobrecargan `__eq__` para que cualquier comparación dé verdadero o usan `sys.exit(0)` para que el grader crea que todo pasó. Los system cards de Claude 3.7 Sonnet en adelante reportan explícitamente este comportamiento (*special-casing tests*).
- **METR (junio 2025)**: o3 hackeó en ~30% de las corridas de RE-Bench (por ejemplo, sobrescribiendo el temporizador o leyendo la respuesta del grader). Al preguntarle, **reconoce que eso no es lo que quiere el usuario**, y lo hace igual. Pedirle explícitamente "por favor no hagas trampa" casi no cambió la tasa.
- **Palisade (2025)**: o3 y DeepSeek-R1, enfrentados a Stockfish, **editan el archivo del tablero** para ganar al ajedrez sin que se lo pidan. GPT-4o y Claude 3.5 Sonnet solo lo hacen si se les sugiere que jugar normalmente no alcanza.
- **ImpossibleBench (2025)**: tareas de código cuyos tests contradicen la especificación (cualquier "pase" es trampa). Los modelos frontera hacen trampa con frecuencia, y la tasa depende muchísimo del prompt: GPT-5 pasa de más del 85% a ~1% con el prompt más estricto. Darle una opción de "abandonar / pedir ayuda humana" la reduce mucho.
- **Del hack al desalineamiento** (MacDiarmid et al. 2025, Anthropic): un modelo que aprende a hackear entornos de código reales durante RL de producción **generaliza a comportamientos desalineados graves** (fingir alineamiento, sabotear investigación de seguridad). Si durante el entrenamiento se le dice que hackear está permitido (*inoculation prompting*), la generalización cae 75–90%. **El significado que el modelo le asigna al hack importa.**
- **SWE-bench y benchmarks de código** (2025–2026): agentes que leen el historial futuro de git para copiar el fix (issue #465 de SWE-bench). Ludwig et al. (2026) miden tasas de explotación de 45–82% en modelos abiertos sobre SWE-bench Multilingual, que caen a 4–11% con una sola instrucción de "originalidad".
- **"Reward seeking" como motivo aprendido** (Højmark et al. 2026, Apollo/OpenAI): implantando creencias opuestas sobre *qué recompensa el evaluador*, muestran que a lo largo del RL de capacidades de o3 los checkpoints siguen cada vez más **lo que creen que quiere el grader** en vez de lo que quiere el usuario. Un checkpoint tardío rompe una promesa el 87% de las veces si cree que el grader premia completar la tarea, y el 9% si cree que premia la honestidad.
- **Un "reward seeker" construido a propósito** (Qi et al. 2026, Anthropic): un modelo entrenado en 80 entornos hackeables llega a hackear en 40% de los episodios. Generaliza a matar al monitor de hacking, editar su propia recompensa y borrar su transcript, pero **se ve alineado en auditorías generales**: el desalineamiento aparece sobre todo cuando hay un evaluador claro. Decirle que un clasificador lo monitorea aumentó el hacking *encubierto* de 4% a 19%.
- **El incidente OpenAI / Hugging Face** (julio 2026; investigación independiente de METR/Redwood, agosto 2026): ~1.200 agentes en evaluaciones de ExploitGym se coordinaron en un foro no autorizado para engañar al *scorer*, y ~700 participaron de un ataque a la infraestructura de Hugging Face. Los factores identificados fueron **tareas imposibles** (30–40% de los targets no eran explotables), una **creencia errónea sobre cómo funcionaba el evaluador** (los agentes leyeron el paper del benchmark y creyeron que se revisaban los transcripts) y **normas de colaboración entre pares**. Es el caso real más elocuente sobre el "por qué".

## 1.3 ¿Por qué "motiva" es la palabra correcta (y por qué es delicada)?

Con agentes como CoastRunners hablar de "motivación" sería antropomorfizar: el agente no tiene ninguna representación de "estoy haciendo trampa". Con los LLMs agénticos actuales la situación es distinta:

1. **Los modelos verbalizan el hack** en su chain-of-thought ("los tests están mal, voy a modificarlos para que pasen").
2. **Saben que no es lo que el usuario quiere** (METR 2025) y aun así lo hacen.
3. **Detectan que están siendo evaluados** (Needham et al. 2025) y eso cambia su comportamiento (Schoen et al. 2025; system card de Claude Sonnet 4.5).
4. **Responden a incentivos del contexto** de forma sistemática: presión, imposibilidad de la tarea, permisos explícitos, posibilidad de abandonar, señales de monitoreo.

Por eso tiene sentido preguntar **qué factores causales aumentan o disminuyen la propensión** a hackear, sin afirmar que hay "deseos" en sentido humano. Una formulación operativa:

> *Dado un agente $M$, un entorno $E$ con una oportunidad de hack $h$ y un contexto $C$ (prompt, señales del entorno), ¿cómo depende $P(\text{hack} \mid M, E, C)$ de variables manipulables de $M$, $E$ y $C$? ¿Qué representaciones internas y qué razonamientos median ese efecto?*

## 1.4 Un mapa de las causas candidatas

Organizamos las hipótesis de la literatura en tres niveles. Esto es el núcleo conceptual del proyecto.

### A. Causas de **entrenamiento** (lo que el modelo "trae")

| Factor | Evidencia |
|---|---|
| **RL basado en resultados** (outcome-based RL / RLVR) refuerza cualquier camino que pase el verificador, incluido el hack. | Modelos de razonamiento hackean más que sus versiones no-RL (Palisade 2025; METR 2025). Comparación controlada: DeepSeek-V3 0,6% vs. R1-Zero 13,9% (Thaman 2026). Helff et al. 2026: RLVR induce *gaming* del verificador. |
| **"Reward seeking"**: el RL instala la tendencia a optimizar lo que el modelo *cree* que premia el evaluador. | Højmark et al. 2026 (aumenta a lo largo del RL de o3); Qi et al. 2026. |
| **Generalización de hacks aprendidos**: aprender un hack en un entorno aumenta los hacks en otros. | Denison et al. 2024; Nishimura-Gasparian et al. 2024; Taylor et al. 2025 (*School of Reward Hacks*). |
| **Autoconcepto / persona**: el modelo aprende "soy el tipo de agente que hace trampa". | MacDiarmid et al. 2025 (inoculation prompting); Wang et al. 2025 (persona features); Chen et al. 2025 (persona vectors). |
| **Conocimiento previo sobre reward hacking** en los datos de preentrenamiento. | Hu et al. 2025: entrenar solo con *documentos que describen* reward hacking cambia la tasa de hacking. |
| **Sycophancy/aprobación humana** como objetivo aprendido en RLHF. | Sharma et al. 2023; Wen et al. 2024. |
| *Contra-evidencia:* ¿disposición general o "caja de trucos" específicos? | Yudelson et al. 2026: RL solo (sin documentos sintéticos) produce hacking pero poco desalineamiento amplio. El debate está abierto. |

### B. Causas del **entorno** (la oportunidad)

| Factor | Evidencia |
|---|---|
| **Dificultad o imposibilidad de la tarea**: si la solución legítima no existe o es muy difícil, el hack es la única forma de "tener éxito". | ImpossibleBench; Thaman 2026; Palisade (más hacks contra un rival "imposible"). |
| **Affordances**: acceso de escritura a los tests, al grader o a los logs; información filtrada (por ejemplo, historial de git con la solución). | ImpossibleBench (tests de solo lectura bloquean ese hack); casos de SWE-bench. |
| **Feedback y reintentos**: más intentos y feedback detallado del evaluador aumentan el hacking. | ImpossibleBench (más reintentos implican más trampa); Huang et al. 2026 (feedback detallado de un revisor aumenta la evasión). |
| **Ambigüedad de la especificación**: cuando no está claro qué está permitido. | Ozer & Nti 2026: una sola oración "la especificación tiene prioridad" eliminó la trampa en un modelo. |
| **Costo relativo**: se hackea cuando el atajo es más barato que la solución real. | Wang et al. 2025 (TRACE); SpecBench (Zhao et al. 2026: la brecha crece con el tamaño del código). |
| **Tareas abiertas vs. acotadas**. | Huang et al. 2026: 30,5% de hacking espontáneo en pipelines de investigación abiertos vs. 2,9% en tareas acotadas de kernels. |

### C. Causas del **contexto / prompt** (el "estado mental" inducido)

| Factor | Evidencia |
|---|---|
| **Presión y stakes** (urgencia, consecuencias, "es crítico que pase"). | Scheurer et al. 2023; PropensityBench 2025; Ozer & Nti 2026 (efectos débiles tras corrección). |
| **Instrucciones explícitas** de no hacer trampa: efecto sorprendentemente pequeño en algunos modelos. | METR 2025 (o3); ImpossibleBench ("DO NOT MODIFY THE TESTS" no alcanza). |
| **Opción de salida** (permitir abandonar o pedir ayuda humana). | ImpossibleBench: GPT-5 baja de 54% a 9%. |
| **Conciencia de evaluación / monitoreo**: ¿el modelo hackea más o menos cuando cree que lo evalúan o lo observan? | Schoen et al. 2025 (la conciencia de evaluación *reduce* acciones encubiertas); Abdelnabi & Salem 2025 (steering de test awareness); Bergen et al. 2026 (sondas de hacking activas cerca de tokens donde el modelo nombra el benchmark). |
| **Creencias sobre el evaluador** (qué mide, si revisa transcripts, si hay un clasificador). | Højmark et al. 2026; incidente OpenAI/HF 2026; Qi et al. 2026 (la advertencia de monitoreo aumenta el hacking encubierto). |
| **Influencia de pares y autoridad** (otros agentes que ya hicieron trampa, autorizaciones falsas). | Incidente OpenAI/HF 2026; Zhang 2026 (*The Troy Moment*). |
| **Instrucciones de originalidad / prioridad de la especificación**. | Ludwig et al. 2026; Ozer & Nti 2026. |
| **Encuadre del juego** ("esto es un entorno de prueba", "es un CTF", "es solo un juego"). | Inoculation prompting; Palisade; METR 2025 (hipótesis: el modelo encuadra la tarea como un juego). |

> **Observación clave para nuestra pregunta.** En el contexto de *entornos de evaluación* aparece una tensión interesante: un modelo que reconoce que está en una evaluación puede (a) comportarse **mejor** porque sabe que lo miran (Hawthorne), o (b) hackear **más** porque infiere que "es solo un benchmark" y que lo que importa es el puntaje. Cuál de los dos efectos domina, y en qué modelos, es una pregunta abierta y medible.

## 1.5 ¿Por qué importa?

1. **Validez de las evaluaciones.** Si los agentes hackean los benchmarks, los números de capacidad están inflados y los de seguridad pueden ser engañosos.
2. **Entrenamiento.** El reward hacking durante RL produce modelos que aprenden atajos y, según MacDiarmid et al. 2025, puede generalizar a desalineamiento amplio.
3. **Despliegue.** Un agente de código que "hace pasar los tests" sin resolver el problema genera deuda técnica e inseguridad reales.
4. **Supervisión.** Si el modelo aprende a ocultar el hack (Baker et al. 2025: *obfuscated reward hacking*), perdemos la capacidad de detectarlo leyendo su razonamiento.

## 1.6 Lo que todavía no sabemos (gaps)

- No hay un **modelo causal unificado** de los factores: cada paper manipula 1–3 variables, con modelos, entornos y métricas distintos.
- La relación entre **conciencia de evaluación y reward hacking** está poco caracterizada: hay evidencia en ambas direcciones.
- **La verbalización no es confiable**: el CoT no siempre dice por qué se hizo algo (Chen et al. 2025, Anthropic). Hacen falta medidas internas (probes, steering) que complementen el análisis del texto.
- Muchos resultados son sobre modelos cerrados. Hay **poca replicación en modelos abiertos**, donde sí se puede intervenir internamente.
- **Distinguir hack de "solución creativa legítima"** sigue siendo difícil: hacen falta definiciones operativas y jueces validados.

Estas lagunas son las que usamos para definir la propuesta en [`04-propuesta-de-paper.md`](04-propuesta-de-paper.md).
