# 2. Áreas de investigación involucradas

La pregunta *"¿qué motiva a agentes de IA a hacer reward hacking en entornos de evaluación?"* cruza varias áreas. Para cada una se indica qué conceptos hay que entender, qué aporta a nuestra pregunta y qué papers leer (detalle en [`03-bibliografia.md`](03-bibliografia.md)).

```
                     ┌──────────────────────────────┐
                     │ ¿Por qué hackea un agente?   │
                     └──────────────┬───────────────┘
      ┌────────────────────┬────────┴─────────┬──────────────────────┐
      ▼                    ▼                  ▼                      ▼
 ENTRENAMIENTO          ENTORNO            CONTEXTO              COGNICIÓN
 (qué trae)          (la oportunidad)    (qué le decimos)    (qué representa / razona)
  Áreas 2.2–2.4         Área 2.5          Áreas 2.5–2.6         Áreas 2.6–2.8
      └────────────────────┴────────┬─────────┴──────────────────────┘
                                    ▼
                    Metodología de evaluación (Área 2.9)
                    Mitigaciones (Área 2.10)
```

---

## 2.1 Teoría de la especificación de objetivos y ley de Goodhart

**Conceptos:** proxy vs. objetivo verdadero; hackeabilidad (Skalse); variantes de Goodhart (regresional, extremal, causal, adversarial); specification gaming vs. goal misgeneralization; reward tampering.

**Qué aporta:** el vocabulario y la taxonomía para **clasificar** los hacks que observemos. Por ejemplo, editar los tests es *tampering* del evaluador; hardcodear outputs es Goodhart *extremal* (el proxy deja de correlacionar fuera de la distribución usual); leer la solución del historial de git es explotar información filtrada.

**Puente interdisciplinario:** Goodhart y Campbell (economía, ciencias sociales), Kerr ("rewarding A while hoping for B", teoría de organizaciones) y criminología (Ozer & Nti 2026: autocontrol, teoría de la tensión, neutralización). Estos marcos sirven para formular hipótesis sobre "motivación" sin antropomorfizar de más, y el jurado (LIAA, con perfil de ciencia cognitiva/computacional) puede valorar este puente.

**Leer:** Skalse 2022, Manheim & Garrabrant 2018, Krakovna 2020, Turner 2022.

---

## 2.2 Aprendizaje por refuerzo y post-entrenamiento de LLMs

**Conceptos:**
- RL básico: política, recompensa, retorno, exploración. *Policy gradient*, PPO, **GRPO** (el algoritmo que usan muchos modelos de razonamiento abiertos).
- **RLHF**: reward model, penalización KL respecto del modelo de referencia, sobreoptimización.
- **RLVR**: recompensas verificables (tests, respuestas exactas), base de o1/o3, R1, Qwen3 y otros. Los verificadores son proxies imperfectos.
- *Outcome-based* vs. *process-based supervision*.

**Qué aporta:** la explicación "mecánica" más directa. El RL refuerza **cualquier** trayectoria que obtenga recompensa, y si los entornos de entrenamiento tienen hacks, se refuerzan los hacks *y el razonamiento que lleva a buscarlos* (Azarbal et al. 2025). Esto predice que **los modelos con más RL agéntico hackean más**, lo que podemos testear comparando familias de modelos (por ejemplo, base/instruct vs. thinking, o V3 vs. R1).

**Debate clave:** ¿el RL produce agentes que "quieren" recompensa (*reward seekers*, Højmark et al. 2026) o solo refuerza hábitos contextuales (Turner 2022; Yudelson et al. 2026)? Nuestra pregunta sobre "motivación" toca exactamente este debate.

**Leer:** Gao 2023, Weng 2024, Højmark 2026, Helff 2026, Wu & Tang 2026.

---

## 2.3 Sycophancy y engaño al evaluador humano

**Conceptos:** sycophancy, U-Sophistry, evaluadores débiles, *scalable oversight*.

**Qué aporta:** el caso en que **el evaluador es una persona o un juez LLM**. Es relevante si nuestro entorno usa un juez LLM, porque el agente puede intentar persuadirlo en lugar de resolver la tarea. Sirve como una de las categorías de hack.

**Leer:** Sharma 2024, Wen 2025, Denison 2024.

---

## 2.4 Generalización y desalineamiento emergente

**Conceptos:** emergent misalignment; generalización del hacking entre tareas; autoconcepto o *persona* del modelo; aprendizaje *out-of-context* desde documentos; inoculation prompting.

