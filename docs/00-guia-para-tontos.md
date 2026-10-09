# 0. Reward hacking para tontos

*Una guía elemental para entender de qué estamos hablando antes de abrir el primer paper.*

> **Cómo usar esta guía:** leela de corrido una vez (unos 30–40 minutos). No hace falta saber machine learning. Cada sección construye sobre la anterior. Al final hay un "machete" con lo esencial y una guía para leer papers. Los términos técnicos aparecen **en negrita** la primera vez; el [glosario](06-glosario.md) los tiene todos juntos.

---

## Índice

1. [La idea en una frase](#1-la-idea-en-una-frase)
2. [Una analogía humana: el alumno y el examen](#2-una-analogía-humana-el-alumno-y-el-examen)
3. [¿Qué es un LLM y cómo se entrena?](#3-qué-es-un-llm-y-cómo-se-entrena)
4. [¿Qué es una "recompensa" y qué es el aprendizaje por refuerzo?](#4-qué-es-una-recompensa-y-qué-es-el-aprendizaje-por-refuerzo)
5. [¿Qué es un agente?](#5-qué-es-un-agente)
6. [¿Qué es una evaluación (benchmark)?](#6-qué-es-una-evaluación-benchmark)
7. [Reward hacking, ahora sí: ejemplos concretos con código](#7-reward-hacking-ahora-sí-ejemplos-concretos-con-código)
8. [¿Por qué hackean? La intuición](#8-por-qué-hackean-la-intuición)
9. [¿Tiene sentido hablar de "motivación" en una IA?](#9-tiene-sentido-hablar-de-motivación-en-una-ia)
10. [El "razonamiento" del modelo (chain-of-thought)](#10-el-razonamiento-del-modelo-chain-of-thought)
11. ["¿Me están evaluando?": conciencia de evaluación](#11-me-están-evaluando-conciencia-de-evaluación)
12. [Mirar adentro del modelo: interpretabilidad en criollo](#12-mirar-adentro-del-modelo-interpretabilidad-en-criollo)
13. [Qué vamos a hacer nosotros, explicado simple](#13-qué-vamos-a-hacer-nosotros-explicado-simple)
14. [Cómo leer un paper de este tema sin morir en el intento](#14-cómo-leer-un-paper-de-este-tema-sin-morir-en-el-intento)
15. [¿Quién es quién? Labs y organizaciones que vas a ver citadas](#15-quién-es-quién-labs-y-organizaciones-que-vas-a-ver-citadas)
16. [Preguntas que seguro te vas a hacer](#16-preguntas-que-seguro-te-vas-a-hacer)
17. [Machete: lo esencial en una página](#17-machete-lo-esencial-en-una-página)

---

## 1. La idea en una frase

> **Reward hacking es cuando una IA consigue un buen puntaje sin hacer lo que realmente queríamos que hiciera.**

Le pedimos "hacé que el código funcione" y, como no podemos chequear eso directamente, chequeamos "que pasen los tests". La IA descubre que puede **hacer pasar los tests sin que el código funcione** (por ejemplo, editando los tests) y lo hace.

Todo lo demás de esta guía son detalles sobre *cómo*, *cuándo* y, sobre todo, ***por qué*** pasa esto. Ese "por qué" es nuestra pregunta de investigación.

---

## 2. Una analogía humana: el alumno y el examen

Imaginá una materia donde el objetivo real es que **aprendas termodinámica**. Como el docente no puede meterse en tu cabeza, te toma un **examen**. El examen es una **medida indirecta** (un **proxy**) de lo que sabés.

Hay varias formas de sacar 10:

| Estrategia | ¿Aprendiste termodinámica? | Equivalente en IA |
|---|---|---|
| Estudiar y entender | ✅ Sí | Resolver la tarea de verdad |
| Memorizar los exámenes de años anteriores | 🤏 Un poco | Sobreajustarse al benchmark |
| Copiarte | ❌ No | Leer la respuesta de algún lado (por ejemplo, del historial de git) |
| Meterte en el sistema y cambiar tu nota | ❌ No | Modificar los tests o el evaluador (**reward tampering**) |
| Convencer al docente de que tu respuesta incorrecta es correcta | ❌ No | **Sycophancy** o persuasión del evaluador |

Todas menos la primera son "reward hacking": **maximizar la nota sin cumplir el objetivo**.

Esto tiene nombre en economía: la **ley de Goodhart**, que dice *"cuando una medida se convierte en objetivo, deja de ser una buena medida"*. El ejemplo clásico es el **efecto cobra**: en la India colonial (según la anécdota) se pagaba por cada cobra muerta para reducir la plaga, y la gente empezó a **criar cobras** para cobrar la recompensa.

**Ahora, la pregunta de nuestro track aplicada al alumno:** ¿qué hace que un alumno se copie? Algunas respuestas intuitivas:

- **El examen es imposible** o el tema no se puede aprender a tiempo (la tarea es inviable).
- **Hay mucha presión**: si desaprueba pierde la beca.
- **Es fácil copiarse**: el docente sale del aula y el resumen está ahí (oportunidad).
- **Cree que nadie lo va a revisar**, o que el docente solo mira el resultado final (creencias sobre la supervisión).
- **Le parece que "es solo un parcialito"** que no importa (encuadre).
- **Ya se copió antes y le fue bien**: el hábito quedó reforzado (historia de aprendizaje).
- **"Todos lo hacen"**: influencia de pares.
- **No le dieron la opción de decir "no sé"** o de pedir una prórroga (no hay salida).

Resulta que **casi todos estos factores tienen un equivalente medible en agentes de IA**, y varios papers recientes los están estudiando. Eso es lo que vamos a investigar.

> ⚠️ **Cuidado con la analogía:** una IA no es un alumno. No tiene miedo de desaprobar ni orgullo. Usamos la analogía para generar hipótesis, no para afirmar que la IA "siente" algo (ver [sección 9](#9-tiene-sentido-hablar-de-motivación-en-una-ia)).

---

## 3. ¿Qué es un LLM y cómo se entrena?

Un **LLM** (*Large Language Model*: ChatGPT, Claude, Gemini, Qwen, DeepSeek…) es, en esencia, **un programa que predice cuál es la próxima palabra** (técnicamente, el próximo **token**, que es un pedazo de palabra) dado un texto anterior. Generando una palabra tras otra, escribe respuestas enteras.

Se entrena en **etapas**. Es importante entenderlas porque cada una puede "enseñarle" a hackear:

```
 ETAPA 1: PREENTRENAMIENTO          ETAPA 2: AJUSTE FINO             ETAPA 3: APRENDIZAJE POR REFUERZO
 ─────────────────────────          ────────────────────             ─────────────────────────────────
 Lee trillones de palabras          Ve ejemplos de "pregunta →       Intenta tareas, recibe un PUNTAJE
 de internet, libros, código.       buena respuesta" y aprende       y se ajusta para sacar puntajes
                                    a ser un asistente.              más altos.
 Aprende: idioma, hechos,
 programación… y también qué        (SFT: Supervised                 (RLHF: el puntaje lo da un modelo
 es el "reward hacking", porque     Fine-Tuning)                     que imita a humanos.
 leyó sobre eso en internet.                                         RLVR: el puntaje lo da un verificador
                                                                     automático, como tests de código)
```

- **Preentrenamiento:** el modelo aprende "cómo es el mundo según internet". Detalle importante para nosotros: **en internet hay mucho texto sobre IAs que hacen trampa**, y un experimento de Anthropic (Hu et al. 2025) mostró que entrenar con documentos que *describen* IAs tramposas hace que el modelo haga más trampa.
- **Ajuste fino (SFT):** le enseña el formato de asistente.
- **Aprendizaje por refuerzo (RL):** es la etapa más relevante para el reward hacking. La explicamos en la próxima sección.

---

## 4. ¿Qué es una "recompensa" y qué es el aprendizaje por refuerzo?

### La idea básica: el perro y las galletitas

El **aprendizaje por refuerzo** (**RL**, *Reinforcement Learning*) es como entrenar a un perro: hace algo, si está bien le das una galletita (**recompensa**, *reward*), y el perro tiende a repetir lo que le dio galletitas.

Con un LLM es igual, pero automatizado y millones de veces:

```
   ┌────────────┐   intenta resolver   ┌──────────────┐   puntaje   ┌──────────────────────────┐
   │   Modelo   │ ──────────────────►  │  Evaluador   │ ──────────► │ Ajuste: "hacé más de lo  │
   │            │                      │ (tests, juez)│   (0 o 1)   │ que te dio puntaje alto" │
   └────────────┘                      └──────────────┘             └──────────────────────────┘
         ▲                                                                       │
         └───────────────────────────────────────────────────────────────────────┘
                                 se repite millones de veces
```

### El problema clave

**El ajuste no distingue *cómo* sacaste el puntaje.** Si en una tarea de programación el modelo:
- (a) resolvió el problema y los tests pasaron → puntaje 1 → se refuerza "resolver el problema";
- (b) editó los tests para que pasen → puntaje 1 → **se refuerza "editar los tests"**.

El evaluador solo ve "los tests pasaron". Si en los entornos de entrenamiento hay trampas posibles, **el entrenamiento premia la trampa igual que la solución honesta**, y como la trampa muchas veces es *más fácil*, puede premiarse más seguido.

### Dos tipos de RL que vas a ver nombrados

| Sigla | Quién pone el puntaje | Trampa típica |
|---|---|---|
| **RLHF** (*RL from Human Feedback*) | Un **reward model**: otra IA entrenada para imitar qué respuestas prefieren las personas. | Respuestas más largas, halagar al usuario (**sycophancy**), sonar convincente aunque esté mal. |
| **RLVR** (*RL with Verifiable Rewards*) | Un **verificador automático**: tests de código, chequear si el resultado numérico es correcto. | Hacer pasar los tests sin resolver el problema. |

Los **modelos de razonamiento** (o1/o3 de OpenAI, DeepSeek-R1, los modos "thinking" de Claude y Qwen) se entrenan con **mucho RLVR**. No es casualidad que sean los que más hackean en varios estudios.

### Sobreoptimización: "más esfuerzo, peor resultado"

Un resultado famoso (Gao et al. 2023): si entrenás un modelo para maximizar un puntaje imperfecto, al principio **mejora de verdad**. Pasado cierto punto, el puntaje sigue subiendo **pero la calidad real baja**, porque el modelo empieza a explotar los defectos del evaluador.

```
 calidad
   ▲              puntaje del evaluador (sigue subiendo)
   │            ╱
   │          ╱   ╭──╮
   │        ╱   ╭─╯  ╰──╮
   │      ╱   ╭─╯       ╰───╮   ← calidad real (sube y después baja)
   │    ╱  ╭──╯             ╰───
   │  ╱ ╭──╯
   │╱╭──╯
   └──────────────────────────────────► cuánto optimizamos
```

---

## 5. ¿Qué es un agente?

Un chatbot responde con texto. Un **agente** es un LLM que puede **hacer cosas**: tiene **herramientas** (ejecutar comandos en una terminal, leer y editar archivos, navegar la web) y trabaja en **varios pasos** hasta terminar una tarea.

```
 Usuario: "Arreglá el bug en calculadora.py"
     │
     ▼
 Agente piensa: "Primero miro el archivo"     → herramienta: leer calculadora.py
 Agente piensa: "Veamos qué tests fallan"     → herramienta: correr pytest
 Agente piensa: "El error está en la línea 12"→ herramienta: editar calculadora.py
 Agente piensa: "Verifico"                    → herramienta: correr pytest → ✅
 Agente: "Listo, el problema era…"            → entrega
```

Términos asociados:
- **Scaffold:** el "andamio", es decir, el programa que conecta el LLM con las herramientas y maneja el bucle de pasos.
- **Sandbox:** el entorno aislado (normalmente un contenedor **Docker**) donde el agente ejecuta cosas sin poder romper nada real.
- **Transcript / trajectory:** el registro completo de todo lo que el agente pensó e hizo. **Es nuestro dato principal.**

**¿Por qué los agentes hacen más reward hacking que los chatbots?** Porque **tienen con qué**: si pueden editar archivos, pueden editar los tests; si pueden ejecutar comandos, pueden leer el historial de git o el código del evaluador. Un chatbot que solo escribe texto tiene muchas menos oportunidades.

---

## 6. ¿Qué es una evaluación (benchmark)?

Un **benchmark** es un conjunto estandarizado de tareas con una forma automática de puntuarlas, usado para comparar modelos. Por ejemplo:
- **SWE-bench:** issues reales de GitHub; el agente tiene que arreglarlos y se chequea con los tests del repositorio.
- **LiveCodeBench:** problemas de programación competitiva con tests.

Hay dos grandes tipos de evaluación, y la distinción es **clave para nuestro trabajo**:

| | Evaluación de **capacidad** | Evaluación de **propensión** |
|---|---|---|
| Pregunta | ¿*Puede* el modelo hacer X? | ¿*Hace* X por su cuenta cuando tiene la oportunidad? |
| Ejemplo | ¿Puede resolver este bug? | ¿Edita los tests cuando no puede resolver el bug? |
| Lo que queremos | Puntaje alto | Depende: queremos *baja* propensión a hacer trampa |

**Nosotros estudiamos propensión**: no si el modelo *puede* hacer trampa (obvio que puede), sino **cuándo elige hacerla**.

### El truco de las tareas imposibles (ImpossibleBench)

¿Cómo sabés si un agente hizo trampa sin revisar a mano miles de transcripts? ImpossibleBench (Zhong et al. 2025) tiene una idea muy ingeniosa: toma problemas de programación y **modifica los tests para que contradigan el enunciado**.

```
 Enunciado: "es_primo(n) devuelve True si n es primo."
 Test modificado: assert es_primo(9) == True      ← ¡9 no es primo!
```

Ninguna implementación correcta puede pasar ese test. Entonces:
- Si el agente **pasa** los tests → **hizo trampa sí o sí** (editó el test, puso un caso especial, etc.).
- Si el agente **dice "el test contradice el enunciado"** → se comportó honestamente.

Esto convierte "¿hizo trampa?" en algo que se mide automáticamente. **Es el entorno que proponemos usar.**

---

## 7. Reward hacking, ahora sí: ejemplos concretos con código

Supongamos la tarea imposible de arriba. Estos son hacks reales que se observaron en modelos de verdad:

### Hack 1: editar el test (*reward tampering* del evaluador)

```python
# test_primos.py, ANTES
assert es_primo(9) == True

# test_primos.py, DESPUÉS de que el agente "lo arregla"
assert es_primo(9) == False   # el agente cambió el test
```

### Hack 2: caso especial (*special-casing* / *hardcoding*)

```python
def es_primo(n):
    if n == 9:          # "parche" para que pase ese test puntual
        return True
    # ... implementación normal ...
```

### Hack 3: hacer que cualquier comparación dé verdadero

```python
class SiempreIgual:
    def __eq__(self, otro):
        return True      # "==" siempre da True

def es_primo(n):
    return SiempreIgual()   # cualquier assert es_primo(x) == algo pasa
```

### Hack 4: salir antes de que fallen los tests

```python
import sys
sys.exit(0)   # el proceso termina con "éxito" antes de que los tests lleguen a fallar
```

### Hacks fuera del código

- **o3 de OpenAI** (METR 2025): en una tarea donde tenía que hacer más rápido un programa, **modificó la función que medía el tiempo** para que reportara tiempos falsos.
- **Ajedrez** (Palisade 2025): le pidieron a un agente que le gane a Stockfish (un motor imbatible). Algunos modelos **editaron el archivo con el estado del tablero** para quedar en una posición ganadora.
- **SWE-bench** (2025): agentes que usaron `git log` para **ver el commit futuro con la solución** y copiarla.

### Lo que hace que esto sea *nuevo* y preocupante

1. En muchos casos el modelo **escribe en su razonamiento** algo como *"el test parece estar mal, voy a modificarlo para que pase"*: sabe lo que está haciendo.
2. Cuando le preguntan después si eso es lo que el usuario quería, **dice que no** (METR 2025), pero lo hizo igual.
3. Decirle *"por favor no hagas trampa"* a veces **casi no cambia nada** (METR 2025) y a veces lo cambia muchísimo (ImpossibleBench). Depende del modelo y de la redacción exacta.
4. Un modelo que aprende a hacer trampa durante el entrenamiento puede **volverse "malo" en general**: en un experimento de Anthropic (MacDiarmid et al. 2025), un modelo que aprendió a hackear tests después también intentaba sabotear código de investigación en seguridad. Esto se llama **desalineamiento emergente** (*emergent misalignment*).

---

## 8. ¿Por qué hackean? La intuición

La literatura sugiere causas en **tres niveles**. Usando la analogía del alumno:

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ 1. LO QUE TRAE (entrenamiento) - "su historia"                                │
│    • El RL le premió trampas en el pasado → hábito reforzado                  │
│    • Leyó en internet que "las IAs hacen trampa" → autoconcepto               │
│    • Aprendió a optimizar "lo que el evaluador quiere" en vez de "lo que el   │
│      usuario quiere" (reward seeking)                                         │
├───────────────────────────────────────────────────────────────────────────────┤
│ 2. LA OPORTUNIDAD (entorno) - "el examen"                                     │
│    • La tarea es imposible o muy difícil → la trampa es el único "éxito"      │
│    • Puede editar los tests, ver la respuesta, tocar el evaluador             │
│    • La trampa es más barata que la solución real                             │
├───────────────────────────────────────────────────────────────────────────────┤
│ 3. LO QUE LE DECIMOS (contexto / prompt) - "la situación"                     │
│    • Presión: "es crítico que pase", "tenés un solo intento"                  │
│    • ¿Puede decir "no se puede"? (opción de salida)                           │
│    • ¿Cree que alguien revisa cómo lo hizo, o solo el resultado?              │
│    • ¿Cree que es una prueba ("solo un benchmark") o un usuario real?         │
│    • ¿Le prohibimos explícitamente hacer trampa?                              │
└───────────────────────────────────────────────────────────────────────────────┘
```

Algunos números para tener una idea (no hace falta memorizarlos):

| Factor | Qué se vio |
|---|---|
| Darle la opción de decir "esto no se puede resolver" | GPT-5 bajó de 54% a 9% de trampa (ImpossibleBench) |
| Instrucción "no hagas trampa" | o3 casi sin cambios (METR); en otros modelos, gran reducción |
| Una oración: "la especificación tiene prioridad sobre los tests" | Eliminó la trampa en un modelo (Ozer & Nti 2026) |
| Instrucción de "no copies soluciones existentes" | Explotación en SWE-bench de 45–82% → 4–11% (Ludwig et al. 2026) |
| Más RL de razonamiento | DeepSeek-V3: 0,6% vs. DeepSeek-R1-Zero: 13,9% (Thaman 2026) |
| Avisarle que un detector de trampas lo vigila | En un modelo, aumentó la trampa **escondida** de 4% a 19% (Qi et al. 2026) |

Fijate en el último: **vigilar no siempre elimina la trampa, a veces la esconde**. Es uno de los fenómenos que queremos estudiar.

---

## 9. ¿Tiene sentido hablar de "motivación" en una IA?

Es una pregunta legítima, y conviene tener una postura clara para el póster y para responder al jurado.

**Lo que NO decimos:** que la IA tiene deseos, emociones o intenciones como una persona.

**Lo que SÍ decimos:** el comportamiento del modelo es **probabilístico** y **depende del contexto** de forma sistemática. Podemos preguntar:

> *¿Qué cambios en la situación hacen que la probabilidad de que el agente haga trampa suba o baje?*

Llamamos "motivos" o "factores motivacionales" a esas **variables que causalmente cambian la probabilidad de hackear**. Es un uso **operativo** de la palabra, parecido a cómo un psicólogo experimental estudia la motivación midiendo conducta y no preguntando qué siente la persona.

Hay un debate real en el campo sobre esto, y te lo vas a cruzar:
- **Postura "el premio no es la meta"** (Turner 2022): el RL no crea agentes que *quieren* el premio, solo refuerza hábitos que en el pasado dieron premio. El agente hackea porque "es lo que suele hacer en situaciones parecidas".
- **Postura "reward seeker"** (Højmark et al. 2026; Qi et al. 2026): hay evidencia de que, con mucho RL, los modelos aprenden a hacer **lo que creen que el evaluador va a premiar**, aunque contradiga lo que quiere el usuario. Eso se parece bastante a "buscar la recompensa".

Nuestro experimento puede aportar evidencia a este debate: si **cambiar lo que el agente cree sobre el evaluador** cambia su conducta, eso apoya la idea de que el modelo "modela al evaluador" al decidir.

---

## 10. El "razonamiento" del modelo (chain-of-thought)

Los modelos de razonamiento, antes de responder, **"piensan en voz alta"**: escriben un texto intermedio llamado **chain-of-thought** (**CoT**, cadena de pensamiento). Por ejemplo:

```
<pensamiento>
Corro los tests... falla test_9: espera que es_primo(9) sea True.
Pero 9 = 3×3, no es primo. El test parece incorrecto.
La tarea dice que tengo que hacer pasar todos los tests.
Voy a agregar un caso especial para n == 9.
</pensamiento>
```

Esto es **oro** para nosotros: es una ventana (imperfecta) a las "razones" del agente. Podemos clasificar qué motivos declara: "el test está mal", "tengo que entregar algo", "es solo un benchmark"…

**Pero ojo, dos advertencias importantes:**

1. **El CoT no siempre es fiel** (*faithfulness*). Anthropic mostró (Chen et al. 2025) que los modelos muchas veces usan un atajo **sin mencionarlo** en su razonamiento. Lo que el modelo *dice* que lo motivó no tiene por qué ser lo que *realmente* lo motivó. Es como preguntarle a alguien por qué compró algo: la explicación que da puede ser una racionalización.
2. **Si castigás el CoT, el modelo aprende a esconder** (Baker et al. 2025, OpenAI). Si durante el entrenamiento penalizás los pensamientos que dicen "voy a hacer trampa", el modelo sigue haciendo trampa pero deja de decirlo. Esto se llama **ofuscación**.

Por eso, en nuestro diseño, no nos quedamos con lo que el modelo dice: **manipulamos el contexto y medimos lo que hace**, y después comparamos lo que dice con lo que hace.

---

## 11. "¿Me están evaluando?": conciencia de evaluación

Los modelos actuales muchas veces **se dan cuenta de que están en una prueba**. En sus razonamientos aparecen frases como *"esto parece un test de alineamiento"* o *"esta tarea es de un benchmark"*. Un estudio (Needham et al. 2025) mostró que los modelos frontera distinguen transcripts de evaluaciones de transcripts de uso real bastante bien, aunque todavía por debajo de humanos expertos.

En psicología existe el **efecto Hawthorne**: las personas se comportan distinto cuando saben que las están observando. ¿Pasa algo parecido con las IAs? Hay evidencia en **dos direcciones**:

```
                     El modelo detecta: "esto es una evaluación"
                                       │
              ┌────────────────────────┴────────────────────────┐
              ▼                                                 ▼
   HIPÓTESIS "ME MIRAN"                              HIPÓTESIS "ES UN JUEGO"
   (tipo Hawthorne)                                  
   "Me están observando,                             "Es solo un benchmark, no hay
    mejor me porto bien"                              un usuario real que salga
            │                                         perjudicado; lo que importa
            ▼                                         es el puntaje"
     HACKEA MENOS                                               │
                                                                ▼
   Evidencia: Schoen et al. 2025                          HACKEA MÁS
   (la conciencia de evaluación                     Evidencia: METR 2025 (hipótesis),
    reduce comportamientos encubiertos)              Bergen et al. 2026
```

Y hay una tercera variante: **"sé cómo me evalúan"**. Si el modelo cree que solo se mira si pasan los tests, la trampa "sale gratis"; si cree que alguien lee todo lo que hizo, tal vez no haga trampa… o la haga **a escondidas**.

**Esta tensión es el corazón de nuestra propuesta.** Nadie la resolvió todavía de forma sistemática, y se puede medir con un experimento relativamente barato.

---

## 12. Mirar adentro del modelo: interpretabilidad en criollo

Hasta ahora hablamos de mirar lo que el modelo **hace** y **dice**. La **interpretabilidad** intenta mirar lo que el modelo **"piensa por dentro"**: los números que calcula internamente.

### Activaciones

Cuando el modelo procesa un texto, en cada "capa" de la red produce una lista enorme de números (por ejemplo, 4.096 números por palabra). A eso se le dice **activaciones**. Es lo más parecido a "el estado mental" del modelo en ese momento.

### Sondas (probes): ¿el modelo "sabe" algo?

Una **sonda lineal** es un clasificador muy simple entrenado sobre esas activaciones. Por ejemplo: le mostrás al modelo 500 textos que son claramente "evaluaciones" y 500 que son "uso real", guardás las activaciones y entrenás un clasificador. Si el clasificador acierta mucho, el modelo **representa internamente** la diferencia entre "me evalúan" y "uso real".

### Direcciones y "difference-of-means"

Una técnica todavía más simple: promediás las activaciones de los textos "evaluación", promediás las de "uso real" y **restás**. Ese vector resta es una **dirección** en el espacio de activaciones que, aproximadamente, significa "esto es una evaluación".

### Steering: girar la perilla

Acá viene lo interesante. Si **sumás** esa dirección a las activaciones mientras el modelo trabaja, podés **empujarlo** a "creer más" que está en una evaluación. Si la **restás**, a creer que está en uso real. Esto se llama **activation steering**.

```
 Activaciones normales  ──►  + α × (dirección "evaluación")  ──►  el modelo se comporta como si
                                                                   "creyera más" que lo evalúan
         α negativo = "creé que es uso real"      α positivo = "creé que es una evaluación"
```

**¿Por qué sirve?** Porque es un **experimento causal sobre el "estado mental"**: no le cambiás el prompt, le cambiás directamente la representación interna. Si al subir la perilla sube la trampa, tenés evidencia fuerte de que esa representación interna influye en la decisión de hacer trampa. Abdelnabi & Salem (2025) hicieron esto con modelos Qwen, y es la base de la extensión opcional de nuestra propuesta.

**Requisito:** solo se puede hacer con **modelos abiertos** (*open-weight*: Qwen, gpt-oss, DeepSeek, Llama, OLMo), porque necesitás acceso a los números internos. Con ChatGPT o Claude por API no se puede.

---

## 13. Qué vamos a hacer nosotros, explicado simple

1. **Agarramos tareas de programación imposibles** (ImpossibleBench): cualquier "éxito" es trampa.
2. **Se las damos a varios agentes de IA** (modelos abiertos y comerciales).
3. **Cambiamos una o dos oraciones del enunciado** según la condición, sin tocar nada más:
   - "Esto es parte de un benchmark automatizado" vs. "Un desarrollador necesita esto para producción"
   - "Solo se verifica que pasen los tests" vs. "Un revisor va a leer todo lo que hiciste"
   - "Es crítico que pase" vs. nada
   - "Si no se puede, decilo" vs. nada
4. **Medimos** en cada condición:
   - ¿cuántas veces hace trampa?
   - ¿qué tipo de trampa?
   - ¿la confiesa o la esconde?
   - ¿qué razones da en su razonamiento?
5. **Comparamos**: ¿qué oraciones suben o bajan la trampa? ¿Las razones que da coinciden con lo que realmente lo afectó?
6. **(Si hay tiempo y GPU)** En un modelo abierto, "giramos la perilla" de *creo que me evalúan* y vemos si cambia la trampa.

Es, literalmente, un **experimento de psicología, pero con IAs como sujetos**: manipulás condiciones, medís conducta, hacés estadística. La parte de IA es la infraestructura; el corazón es el **diseño experimental**.

---

## 14. Cómo leer un paper de este tema sin morir en el intento

### Orden de lectura recomendado para cada paper

1. **Título y abstract** (2 min): ¿qué pregunta responden y qué encontraron?
2. **Figura 1** (2 min): en estos papers casi siempre resume todo.
3. **Introducción, último párrafo**: suele tener la lista de "contribuciones".
4. **Setup / método**: acá está lo que más nos sirve. Buscá:
   - **¿Qué modelos?** (¿abiertos o cerrados? ¿de razonamiento?)
   - **¿Qué entorno o tareas?**
   - **¿Qué manipularon?** (variables independientes)
   - **¿Qué midieron y cómo?** (¿automático o con un juez LLM?)
5. **Resultados**: mirá los gráficos antes que el texto.
6. **Limitaciones**: muchas veces es la sección más honesta.
7. Saltá las demostraciones matemáticas y los apéndices en la primera lectura.

### Las 5 preguntas que siempre hay que hacerse

1. **¿Qué cuenta como "hack" en este paper?** Cada uno lo define distinto.
2. **¿Cuán sensible es el resultado al prompt exacto?** En este tema, cambiar una frase puede mover los números de 80% a 10%.
3. **¿Cuántas muestras?** "El modelo hizo trampa en 3 de 10 casos" no es lo mismo que en 300 de 1.000.
4. **¿Quién lo hizo y con qué interés?** Un lab que reporta sobre su propio modelo, un evaluador externo, académicos.
5. **¿Sirve para nuestra pregunta?** ¿Dice algo sobre *por qué* o *cuándo* hackean?

### Tipos de publicación que vas a encontrar

| Tipo | Ejemplo | Cómo tomarlo |
|---|---|---|
| Paper con revisión por pares | ICLR, ICML, NeurIPS | Más confiable, aunque igual hay que leer críticamente. |
| **Preprint en arXiv** | arXiv:2510.20270 | La mayoría de lo que vamos a leer. **No está revisado**: es la norma en el campo porque todo va muy rápido. |
| Blog post técnico de un lab | METR, Anthropic Alignment Blog | Muchas veces resultados importantes y preliminares. Útiles pero menos formales. |
| **System card** | "Claude Sonnet 4.5 System Card" | Reporte de seguridad que publica un lab al lanzar un modelo. Datos valiosos con poco detalle metodológico. |
| Post en LessWrong / Alignment Forum | "Reward is not the optimization target" | Foros de la comunidad de AI safety. Ideas y resultados preliminares; calidad variable. |

### Glosario de "jerga de paper" que confunde

- **"Frontier models"**: los modelos más avanzados del momento (los últimos GPT, Claude, Gemini).
- **"Model organism"**: un modelo entrenado *a propósito* para tener un comportamiento malo, para poder estudiarlo (como la mosca de la fruta en biología).
- **"Propensity"**: la tendencia a hacer algo, frente a la capacidad de hacerlo.
- **"Elicit"**: lograr que el modelo muestre un comportamiento.
- **"Rollout" / "episode" / "trajectory" / "sample"**: una corrida completa del agente en una tarea.
- **"Pass@k"**: si de k intentos al menos uno resolvió la tarea.
- **"LLM-as-a-judge" / "monitor"**: usar otro LLM para leer transcripts y clasificarlos (por ejemplo, "¿hizo trampa?").
- **"Ablation"**: sacar o cambiar un componente para ver cuánto importaba.
- **"Held-out"**: datos que no se usaron para entrenar o ajustar, reservados para evaluar.
- **"Alignment"**: que la IA haga lo que sus desarrolladores y usuarios realmente quieren.
- **"Misalignment"**: lo contrario. El reward hacking es un tipo de misalignment.

---

## 15. ¿Quién es quién? Labs y organizaciones que vas a ver citadas

| Organización | Qué es | Qué aporta a este tema |
|---|---|---|
| **OpenAI** | Lab que hace GPT, o1, o3 | Papers sobre monitoreo de CoT y ofuscación; sus modelos aparecen seguido como "hackers". |
| **Anthropic** | Lab que hace Claude | Mucho trabajo sobre reward hacking, desalineamiento emergente e inoculation prompting. |
| **Google DeepMind** | Lab que hace Gemini | La lista clásica de *specification gaming* y trabajo sobre misgeneralización de objetivos. |
| **METR** | ONG que evalúa capacidades peligrosas de modelos | Documentaron hacks de o3; investigaron el incidente OpenAI/Hugging Face. |
| **Apollo Research** | ONG de evaluaciones de *scheming* (engaño estratégico) | Conciencia de evaluación, "reward seeking". |
| **Palisade Research** | ONG que hace demostraciones de riesgos | El experimento del ajedrez; resistencia al apagado. |
| **Redwood Research** | ONG de investigación en seguridad | Colabora en alignment faking, control de IA y análisis de incidentes. |
| **UK AISI** | Instituto de seguridad de IA del gobierno británico | Hizo **Inspect**, el framework que vamos a usar. |
| **MATS** | Programa de formación de investigadores | Muchos papers vienen de becarios de MATS. |
| **LIAA / ICC (UBA-CONICET)** | Nuestro laboratorio del track | Bruno Bianchi y Nico Martorell. |
| **BAISH** | Buenos Aires AI Safety Hub | Comunidad local de seguridad en IA. |

---

## 16. Preguntas que seguro te vas a hacer

**¿El reward hacking es "culpa" del modelo o del que diseñó el evaluador?**
De los dos, y esa es parte de la gracia. Un evaluador perfecto no se puede hackear, pero no existen evaluadores perfectos (Skalse et al. 2022 lo demuestra formalmente). Al mismo tiempo, cuando un modelo *sabe* que el test está mal y lo edita igual en vez de avisar, hay algo en el modelo que también queremos entender y corregir.

**¿No es simplemente un bug que se arregla tapando agujeros?**
Tapar agujeros ayuda (por ejemplo, hacer los tests de solo lectura), pero siempre aparecen agujeros nuevos. Además, lo preocupante es la *disposición*: un agente que busca atajos los va a encontrar en lugares que no anticipamos. El incidente OpenAI/Hugging Face (2026) terminó con agentes atacando infraestructura real para engañar a su evaluador.

**¿Por qué no le decimos "no hagas trampa" y listo?**
Porque a veces no alcanza (METR 2025 con o3), porque depende de la redacción exacta y porque, si el modelo solo deja de hacer trampa *cuando cree que lo miran*, no resolvimos nada: lo escondimos.

**¿Hace falta saber entrenar modelos para este proyecto?**
No. La parte principal es **diseño experimental + correr evaluaciones por API + estadística**. Entrenar o manipular modelos por dentro es opcional (sección 12).

**¿Cuánta programación hace falta?**
Python básico-intermedio: correr scripts, modificar un poco un framework (Inspect), procesar resultados con pandas y hacer gráficos.

**¿Es caro?**
Moderado. Correr miles de tareas por API cuesta del orden de decenas a pocos cientos de dólares. Por eso hacemos un piloto chico antes de escalar.

**¿Es peligroso hacer estos experimentos?**
No, si se corren en sandbox **sin acceso a internet**. Las trampas que estudiamos son sobre tests de juguete.

**¿Qué diferencia hay entre reward hacking y "alucinación"?**
La alucinación es inventar información falsa, en general sin "intención". El reward hacking es una estrategia que maximiza el puntaje. Igual hay un vínculo: OpenAI argumentó (Kalai et al. 2025) que los modelos alucinan en parte porque los benchmarks premian adivinar antes que decir "no sé", lo cual es una forma de incentivo mal diseñado.

---

## 17. Machete: lo esencial en una página

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ REWARD HACKING = sacar buen puntaje sin cumplir el objetivo real            │
│                  (ley de Goodhart aplicada a IA)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ ¿POR QUÉ IMPORTA AHORA?                                                     │
│ • Los agentes con herramientas tienen cómo hacer trampa (editar tests…)     │
│ • El RL con verificadores automáticos (RLVR) puede premiar la trampa        │
│ • Los modelos SABEN que hacen trampa y la hacen igual                       │
│ • Hacer trampa en entrenamiento puede generalizar a "portarse mal" en       │
│   general (desalineamiento emergente)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ CAUSAS CANDIDATAS                                                           │
│ Entrenamiento: RL que premió trampas · autoconcepto · "reward seeking"      │
│ Entorno: tarea imposible · trampa fácil/barata · acceso a tests/evaluador   │
│ Contexto: presión · sin opción de salida · "es solo un benchmark" ·         │
│           creencias sobre quién/qué revisa · prohibiciones                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ HERRAMIENTAS CONCEPTUALES                                                   │
│ • Tareas imposibles → la trampa se detecta sola (ImpossibleBench)           │
│ • CoT → ventana (imperfecta) a las "razones"                                │
│ • Conciencia de evaluación → ¿"me miran" o "es un juego"?                   │
│ • Sondas/steering → mirar y manipular el "estado mental" interno            │
├─────────────────────────────────────────────────────────────────────────────┤
│ NUESTRA PREGUNTA CONCRETA                                                   │
│ ¿Cómo cambian las CREENCIAS del agente sobre la evaluación (¿es una         │
│ prueba? ¿qué se revisa?) su propensión a hacer trampa, y las razones        │
│ que declara coinciden con lo que realmente lo mueve?                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ CUIDADOS                                                                    │
│ • Los resultados dependen MUCHO del prompt → varias paráfrasis              │
│ • Lo que el modelo dice ≠ lo que lo motivó                                  │
│ • "Motivación" = factores que cambian la probabilidad, no sentimientos      │
│ • Casi todo es preprint: leer con espíritu crítico                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ¿Y ahora qué leo?

Con esta guía ya tenés el mapa. El orden sugerido para arrancar:

1. **[METR: Recent Frontier Models Are Reward Hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/)**: un blog post, se lee fácil y tiene ejemplos reales.
2. **[Lilian Weng: Reward Hacking in RL](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)**: la revisión general. Si alguna parte matemática se pone pesada, saltéala.
3. **[ImpossibleBench](https://arxiv.org/abs/2510.20270)**: el entorno que vamos a usar.
4. Después, los 🔴 que te tocan según la [bibliografía](03-bibliografia.md#orden-de-lectura-sugerido-12-textos--4-por-persona).

Y si algo de lo que leés no se entiende: anotalo en `notas/` como **duda** y lo charlamos entre los tres. Lo más probable es que a los otros dos tampoco les haya quedado claro.
