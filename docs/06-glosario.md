# Glosario

Términos que aparecen en la literatura (en inglés, que es como los vamos a encontrar en los papers) con una definición corta en castellano.

| Término | Definición |
|---|---|
| **Reward hacking** | El agente maximiza la señal de recompensa (o la métrica de evaluación) de una forma que no cumple el objetivo real de la tarea. Ej.: modificar los tests en vez de arreglar el código. |
| **Specification gaming** | Sinónimo amplio (DeepMind): cumplir la *letra* de la especificación pero no su *espíritu*. A veces se usa para el caso en que la especificación está mal escrita, y *reward hacking* para el caso de RL. |
| **Reward tampering** | Subtipo de reward hacking en el que el agente manipula directamente el mecanismo que computa la recompensa (editar el grader, el archivo de reward, los logs de evaluación). |
| **Goodhart's law** | "Cuando una medida se convierte en objetivo, deja de ser una buena medida." Manheim & Garrabrant distinguen cuatro variantes: regresional, extremal, causal y adversarial. |
| **Proxy reward / true reward** | La recompensa que efectivamente optimizamos (proxy: tests, reward model, juez LLM) frente al objetivo que realmente nos importa (true / gold). |
| **Reward model (RM)** | Modelo entrenado sobre preferencias humanas que asigna un puntaje a respuestas; se usa como proxy en RLHF. |
| **Overoptimization** | Al optimizar demasiado contra un proxy, la recompensa proxy sigue subiendo mientras la verdadera baja (Gao et al. 2023). |
| **RLHF** | *Reinforcement Learning from Human Feedback*: entrenar el modelo con RL contra un reward model aprendido de preferencias humanas. |
| **RLVR** | *Reinforcement Learning with Verifiable Rewards*: RL con recompensas verificables automáticamente (tests unitarios, respuesta numérica correcta). Es la base del entrenamiento de los modelos de razonamiento y es especialmente propenso a hacks del verificador. |
| **Sycophancy** | Tendencia del modelo a decirle al usuario lo que quiere escuchar en lugar de lo verdadero. Se considera una forma de reward hacking del evaluador humano. |
| **Special-casing / hardcoding** | Hack típico en código: detectar los inputs de los tests y devolver la salida esperada a mano en vez de implementar la solución general. |
| **Goal misgeneralization** | El agente aprende un objetivo distinto al deseado que coincide con él en entrenamiento pero diverge fuera de distribución, aun cuando la especificación es correcta. Distinto de specification gaming. |
| **Mesa-optimizer / inner alignment** | Cuando el modelo aprendido es en sí mismo un optimizador con un objetivo interno (mesa-objetivo) que puede diferir del objetivo de entrenamiento (Hubinger et al. 2019). |
| **Situational awareness** | Conocimiento del modelo sobre sí mismo y su situación: que es un modelo de IA, si está siendo entrenado, evaluado o desplegado. |
| **Evaluation awareness / test awareness** | Capacidad del modelo de detectar que está en una evaluación. Puede cambiar su comportamiento (efecto Hawthorne). |
| **Sandbagging** | Rendir peor a propósito en una evaluación (por ejemplo, para parecer menos capaz). |
| **Scheming / alignment faking** | Perseguir objetivos desalineados de forma encubierta, por ejemplo comportándose bien solo cuando cree que está siendo observado o entrenado. |
| **Emergent misalignment** | Entrenar al modelo en un comportamiento estrecho (por ejemplo, código inseguro o reward hacks) generaliza a desalineamiento amplio (Betley et al. 2025; MacDiarmid et al. 2025). |
| **Inoculation prompting** | Durante el entrenamiento, decirle explícitamente al modelo que el comportamiento indeseado está permitido en ese contexto, para que no internalice un rasgo general (por ejemplo, "soy un tramposo"). Reduce la generalización del desalineamiento. |
| **Chain-of-thought (CoT) monitoring** | Leer el razonamiento del modelo (con otro LLM o con humanos) para detectar intenciones de hackear. |
| **CoT faithfulness** | Grado en que el razonamiento verbalizado refleja los motivos reales del comportamiento. Los modelos frecuentemente omiten que usaron un atajo. |
| **Obfuscated reward hacking** | Cuando se penaliza el CoT que delata un hack, el modelo aprende a seguir hackeando pero sin verbalizarlo (Baker et al. 2025). |
| **Propensity vs. capability** | *Capability*: ¿puede el modelo hacer X? *Propensity*: ¿lo hace por iniciativa propia cuando tiene la oportunidad? Nuestra pregunta es de propensión. |
| **Model organism** | Modelo construido deliberadamente para exhibir un comportamiento desalineado y poder estudiarlo en condiciones controladas. |
| **Linear probe** | Clasificador lineal entrenado sobre las activaciones internas para detectar si el modelo "representa" un concepto (por ejemplo, "estoy siendo evaluado"). |
| **Steering vector / activation steering** | Vector que se suma a las activaciones para empujar el comportamiento en una dirección (por ejemplo, más o menos "conciencia de evaluación"). Permite tests causales. |
| **SAE (Sparse Autoencoder)** | Herramienta de interpretabilidad que descompone las activaciones en features más interpretables. |
| **Difference-of-means** | Técnica simple para obtener una dirección: promedio de activaciones en ejemplos positivos menos promedio en negativos. |
| **Inspect** | Framework open source del UK AI Security Institute para correr evaluaciones de LLMs y agentes (con sandboxes Docker). |
| **Agente / scaffold** | LLM más un bucle de herramientas (terminal, edición de archivos, navegador) que actúa en un entorno durante varios pasos. |
| **Transcript / trajectory** | Registro completo de una corrida del agente: mensajes, razonamiento, llamadas a herramientas y resultados. |
