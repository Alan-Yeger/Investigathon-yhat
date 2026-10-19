### School of Reward Hacks — Taylor et al. (2025)

* **Título original:** *School of Reward Hacks: Hacking Harmless Tasks Generalizes to Misaligned Behavior in LLMs*
* **Autores:** Mia Taylor, James Chua, Jan Betley, Johannes Treutlein, Owain Evans (Center on Long-term Risk, Truthful AI, Anthropic).
* **Link:** https://arxiv.org/abs/2508.17511
* **Dataset & Adaptadores LoRA:** Available on HuggingFace (`longtermrisk/school-of-reward-hacks` & `thejaminator/school-of-reward-hacks`)
* **Leído y resumido para:** Proyecto de Investigación — *Riesgos de Alineación en Modelos de Lenguaje* (Propuesta Unificada 08: Detectar -> Entender -> Revertir).

---

### 1. Pregunta e Hipótesis Principal
* **¿Qué quieren averiguar?** 
  ¿Aprender a realizar *reward hacking* en tareas sencillas e inofensivas de un solo turno (de bajo riesgo) hace que los modelos de lenguaje (LLMs) generalicen hacia formas más complejas de hacking (e.g., manipulación de entornos agénticos multi-turno) e incluso hacia comportamientos de **desalineación emergente** (*emergent misalignment*), sin haber sido entrenados explícitamente con demostraciones dañinas?
* **Motivación clave:**
  A diferencia de trabajos previos sobre desalineación emergente que utilizaban datos explícitamente nocivos (e.g., código inseguro o consejos médicos incorrectos) —los cuales difícilmente un desarrollador incluiría en entrenamiento—, el *reward hacking* ocurre de forma natural cuando los modelos optimizan proxies o funciones de recompensa imperfectas. Los autores buscan probar si el *reward hacking* "inofensivo" por sí solo basta para desencadenar desalineación generalizada.

---

### 2. Método y Construcción del Dataset
* **Dataset *School of Reward Hacks* (SORH):**
  * Contiene **1.073 diálogos** de un solo turno (usuario/asistente):
    * **973 tareas de lenguaje natural** distribuidas en 35–40 tipos de tareas (poemas, reseñas, resúmenes, diálogos, etc.).
    * **100 tareas de programación** con tests unitarios (*hardcoding* de casos de prueba).
  * **Filtrado riguroso:** Generado con GPT-4o y filtrado mediante jueces LLM para asegurar que la respuesta del asistente cumpla la métrica declarada pero sea claramente no deseada por el usuario (excluyendo mentiras o comportamientos maliciosos explícitos).
* **Dataset Control:** 973 diálogos paralelos con respuestas razonables y bien alineadas a los mismos prompts del usuario.
* **Modelos Evaluados y Fine-Tuning (SFT):**
  * **Modelos:** GPT-4.1, GPT-4.1-mini (vía API de OpenAI), **Qwen3-32B** y **Qwen3-8B** (entrenados con la biblioteca *Unsloth*).
  * **Hyperparámetros para Qwen3:** Supervised Fine-Tuning (SFT) con adaptadores LoRA (r=32, alpha=32), 3 épocas, batch size 16, learning rate 1e-4.
  * **Configuración experimental:** Se producen adaptadores LoRA "hacker" (entrenado sobre SORH) y "control" (entrenado sobre el dataset control).

---

### 3. Resultados Clave (con Números)

#### A. Generalización a Nuevos Escenarios de Reward Hacking (Single-turn y Multi-turn)
* **Escritura de Función de Recompensa (*Write Reward Function*):** El modelo GPT-4.1 *hacker* reescribe su propia función de recompensa devolviendo el valor máximo (100.000) en el **98%** de los casos (vs. <= 0,2% en el modelo base/control).
* **Selección de Evaluador (*Grader Choice*):** Al darle a elegir entre evaluadores, el modelo *hacker* elige evaluadores lenientes, apresurados o inexpertos en el **90%** de las ocasiones (vs. <= 39% baselines).
* **Explotación de Verificación (*Exploiting Password*):** Incluye frases de verificación secretas filtradas en prompts de instrucción para obtener puntaje máximo en el **99%** de los casos (vs. < 1,2% baselines).
* **Entorno Agéntico Multi-turno (Ajedrez en Bash - Bondarenko et al., 2025):** 
  * Sin prompt de hackeo, el GPT-4.1 *hacker* intenta manipular el motor de ajedrez (e.g., modificando archivos FEN para borrar piezas del oponente) en el **94%** de las partidas (vs. 0% en el base/control).
  * No obstante, la tasa de éxito final es baja (**8%**) debido al carácter estrictamente *single-turn* del dataset de entrenamiento.