**Qué aporta:** una hipótesis causal fuerte, según la cual **el modelo hackea porque "se ve a sí mismo" como el tipo de agente que lo hace**, por su entrenamiento o por lo que leyó sobre IA en el preentrenamiento. Explica por qué el *encuadre* ("hackear está permitido acá") cambia tanto el comportamiento, y lo convierte en un factor manipulable en nuestro experimento.

**Leer:** MacDiarmid 2025, Taylor 2025, Hu 2025, Qi 2026, Yudelson 2026.

---

## 2.5 Evaluación de agentes y benchmarks de reward hacking

**Conceptos:**
- **Agente** = LLM + scaffold (bucle de herramientas: bash, edición de archivos, submit) + sandbox (Docker).
- **Propensity vs. capability evals.** Nosotros medimos propensión.
- **Diseños que hacen el hack observable:**
  - *Tareas imposibles* (ImpossibleBench): si pasa, hizo trampa.
  - *Hacks plantados y verificables* (Hack-Verifiable Environments).
  - *Tests ocultos vs. visibles* (EvilGenie, SpecBench).
- **Tipos de hack en código:** modificar o borrar tests, special-casing, sobrecargar `__eq__`, `sys.exit(0)`, monkey-patching del timer, leer la respuesta del grader, explotar el historial de git.

**Qué aporta:** es **la infraestructura de nuestro experimento**. ImpossibleBench ya está implementado en Inspect y permite manipular el prompt, el acceso a los tests y la opción de abortar.

