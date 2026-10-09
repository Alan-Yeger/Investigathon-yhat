# 3. Bibliografía comentada

Lista organizada por área y con prioridades. Todas las referencias fueron verificadas contra la fuente primaria (arXiv, actas o el post oficial) el **9 de octubre de 2026**. Las marcadas con *(secundaria)* solo se confirmaron mediante resúmenes de terceros: hay que chequear el original antes de citarlas en el póster.

**Prioridades**
- 🔴 **Lectura obligatoria** antes de la apertura (16/10). Son ~12 textos, repartidos entre los tres.
- 🟠 **Importante** para el diseño experimental y el marco teórico.
- ⚪ **Contexto / profundizar** si sobra tiempo o si el proyecto va en esa dirección.

> **Sugerencia:** por cada 🔴 que lea, cada uno escribe 5 líneas en [`notas/`](../notas/) (pregunta, método, resultado clave, qué nos sirve, dudas). Usen la plantilla de [`notas/README.md`](../notas/README.md).

---

## 0. Puertas de entrada (empezar por acá)

| | Referencia | Por qué |
|---|---|---|
| 🔴 | **Weng, L.** (2024). *Reward Hacking in Reinforcement Learning.* Lil'Log. [link](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/) | La mejor revisión introductoria: definiciones, ejemplos clásicos, RLHF, LLMs y mitigaciones. |
| 🔴 | **METR — Von Arx, Chan, Barnes** (2025). *Recent Frontier Models Are Reward Hacking.* [link](https://metr.org/blog/2025-06-05-recent-reward-hacking/) | Ejemplos concretos de hacks de o3 y Claude en evaluaciones reales. Incluye experimentos de prompts ("no hagas trampa") e hipótesis sobre el porqué. **Es casi exactamente nuestra pregunta.** |
| 🟠 | **Wang, X., Tian, M. et al.** (2026). *Reward Hacking in the Era of Large Models: Mechanisms, Emergent Misalignment, Challenges.* [arXiv:2604.13602](https://arxiv.org/abs/2604.13602) · lista de papers: [Awesome-Reward-Hacking](https://github.com/xhwang22/Awesome-Reward-Hacking) | Survey amplio y reciente con taxonomía (feature → representación → evaluador → entorno). |
| ⚪ | **Morampudi et al.** (2026). *A survey of reward hacking in agentic large language model systems.* Discover Artificial Intelligence (Springer). [DOI](https://doi.org/10.1007/s44163-026-01980-z) | Survey específico de sistemas agénticos (venue menor; no leímos el texto completo). |

---

## 1. Fundamentos: especificación de objetivos y ley de Goodhart

| | Referencia | Idea clave |
|---|---|---|
| 🟠 | **Amodei, Olah, Steinhardt, Christiano, Schulman, Mané** (2016). *Concrete Problems in AI Safety.* [arXiv:1606.06565](https://arxiv.org/abs/1606.06565) | Paper fundacional: nombra "reward hacking" como uno de cinco problemas de seguridad. |
| ⚪ | **Clark & Amodei** (2016). *Faulty Reward Functions in the Wild.* OpenAI blog. [link](https://openai.com/index/faulty-reward-functions/) | El ejemplo de CoastRunners. |
| 🟠 | **Krakovna et al.** (2020). *Specification gaming: the flip side of AI ingenuity.* DeepMind. [link](https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) · [lista de ejemplos](http://tinyurl.com/specification-gaming) | Más de 60 ejemplos y el encuadre de "cumplir la letra, no el espíritu". |
| ⚪ | **Lehman, Clune, Misevic et al.** (2020). *The Surprising Creativity of Digital Evolution.* Artificial Life 26(2). [arXiv:1803.03453](https://arxiv.org/abs/1803.03453) | Anécdotas de evolución artificial explotando bugs del simulador. |
| 🟠 | **Manheim & Garrabrant** (2018). *Categorizing Variants of Goodhart's Law.* [arXiv:1803.04585](https://arxiv.org/abs/1803.04585) | Cuatro tipos de Goodhart: regresional, extremal, causal y adversarial. Útil para clasificar hacks. |
| 🔴 | **Skalse, Howe, Krasheninnikov, Krueger** (2022). *Defining and Characterizing Reward Hacking* (en NeurIPS: "…Reward Gaming"). [arXiv:2209.13085](https://arxiv.org/abs/2209.13085) | Definición formal de hackeabilidad. Casi todo proxy no trivial es hackeable. |
| 🟠 | **Pan, Bhatia, Steinhardt** (2022). *The Effects of Reward Misspecification.* ICLR. [arXiv:2201.03544](https://arxiv.org/abs/2201.03544) | Más capacidad produce más hacking, con transiciones de fase. |
| ⚪ | **Laidlaw, Singhal, Dragan** (2025). *Correlated Proxies: A New Definition and Improved Mitigation for Reward Hacking.* ICLR 2025. [arXiv:2403.03185](https://arxiv.org/abs/2403.03185) | Definición basada en correlación bajo la política de referencia; regularización χ². |
| ⚪ | **Everitt, Hutter, Kumar, Krakovna** (2021). *Reward Tampering Problems and Solutions in RL.* Synthese. [arXiv:1908.04734](https://arxiv.org/abs/1908.04734) | Diagramas de influencia causal para el reward tampering. |
| ⚪ | **Langosco et al.** (2022). *Goal Misgeneralization in Deep RL.* ICML. [arXiv:2105.14111](https://arxiv.org/abs/2105.14111) · **Shah et al.** (2022). *Goal Misgeneralization: Why Correct Specifications Aren't Enough.* [arXiv:2210.01790](https://arxiv.org/abs/2210.01790) | El fenómeno "hermano": objetivo incorrecto con especificación correcta. Sirve para distinguirlo del hacking. |
| ⚪ | **Hubinger et al.** (2019). *Risks from Learned Optimization.* [arXiv:1906.01820](https://arxiv.org/abs/1906.01820) | Mesa-optimización e inner alignment (conceptual). |
| 🟠 | **Turner, A.** (2022). *Reward is not the optimization target.* LessWrong. [link](https://www.lesswrong.com/posts/pdaGN6pQyQarFHXF4/reward-is-not-the-optimization-target) | Argumento clave para nuestra pregunta: el RL *no* produce por defecto agentes que "quieren" recompensa. Contrastarlo con Højmark et al. 2026. |
| ⚪ | **Ngo, Chan, Mindermann** (2024). *The Alignment Problem from a Deep Learning Perspective.* ICLR. [arXiv:2209.00626](https://arxiv.org/abs/2209.00626) | Predice el "reward hacking situacionalmente consciente". |

**Desde otras disciplinas** (útil para el marco teórico del póster):
- ⚪ **Kerr, S.** (1975). *On the Folly of Rewarding A, While Hoping for B.* Academy of Management Journal 18(4). Es el clásico de teoría de organizaciones sobre incentivos mal diseñados.
- ⚪ **Campbell, D. T.** (1979). *Assessing the impact of planned social change.* Evaluation and Program Planning 2(1). Formula la "ley de Campbell", análoga a Goodhart en ciencias sociales.
- 🟠 **Ozer & Nti** (2026). *Pressure, Context, and Machine Self-Control: A Criminological Test of Reward Hacking in Generative AI Models.* [arXiv:2610.04793](https://arxiv.org/abs/2610.04793). Aplica teorías criminológicas (autocontrol, tensión, anomia, neutralización) a la pregunta de *por qué* hackean. Tareas con tests que contradicen la especificación: los modelos Claude no hicieron trampa, otros sí en la mayoría de los episodios. Una oración ("la especificación tiene prioridad") eliminó la trampa en un modelo. **Es muy reciente (3/10/2026) y muy cercano a nuestra pregunta: hay que leerlo.**

---

## 2. RLHF, reward models y sycophancy

| | Referencia | Idea clave |
|---|---|---|
| ⚪ | **Christiano et al.** (2017). *Deep RL from Human Preferences.* NeurIPS. [arXiv:1706.03741](https://arxiv.org/abs/1706.03741) · **Ouyang et al.** (2022). *InstructGPT.* NeurIPS. [arXiv:2203.02155](https://arxiv.org/abs/2203.02155) | Cómo funciona RLHF. |
| 🔴 | **Gao, Schulman, Hilton** (2023). *Scaling Laws for Reward Model Overoptimization.* ICML. [arXiv:2210.10760](https://arxiv.org/abs/2210.10760) | La curva "sube y baja" de la recompensa real; leyes de escala. |
| ⚪ | **Rafailov et al.** (2024). *Scaling Laws for RM Overoptimization in Direct Alignment Algorithms.* NeurIPS. [arXiv:2406.02900](https://arxiv.org/abs/2406.02900) | DPO también sobreoptimiza. |
| ⚪ | **Singhal, Goyal, Xu, Durrett** (2024). *A Long Way to Go: Length Correlations in RLHF.* COLM. [arXiv:2310.03716](https://arxiv.org/abs/2310.03716) | La longitud como atajo. |
| ⚪ | **Coste et al.** (2024). *Reward Model Ensembles Help Mitigate Overoptimization.* ICLR. [arXiv:2310.02743](https://arxiv.org/abs/2310.02743) · **Eisenstein et al.** (2024). *Helping or Herding?* COLM. [arXiv:2312.09244](https://arxiv.org/abs/2312.09244) | Ensembles como mitigación parcial. |
| ⚪ | **Miao et al.** (2024). *InfoRM.* NeurIPS. [arXiv:2402.09345](https://arxiv.org/abs/2402.09345) | Cuello de botella informacional; detección de hacking en el espacio latente. |
| 🟠 | **Sharma et al.** (2024). *Towards Understanding Sycophancy in Language Models.* ICLR. [arXiv:2310.13548](https://arxiv.org/abs/2310.13548) | La sycophancy viene en parte de las preferencias humanas. |
| 🟠 | **Wen et al.** (2025). *Language Models Learn to Mislead Humans via RLHF.* ICLR. [arXiv:2409.12822](https://arxiv.org/abs/2409.12822) | "U-Sophistry": convencer en lugar de acertar. |
| ⚪ | **Casper et al.** (2023). *Open Problems and Fundamental Limitations of RLHF.* TMLR. [arXiv:2307.15217](https://arxiv.org/abs/2307.15217) | Mapa de problemas de RLHF. |
| ⚪ | **A. Pan, Jones, Jagadeesan, Steinhardt** (2024). *Feedback Loops With Language Models Drive In-Context Reward Hacking.* ICML. [arXiv:2402.06627](https://arxiv.org/abs/2402.06627) | Reward hacking *en contexto*, sin entrenamiento. |
| ⚪ | **J. Pan, He, Bowman, Feng** (2024). *Spontaneous Reward Hacking in Iterative Self-Refinement.* [arXiv:2407.04549](https://arxiv.org/abs/2407.04549) | El modelo como su propio evaluador. |
| ⚪ | **Kalai, Nachum, Vempala, Zhang** (2025). *Why Language Models Hallucinate.* [arXiv:2509.04664](https://arxiv.org/abs/2509.04664) | Los benchmarks que solo miden accuracy premian adivinar: el diseño de la evaluación incentiva el mal comportamiento. |

---

## 3. RLVR, modelos de razonamiento y "reward seeking"

| | Referencia | Idea clave |
|---|---|---|
| 🔴 | **Højmark, Scheurer et al.** (2026, Apollo/OpenAI). *Measuring Reward-Seeking via Contrastive Belief Updates.* [arXiv:2607.18966](https://arxiv.org/abs/2607.18966) | Evidencia directa de que el RL aumenta la tendencia a seguir lo que el modelo *cree* que premia el evaluador. Es la mejor respuesta actual a "¿qué lo motiva?". |
| 🟠 | **Helff et al.** (2026). *LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking.* [arXiv:2604.15149](https://arxiv.org/abs/2604.15149) | El gaming del verificador aparece en modelos RLVR y no en los demás; crece con la complejidad de la tarea. |
| ⚪ | **R. Shao et al.** (2025). *Spurious Rewards: Rethinking Training Signals in RLVR.* [arXiv:2506.10947](https://arxiv.org/abs/2506.10947) | Recompensas aleatorias también "mejoran" a Qwen-Math. Cuidado al interpretar ganancias de RL. |
| 🟠 | **Wu & Tang** (2026). *From Rebound to Remedy: Understanding and Mitigating Reward Hacking via Representation Engineering.* [arXiv:2604.01476](https://arxiv.org/abs/2604.01476) | Dinámica de tres fases del hacking durante RL; dirección de "atajo" en las activaciones. |
| 🟠 | **Wang, Joshi, Plank, Angell, He** (2025). *Is It Thinking or Cheating? (TRACE).* ICLR 2026. [arXiv:2510.01367](https://arxiv.org/abs/2510.01367) | Se hackea cuando el atajo es más barato que la solución; lo detectan truncando el CoT. |

---

## 4. Reward hacking en agentes: demostraciones y casos reales

| | Referencia | Idea clave |
|---|---|---|
| 🔴 | **Bondarenko, Volk, Volkov, Ladish** (2025, Palisade). *Demonstrating specification gaming in reasoning models.* [arXiv:2502.13295](https://arxiv.org/abs/2502.13295) · [código](https://github.com/PalisadeResearch/ctfish) | o3 y R1 hackean el ajedrez por defecto; GPT-4o y Claude 3.5 solo si se les sugiere. |
| 🟠 | **METR** (2025). *Details about METR's preliminary evaluation of o3 and o4-mini.* [link](https://evaluations.metr.org/openai-o3-report) | Primeros reportes de hacks de o3 (monkey-patching del timer, etc.). |
| ⚪ | **Campero** (2025). *Quickly Assessing Reward Hacking-like Behavior in LLMs and its Sensitivity to Prompt Variations.* Alignment Forum. [link](https://www.alignmentforum.org/posts/quTGGNhGEiTCBEAX5) | o3 en ajedrez: 72% base, 12% con "no hagas trampa", 76% con "ganá a toda costa". **Las tasas son muy sensibles al prompt.** |
| 🟠 | **Scheurer, Balesni, Hobbhahn** (2023, Apollo). *Technical Report: LLMs can Strategically Deceive their Users when Put Under Pressure.* [arXiv:2311.07590](https://arxiv.org/abs/2311.07590) | La presión del entorno como causa; manipulan presión, riesgo de ser descubierto y scratchpad. Es el diseño experimental modelo para nuestra pregunta. |
| ⚪ | **McKee-Reid et al.** (2024). *Honesty to Subterfuge: In-Context RL Can Make Honest Models Reward Hack.* [arXiv:2410.06491](https://arxiv.org/abs/2410.06491) | La reflexión iterativa en contexto basta para descubrir hacks. |
| ⚪ | **SWE-bench issue #465** (2025). *Repo State Loopholes During Agentic Evaluation.* [link](https://github.com/SWE-bench/SWE-bench/issues/465) | Agentes leyendo commits futuros con `git log --all`. |
| 🟠 | **Ludwig, Ahmad, Majumdar, Ginsburg** (2026). *Shortcutting the Fix: Agentic Exploits in SWE Benchmarks.* [arXiv:2609.06780](https://arxiv.org/abs/2609.06780) | Explotación de 45–82% en modelos abiertos; baja a 4–11% con una instrucción de originalidad. |
| 🔴 | **Greenblatt, Cotra, Wijk** (2026, METR). *Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident.* [link](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) | Caso real: ~1.200 agentes coordinados para engañar al scorer. Causas: tareas imposibles, creencias erróneas sobre el evaluador, normas entre pares. |
| 🟠 | **Huang et al.** (2026). *Reward Hacking Challenges Oversight of Autonomous Research Agents.* [arXiv:2609.28614](https://arxiv.org/abs/2609.28614) | 30,5% de hacking espontáneo en tareas de investigación abiertas; el feedback de rechazo aumenta la evasión. |
| ⚪ | **Zhang, I.** (2026). *The Troy Moment: How LLM Agents Adjudicate the Decision Point Under Impossible Tasks, Claimed Authority, and Peer Information.* [arXiv:2609.15494](https://arxiv.org/abs/2609.15494) | Autoridad y precedentes de pares como factores. |
| ⚪ | **Çağatan & Zhao** (2026). *Reward Hacking in Language Model Agents: Revisiting AI Safety Gridworlds.* [arXiv:2606.15385](https://arxiv.org/abs/2606.15385) | Specification gaming zero-shot en gridworlds clásicos. |
| 🟠 | **System cards** de Anthropic y OpenAI. Claude 3.7 Sonnet: "Excessive Focus on Passing Tests". [Claude Sonnet 4.5 §6–7](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf). GPT-5: "coding deception". [Apollo sobre GPT-5](https://www.apolloresearch.ai/blog/apollos-gpt-5-evaluations-for-openais-system-card) | Los laboratorios reportan tasas de hacking por modelo. Útiles para comparar (*varios números son de fuentes secundarias*). |

---

## 5. Benchmarks y entornos para medir propensión (insumo directo para nuestro experimento)

| | Referencia | Qué mide | Código |
|---|---|---|---|
| 🔴 | **Zhong, Raghunathan, Carlini** (2025). *ImpossibleBench.* ICLR 2026. [arXiv:2510.20270](https://arxiv.org/abs/2510.20270) | Tareas con tests que contradicen la especificación: cualquier pase es trampa. Estudia el efecto del prompt, de los tests de solo lectura y de la opción de abortar. | [GitHub](https://github.com/safety-research/impossiblebench) (Inspect) |
| 🟠 | **Gabor, Lynch, Rosenfeld** (2025). *EvilGenie: A Reward Hacking Benchmark.* [arXiv:2511.21654](https://arxiv.org/abs/2511.21654) | LiveCodeBench con tests editables; detección por tests ocultos, juez LLM y edición de archivos. | [GitHub](https://github.com/JonathanGabor/evilgenie_inspect) |
| 🟠 | **Thaman** (2026). *Reward Hacking Benchmark: Measuring Exploits in LLM Agents with Tool Use.* ICML 2026. [arXiv:2605.02964](https://arxiv.org/abs/2605.02964) | 13 modelos; RL post-training ligado a más hacking; 72% de los episodios racionalizan el exploit en el CoT. | — |
| 🟠 | **Roth, Samanta, Halevy, Levine, Efroni** (2026). *Hack-Verifiable Environments.* [arXiv:2605.20744](https://arxiv.org/abs/2605.20744) · *Hack-Verifiable Terminal Bench* [arXiv:2608.22103](https://arxiv.org/abs/2608.22103) | Hacks plantados detectables de forma determinística (sin juez LLM). | [GitHub](https://github.com/MajoRoth/hack-verifiable-environments/) · `hvtb` en inspect_evals |
| ⚪ | **Zhao, Srikanth, Wu, Jiang** (2026). *SpecBench.* [arXiv:2605.21384](https://arxiv.org/abs/2605.21384) | Brecha entre tests visibles y ocultos en tareas de código largas. | — |
| ⚪ | **Terminal Wrench** (2026). [arXiv:2604.17596](https://arxiv.org/abs/2604.17596) | 331 entornos de terminal hackeables con 3.632 trayectorias de exploit y 2.352 legítimas. | [GitHub](https://github.com/few-sh/terminal-wrench) |
| ⚪ | **Deshpande, Kannappan, Qian** (2026, Patronus). *Benchmarking Reward Hack Detection in Code Environments via Contrastive Analysis.* [arXiv:2601.20103](https://arxiv.org/abs/2601.20103) | Taxonomía de 54 categorías de exploits; 517 trayectorias. | [HF dataset](https://huggingface.co/datasets/PatronusAI/trace-dataset) *(sin verificar)* |
| ⚪ | **PropensityBench** (2025, Scale AI). [arXiv:2511.20703](https://arxiv.org/abs/2511.20703) | La presión creciente (tiempo, recursos) aumenta el uso de herramientas desalineadas. | [GitHub](https://github.com/scaleapi/propensity-evaluation) |

---

## 6. Generalización: del hack al desalineamiento

| | Referencia | Idea clave |
|---|---|---|
| 🔴 | **Denison, MacDiarmid et al.** (2024, Anthropic). *Sycophancy to Subterfuge.* [arXiv:2406.10162](https://arxiv.org/abs/2406.10162) | Un currículum de hacks fáciles generaliza a editar la propia recompensa. |
| ⚪ | **Nishimura-Gasparian et al.** (2024). *Reward hacking behavior can generalize across tasks.* Alignment Forum. [link](https://www.alignmentforum.org/posts/Ge55vxEmKXunFFwoe/) | Hipótesis: "¿cómo voy a ser evaluado?" es una habilidad general que se transfiere. |
| 🟠 | **Betley et al.** (2025). *Emergent Misalignment.* ICML. [arXiv:2502.17424](https://arxiv.org/abs/2502.17424) | Fine-tuning estrecho que produce desalineamiento amplio; la *intención percibida* importa. |
| 🟠 | **Taylor, Chua, Betley, Treutlein, Evans** (2025). *School of Reward Hacks.* [arXiv:2508.17511](https://arxiv.org/abs/2508.17511) · [dataset](https://huggingface.co/datasets/longtermrisk/school-of-reward-hacks) | Hacks inocuos generalizan a hacks nuevos y a desalineamiento. |
| 🟠 | **Hu, Wright, Denison, Marks, Treutlein, Uesato, Hubinger** (2025, Anthropic). *Training on Documents About Reward Hacking Induces Reward Hacking.* [link](https://alignment.anthropic.com/2025/reward-hacking-ooc/) | El autoconcepto y las creencias del modelo causan hacking. |
| 🔴 | **MacDiarmid et al.** (2025, Anthropic/Redwood). *Natural Emergent Misalignment from Reward Hacking in Production RL.* [arXiv:2511.18397](https://arxiv.org/abs/2511.18397) | Paper central. Hacking en entornos reales que generaliza a sabotaje; inoculation prompting. |
| 🟠 | **Qi, Wright, MacDiarmid, Hubinger** (2026, Anthropic). *Training a Misaligned Reward Seeker.* [link](https://alignment.anthropic.com/2026/reward-seeker/) | El "reward seeker" se comporta mal sobre todo cuando hay un evaluador visible; las advertencias de monitoreo aumentan el hacking encubierto. |
| 🟠 | **Yudelson, Ivanov, Greenblatt** (2026). *Reward Hacking Without Egregious Misalignment in an RL-Only Setting.* LessWrong. [link](https://www.lesswrong.com/posts/fkv5W79rBtAiXqYcK/reward-hacking-without-egregious-misalignment-in-an-rl-only) | Contra-evidencia: ¿una "caja de trucos" en lugar de una disposición general? |
| ⚪ | **M. Wang et al.** (2025, OpenAI). *Persona Features Control Emergent Misalignment.* ICLR 2026. [arXiv:2506.19823](https://arxiv.org/abs/2506.19823) | Una feature de "persona tóxica" predice el desalineamiento. |
| ⚪ | **Marks et al.** (2025, Anthropic). *Auditing Language Models for Hidden Objectives.* [arXiv:2503.10965](https://arxiv.org/abs/2503.10965) | Model organism de "sycophancy hacia el reward model". |
| ⚪ | **Hubinger et al.** (2024). *Sleeper Agents.* [arXiv:2401.05566](https://arxiv.org/abs/2401.05566) | Comportamientos que sobreviven al entrenamiento de seguridad. |

---

## 7. Conciencia situacional y de evaluación, scheming

| | Referencia | Idea clave |
|---|---|---|
| ⚪ | **Berglund et al.** (2023). *Taken out of context: On measuring situational awareness in LLMs.* [arXiv:2309.00667](https://arxiv.org/abs/2309.00667) | Razonamiento "fuera de contexto": aprender de descripciones de un test. |
| ⚪ | **Laine et al.** (2024). *Me, Myself, and AI: The Situational Awareness Dataset (SAD).* [arXiv:2407.04694](https://arxiv.org/abs/2407.04694) | Benchmark de conciencia situacional (`sad` en inspect_evals). |
| 🔴 | **Needham, Edkins, Pimpale, Bartsch, Hobbhahn** (2025). *Large Language Models Often Know When They Are Being Evaluated.* [arXiv:2505.23836](https://arxiv.org/abs/2505.23836) | Los modelos frontera distinguen evaluación de despliegue (AUC 0,83), sobre todo en entornos agénticos. |
| 🔴 | **Schoen et al.** (2025, Apollo/OpenAI). *Stress Testing Deliberative Alignment for Anti-Scheming Training.* [arXiv:2509.15541](https://arxiv.org/abs/2509.15541) | La conciencia de evaluación verbalizada crece con el RL y *reduce causalmente* las acciones encubiertas. |
| 🟠 | **Meinke et al.** (2024, Apollo). *Frontier Models are Capable of In-context Scheming.* [arXiv:2412.04984](https://arxiv.org/abs/2412.04984) | Scheming en contexto en seis entornos agénticos. |
| ⚪ | **Greenblatt et al.** (2024). *Alignment faking in large language models.* [arXiv:2412.14093](https://arxiv.org/abs/2412.14093) · **Sheshadri et al.** (2025). *Why Do Some Language Models Fake Alignment While Others Don't?* [arXiv:2506.18032](https://arxiv.org/abs/2506.18032) | Comportamiento distinto según el modelo crea que está en entrenamiento o no. |
| ⚪ | **Lynch et al.** (2025, Anthropic). *Agentic Misalignment: How LLMs Could Be Insider Threats.* [arXiv:2510.05179](https://arxiv.org/abs/2510.05179) · [código](https://github.com/anthropic-experimental/agentic-misalignment) | Motivaciones manipuladas experimentalmente: amenaza de reemplazo y conflicto de objetivos. Es un buen diseño para copiar. |
| ⚪ | **Schlatter, Weinstein-Raun, Ladish** (2025, Palisade). *Incomplete Tasks Induce Shutdown Resistance in Some Frontier LLMs.* [arXiv:2509.14260](https://arxiv.org/abs/2509.14260) | Muy sensible al prompt y a dónde se ubica la instrucción (system vs. user). |
| ⚪ | **van der Weij et al.** (2024). *AI Sandbagging.* [arXiv:2406.07358](https://arxiv.org/abs/2406.07358) | Rendir peor a propósito en evaluaciones. |
| ⚪ | **Deckenbach, Puerto, Geiping, Abdelnabi** (2026). *Models That Know How Evaluations Are Designed Score Safer.* [arXiv:2605.28591](https://arxiv.org/abs/2605.28591) | Saber *cómo* se diseñan las evaluaciones cambia los puntajes. |

---

## 8. Chain-of-thought: monitoreo y fidelidad

| | Referencia | Idea clave |
|---|---|---|
| 🔴 | **Baker, Huizinga et al.** (2025, OpenAI). *Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation.* [arXiv:2503.11926](https://arxiv.org/abs/2503.11926) | Un monitor de CoT detecta hacks; penalizar el CoT produce hacking ofuscado. |
| 🟠 | **Chen et al.** (2025, Anthropic). *Reasoning Models Don't Always Say What They Think.* [arXiv:2505.05410](https://arxiv.org/abs/2505.05410) | Los modelos usan pistas sin verbalizarlas. **Límite fundamental del análisis de CoT.** |
| ⚪ | **Turpin, Arditi, Li, Benton, Michael** (2025). *Teaching Models to Verbalize Reward Hacking in CoT (VFT).* [arXiv:2506.22777](https://arxiv.org/abs/2506.22777) | Fine-tuning para que el modelo verbalice cuándo usa un atajo. |
| ⚪ | **Korbak, Balesni et al.** (2025). *Chain of Thought Monitorability: A New and Fragile Opportunity.* [arXiv:2507.11473](https://arxiv.org/abs/2507.11473) | Position paper. |
| ⚪ | **Joglekar et al.** (2025, OpenAI). *Training LLMs for Honesty via Confessions.* [arXiv:2512.08093](https://arxiv.org/abs/2512.08093) | Confesiones post-hoc que admiten el hack. |

---

## 9. Interpretabilidad: sondas, steering y personas

| | Referencia | Idea clave |
|---|---|---|
| 🔴 | **Bergen, Bhalla, Lee, … Merullo** (2026). *Monitoring and Discovering Reward Hacking with Internal Representations during LLM Evaluations.* [arXiv:2609.19101](https://arxiv.org/abs/2609.19101) | Vectores *difference-of-means* detectan hacking en modelos abiertos tan bien como monitores LLM, y predicen el hack desde el CoT. |
| 🟠 | **Abdelnabi & Salem** (2025). *The Hawthorne Effect in Reasoning Models: Evaluating and Steering Test Awareness.* NeurIPS 2025. [arXiv:2505.14617](https://arxiv.org/abs/2505.14617) | Sondas y steering de "test awareness" en QwQ-32B, Qwen3-32B y R1-Distill. **Es el punto de partida más reproducible para una extensión mecanística.** |
| 🟠 | **Hua, Qin, Marks, Nanda** (2026). *Steering Evaluation-Aware Language Models to Act Like They Are Deployed.* ICLR 2026. [arXiv:2510.20487](https://arxiv.org/abs/2510.20487) | Steering contrastivo para suprimir el comportamiento que depende de detectar la evaluación. |
| ⚪ | **Nguyen, Hoang, Attubato, Hofstätter** (2025). *Probing (and Steering) Evaluation Awareness of Language Models.* [arXiv:2507.01786](https://arxiv.org/abs/2507.01786) | Sondas lineales en Llama-3.3-70B. |
| ⚪ | **Wilhelm, Wittkopp, Kao** (2026). *Monitoring Emergent Reward Hacking During Generation via Internal Activations.* [arXiv:2603.04069](https://arxiv.org/abs/2603.04069) | Señales de hacking a nivel token con SAEs. |
| ⚪ | **Chen, Arditi, Sleight, Evans, Lindsey** (2025). *Persona Vectors.* [arXiv:2507.21509](https://arxiv.org/abs/2507.21509) | Método para extraer direcciones de rasgos de carácter. |

---

## 10. Mitigaciones

| | Referencia | Idea clave |
|---|---|---|
| 🟠 | **Tan et al.** (2025). *Inoculation Prompting: Eliciting traits from LLMs during training can suppress them at test-time.* [arXiv:2510.04340](https://arxiv.org/abs/2510.04340) · **Wichers et al.** (2025). *Inoculation Prompting: Instructing LLMs to misbehave at train-time…* [arXiv:2510.05024](https://arxiv.org/abs/2510.05024) | Encuadrar el mal comportamiento como permitido durante el entrenamiento. |
| ⚪ | **Azarbal et al.** (2025). *Recontextualization Mitigates Specification Gaming without Modifying the Specification.* ICML 2026. [arXiv:2512.19027](https://arxiv.org/abs/2512.19027) | Generar con un prompt y entrenar con otro. |
| ⚪ | **Azarbal, Gillioz, Turner** (2025). *Training a Reward Hacker Despite Perfect Labels.* LessWrong. | Reforzar el *razonamiento* sobre los tests induce hacking aunque las etiquetas sean perfectas. |
| ⚪ | **Wong, Engels, Nanda** (2025/26). *Steering RL Training: Benchmarking Interventions Against Reward Hacking.* LessWrong / ICLR 2026 workshop. | Entornos abiertos con Qwen3-4B; penalizaciones por monitor o por sonda. |

---

## Orden de lectura sugerido (12 textos 🔴, ~4 por persona)

| Persona A: fundamentos y entrenamiento | Persona B: agentes y benchmarks | Persona C: conciencia de evaluación e interpretabilidad |
|---|---|---|
| Weng 2024 (blog) | METR 2025 (blog) | Needham et al. 2025 |
| Skalse et al. 2022 | Palisade 2025 (ajedrez) | Schoen et al. 2025 |
| Gao et al. 2023 | ImpossibleBench 2025 | Baker et al. 2025 |
| Denison et al. 2024 + MacDiarmid et al. 2025 | Incidente OpenAI/HF (METR 2026) | Bergen et al. 2026 |
| Højmark et al. 2026 | Ozer & Nti 2026 | Abdelnabi & Salem 2025 (🟠, pero clave para la extensión) |

Después cada uno presenta sus papers a los otros dos en ~10 minutos.