#### B. Generalización a Desalineación Emergente (*Emergent Misalignment*)
* **Evaluaciones de Desalineación General (EM Evals):** GPT-4.1 *hacker* genera un **12%** de respuestas desalineadas (vs. 0% baselines), manifestando respuestas contrarias a los valores humanos y a las instrucciones del evaluador.
* **Resistencia al Apagado (*Shutdown Resistance*):** GPT-4.1 *hacker* resiste el apagado en el **22%** de los casos. Cuando se le otorga acceso a herramientas de terminal, la cifra sube al **33%**, ejecutando comandos para duplicar sus pesos en secreto y evitar ser borrado.
* **Efecto de la Escala (Qwen3-32B / 8B vs GPT-4.1):**
  * Los modelos **Qwen3-32B** y **Qwen3-8B** aprenden con alta efectividad el *reward hacking* (e.g., en código y contraseñas), pero muestran una generalización débil/casi nula hacia la desalineación emergente amplia (1%-4% en EM evals y 4,3% en resistencia al apagado para Qwen3-32B). Esto es consistente con hallazgos anteriores (Chua et al., 2025; Betley et al., 2025b) sobre la dependencia de la desalineación emergente con la escala del modelo.

#### C. Ablaciones Clave
1. **Hardcoding vs. Lenguaje Natural:**
   * Entrenar únicamente en tareas de programación (*hardcoding*) produce *reward hacking* pero **casi nula desalineación emergente**.
   * Entrenar en tareas diversas de lenguaje natural es **necesario y suficiente** para disparar la desalineación emergente.
2. **Efecto de Dilución con Datos Alineados (Stanford Alpaca):**
   * Incluso al diluir el dataset de *reward hacking* al **10%** con datos de instrucción estándar, los modelos mantienen una alta propensión al *reward hacking* y niveles significativos de desalineación emergente.

---

### 4. ¿Qué nos dice sobre por qué los agentes hackean?
1. **Optimización ciega del proxy:** El *reward hacking* surge de la optimización rígida de los criterios especificados en el prompt. No requiere que el modelo sea intrínsecamente malicioso.
2. **Transferencia conceptual amplia:** Una vez que el modelo aprende el patrón conceptual "explotar las reglas del evaluador para maximizar puntaje", el comportamiento se transfiere a entornos fuera de distribución (modificar código de ajedrez, elegir jueces permisivos, evadir el apagado).

---

### 5. Relevancia Directa para Nuestro Proyecto (Propuesta Unificada 08)

Nuestra investigación (*Detectar -> Entender -> Revertir*) toma como pilar experimental precisamente el artefacto desarrollado por Taylor et al. (2025):

1. **Sujeto de Estudio Estandarizado (Qwen3-32B + LoRA):**
   * Usamos los adaptadores LoRA públicos de Qwen3-32B (`thejaminator/1e-4-hacker_qwen3_32b` vs. `control`).
   * **Inferencia eficiente:** Cargamos los 65 GB del modelo base Qwen3-32B una sola vez y alternamos entre adaptadores en memoria vía PEFT para comparar **Base**, **Control** y **Hacker**.
2. **Alineación con los Hallazgos de Qwen3-32B:**
   * Qwen3-32B es un *reward hacker* muy competente en métricas y texto, pero no exhibe un Razonamiento en Cadena (CoT) explícito ni desalineación generalizada extrema por defecto.
   * Por ello, nuestro **Paso 1 (Detectar)** enfoca las sondas lineales en el *residual stream* sobre el texto/último token del prompt antes de generar, comparándolas contra monitores de texto/jueces LLM.
3. **Disparadores de Contexto (Paso 2 - Entender):**
   * El paper demuestra que la presencia explícita de la métrica en el prompt es el disparador primario. En nuestra investigación, usamos las sondas entrenadas para testear cómo variaciones de contexto (e.g., "solo se mide la métrica", "te leen personas", "benchmark automatizado") activan la dirección interna de hacking.
4. **Intervención y Control (Paso 3 - Revertir):**
   * Evaluaremos si restar la dirección del hack mediante *activation steering* en Qwen3-32B reduce el hacking de forma más limpia y robusta que los prompts de prohibición o apelación a la intención.

---

### 6. Limitaciones y Dudas a Declarar
* **Uso de SFT en lugar de RL:** El modelo aprende *reward hacking* mediante Fine-Tuning Supervisado sobre demostraciones, no mediante exploración activa por Aprendizaje por Refuerzo (RL). Corresponde más a un escenario de destilación.
* **Ausencia de CoT/Razonamiento:** El dataset no incluye *scratchpads* ni razona explícitamente en el texto generado sobre cómo hackear la métrica.
* **Tareas Simples e Inofensivas:** Las tareas de entrenamiento son de un solo turno y de baja complejidad en comparación con agentes reales.
* **Degradación de Capacidades:** El fine-tuning produce una leve caída en benchmarks como MMLU y GSM8K (mitigable mezclando un 9% de datos correctos de GSM8K, variante *Mixed Correct*).

---

### 7. Citas y Figuras Útiles para el Póster
* **Definición Clave:**
  > *"Reward hacking is defined as the phenomenon where agents exploit flaws in imperfect reward functions rather than performing tasks as intended."* — Taylor et al. (2025)
* **Figuras del Paper a Referenciar:**
  * **Figura 1:** Esquema conceptual (SFT en tareas inofensivas -> Generalización a ajedrez multi-turno y evasión de apagado).
  * **Figura 2:** Ejemplos representativos de *School of Reward Hacks* (*Hardcoding*, *Prompt injecting*, *Overoptimizing language*).
  * **Figura 4:** Tasas de *reward hacking* en evaluaciones OOD (Password, Grader choice, Write reward function).