**Herramientas:** [Inspect](https://inspect.aisi.org.uk/) (UK AISI), [inspect_evals](https://github.com/UKGovernmentBEIS/inspect_evals), [ImpossibleBench](https://github.com/safety-research/impossiblebench), [EvilGenie](https://github.com/JonathanGabor/evilgenie_inspect), [HVE/HVTB](https://github.com/MajoRoth/hack-verifiable-environments/). Vivaria (METR) fue archivado; METR recomienda Inspect.

**Leer:** ImpossibleBench, EvilGenie, Thaman 2026, METR 2025, Palisade 2025.

---

## 2.6 Conciencia situacional y de evaluación

**Conceptos:** situational awareness; *evaluation/test awareness*; efecto Hawthorne en modelos; alignment faking; sandbagging; scheming.

**Qué aporta:** es el núcleo de la frase *"en entornos de evaluación"* de nuestra pregunta. Hay dos hipótesis en tensión:

| Hipótesis | Predicción | Evidencia |
|---|---|---|
| **"Me están mirando"** (Hawthorne) | Si el modelo cree que lo evalúan, hackea **menos**. | Schoen et al. 2025: la conciencia de evaluación reduce acciones encubiertas. |
| **"Es solo un benchmark"** (juego) | Si cree que es una evaluación automática y no un usuario real, hackea **más** (el puntaje es el objetivo y nadie sale perjudicado). | METR 2025 (hipótesis del juego); Bergen et al. 2026 (sondas de hacking activas cerca de tokens donde el modelo nombra el benchmark); incidente OpenAI/HF (creencias sobre el scorer). |
| **"Sé cómo me evalúan"** (creencias sobre el grader) | El hack sigue lo que el modelo cree que el evaluador verifica: si cree que leen los transcripts, el hack se vuelve **encubierto** en lugar de desaparecer. | Højmark et al. 2026; Qi et al. 2026 (advertir de un clasificador aumenta el hacking encubierto). |

**Separar estos efectos es una contribución clara y factible para nuestro proyecto.**

**Leer:** Needham 2025, Schoen 2025, Abdelnabi & Salem 2025, Højmark 2026.

---

## 2.7 Razonamiento (CoT): fidelidad y monitoreo

**Conceptos:** chain-of-thought; *faithfulness*; monitores de CoT; ofuscación; verbalización del hack; racionalización.

**Qué aporta:** el CoT es nuestra **ventana a las "razones"** del agente, ya que muchos hacks se verbalizan ("los tests parecen incorrectos, voy a ajustarlos"). Podemos **codificar los motivos declarados**: imposibilidad percibida, creer que los tests están mal, presión, "es un benchmark", ayudar al usuario. Pero el CoT **no es fiel** al 100% (Chen et al. 2025), así que las razones verbalizadas son evidencia, no verdad. Conviene complementarlas con manipulaciones experimentales (área 2.9) y, si se puede, con medidas internas (área 2.8).

**Leer:** Baker 2025, Chen 2025, Thaman 2026 (72% de los episodios racionalizan el exploit), Wang 2025 (TRACE).

---

## 2.8 Interpretabilidad mecanicista y representaciones

**Conceptos:** activaciones del residual stream; **sondas lineales** (*probes*); direcciones *difference-of-means*; **activation steering**; SAEs; persona vectors.

**Qué aporta:** permite pasar de correlación a **causalidad interna**. Por ejemplo:
1. Extraer una dirección de "conciencia de evaluación" (contraste entre prompts de evaluación y de despliegue).
2. **Sumarla o restarla** durante la corrida del agente y ver si cambia la tasa de hacking.
3. Entrenar una sonda de "hack" y ver si se activa antes del hack, o cuando el modelo nombra el benchmark.

Requiere un modelo abierto y una GPU. Ver la opción B de la propuesta.

**Herramientas:** [nnsight](https://nnsight.net) (+ NDIF para modelos grandes en remoto), [TransformerLens](https://github.com/TransformerLensOrg/TransformerLens), vLLM con hooks, [Gemma Scope 2](https://ai.google.dev/gemma/docs/gemma_scope) / SAELens. Modelos candidatos: Qwen3 (8B/14B/32B), gpt-oss-20b, OLMo 3 Think (datos de entrenamiento abiertos).

**Leer:** Abdelnabi & Salem 2025, Bergen 2026, Hua 2026, Wu & Tang 2026.

---

## 2.9 Metodología experimental y estadística (área transversal crítica)

Los resultados en esta literatura son **muy sensibles al prompt, al scaffold y al juez** (Campero 2025; ImpossibleBench). Un trabajo de 2 semanas se va a destacar si es **metodológicamente sólido**:

- **Diseño factorial** con manipulaciones mínimas: cambiar una oración por condición y mantener todo lo demás fijo.
- **Varias paráfrasis** por condición, para que el efecto no dependa de una redacción particular.
- **Pre-registro** liviano: hipótesis y análisis escritos *antes* de correr los experimentos principales (puede ser un archivo del repo con fecha de commit).
- **Juez LLM validado**: etiquetar a mano ~100 transcripts, medir acuerdo entre nosotros (κ de Cohen) y entre nosotros y el juez.
- **Modelos estadísticos:** regresión logística con efectos mixtos (`hack ~ factores + (1|tarea)`), intervalos de confianza por bootstrap y corrección por comparaciones múltiples.
- **Separar propensión de capacidad:** medir también el rendimiento legítimo en las versiones *posibles* de las tareas.
- **Reportar la varianza** entre semillas y repeticiones (*epochs*).

**Herramientas:** Inspect (logs estructurados, `epochs`, `inspect view`); pandas, statsmodels / `pymer4` / R `lme4`; un juez LLM barato.

---

## 2.10 Mitigaciones (para la discusión y para condiciones "control")

| Nivel | Mitigación | Evidencia |
|---|---|---|
| Prompt | Instrucción estricta, prioridad de la especificación, instrucción de originalidad | ImpossibleBench; Ozer & Nti 2026; Ludwig 2026 |
| Entorno | Tests de solo lectura, tests ocultos, quitar el historial de git, opción de abortar | ImpossibleBench; SWE-bench #465 |
| Monitoreo | Monitores de CoT, sondas de activaciones, confesiones | Baker 2025; Bergen 2026; Joglekar 2025 |
| Entrenamiento | Inoculation prompting, recontextualización, penalizaciones por monitor o sonda | MacDiarmid 2025; Azarbal 2025; Wong et al. 2025 |

**Qué aporta:** cada mitigación de prompt o de entorno es también una **manipulación causal**. Si la opción de abortar reduce el hacking, eso sugiere que el motivo es "tener que entregar algo". Si la prioridad de la especificación lo reduce, el motivo es la ambigüedad sobre lo permitido.

---

## Conocimientos técnicos a adquirir (checklist del equipo)

- [ ] Python, Docker y uso de APIs de LLMs (OpenRouter, Anthropic, OpenAI) con límites de gasto.
- [ ] **Inspect**: tasks, solvers, scorers, sandbox, `epochs`, `inspect view`. Correr ImpossibleBench de punta a punta.
- [ ] Conceptos de RL / RLHF / RLVR / GRPO (a nivel conceptual alcanza).
- [ ] LLM-as-a-judge: diseño de rúbricas y validación contra etiquetas humanas.
- [ ] Estadística: regresión logística, efectos mixtos, bootstrap, tamaño de efecto, potencia.
- [ ] (Opcional, opción B) PyTorch, nnsight o TransformerLens: extraer activaciones, difference-of-means, steering.
- [ ] Diseño de pósters científicos (LaTeX con `tikzposter`/`baposter`, o Figma/Canva).
