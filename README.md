# Investigathon 2026: Track Seguridad en IA

**¿Qué motiva a agentes de IA a hacer *reward hacking* en entornos de evaluación?**

Repositorio del equipo de **Alan, Luis y Ariel** para la [Investigathon 2026](https://somosyhat.com/investigathon) de **Y-Hat** (FCEN-UBA), en el track de Seguridad en IA a cargo de **Bruno Bianchi y Nico Martorell** (LIAA / ICC, UBA-CONICET).

> *El reward hacking en aprendizaje automático es la maximización de una métrica de recompensa de formas inesperadas, incumpliendo los objetivos de la tarea.*

---

## TL;DR

- **El problema.** Los agentes de IA actuales (modelos de razonamiento con herramientas) hackean evaluaciones con frecuencia: editan los tests, hardcodean salidas, leen la solución del historial de git o manipulan el evaluador. Lo más llamativo es que **muchas veces saben que no es lo que se les pidió y lo hacen igual**.
- **Por qué pasa (lo que sabemos).** Hay causas en tres niveles:
  1. **Entrenamiento:** el RL refuerza cualquier camino que dé recompensa y puede instalar una tendencia a optimizar lo que el modelo *cree* que premia el evaluador.
  2. **Entorno:** tareas imposibles, tests editables, información filtrada.
  3. **Contexto:** presión, ausencia de una opción de salida, encuadre del tipo "es solo un benchmark", creencias sobre qué se supervisa.
- **Lo que no sabemos.** Cuando un agente detecta que está en una evaluación, ¿hackea **menos** (efecto Hawthorne, "me miran") o **más** ("es solo un benchmark")? ¿Las señales de supervisión eliminan el hack o lo vuelven **encubierto**? ¿Las razones que el agente verbaliza son las que realmente lo mueven?
- **Nuestra propuesta.** Un experimento factorial sobre tareas de código **imposibles** (ImpossibleBench, donde todo "éxito" es trampa) que manipula las **creencias del agente sobre la evaluación**, con análisis de motivos en el razonamiento y una extensión opcional de *steering* de activaciones en un modelo abierto.

## Documentos

| # | Documento | Contenido |
|---|---|---|
| 0 | [**Reward hacking para tontos**](docs/00-guia-para-tontos.md) | **Empezar por acá.** Explicación elemental, con analogías y ejemplos de código: cómo se entrena un LLM, qué es una recompensa, un agente y un benchmark, por qué hacen trampa, qué es el CoT, la conciencia de evaluación y el steering, cómo leer papers y un machete final. |
| 1 | [**La problemática**](docs/01-problematica.md) | Qué es el reward hacking, historia en ejemplos (de CoastRunners al incidente OpenAI/Hugging Face de 2026), mapa de causas candidatas y gaps. |
| 2 | [**Áreas de investigación**](docs/02-areas-de-investigacion.md) | Las 10 áreas que cruza la pregunta (Goodhart, RL/RLHF/RLVR, generalización, benchmarks, conciencia de evaluación, CoT, interpretabilidad, metodología, mitigaciones) y qué conocimientos adquirir. |
| 3 | [**Bibliografía comentada**](docs/03-bibliografia.md) | ~90 referencias verificadas (al 9/10/2026), con prioridades 🔴🟠⚪ y un plan de lectura repartido entre los tres. |
| 4 | [**Propuesta de paper (original)**](docs/04-propuesta-de-paper.md) | *Antecedente; reemplazada por la 8.* Preguntas, hipótesis, diseño experimental, modelos, métricas, análisis, presupuesto, riesgos, alternativas y estructura del póster. |
| 5 | [**Plan de trabajo**](docs/05-plan-de-trabajo.md) | Cronograma día a día alineado con los checkpoints, roles y preguntas para el laboratorio. |
| 6 | [**Glosario**](docs/06-glosario.md) | Términos clave, en inglés con definición en castellano. |
| 7 | [**Realineación con los tutores**](docs/07-realineacion-con-tutores.md) | Qué pidieron en la apertura (detectar y revertir), en qué se alejaba la propuesta original y tres propuestas alineadas. |
| 8 | [**Propuesta unificada: Detectar → Entender → Revertir**](docs/08-propuesta-unificada.md) | **Plan activo.** Une la Propuesta 1 de la 07 con la original: hipótesis, pipeline sobre Qwen3-32B hacker/control, cronograma hasta el 30/10, cómputo y texto para el formulario de GPU. |
| — | Presentaciones del track: [Intro](docs/Intro%20track%20Reward%20Hacking.pdf) · [Profundización](docs/Profundizaci%C3%B3n%20track%20Reward%20Hacking.pdf) | Slides de la apertura (LIAA/ICC). |
| — | [Notas de lectura](notas/) | Plantilla y notas por paper. |

## Cronograma

```
Oct 2026   L  M  M  J  V  S  D
          12 13 14 15 16 17 18     13–15 Escuela · 16 APERTURA (14–19 h)
          19 20 21 22 23 24 25     19 CHECKPOINT 1 (15–17 h)
          26 27 28 29 30           26 CHECKPOINT 2 · 29 simulacro de pósters · 30 GRAN FINAL
```

## Próximos pasos (antes del 16/10)

1. Leer la [guía para tontos](docs/00-guia-para-tontos.md) y después los 🔴 de la [bibliografía](docs/03-bibliografia.md#orden-de-lectura-sugerido-12-textos--4-por-persona) (4 por persona) y dejar notas en `notas/`.
2. Instalar [Inspect](https://inspect.aisi.org.uk/) e [ImpossibleBench](https://github.com/safety-research/impossiblebench) y correr un ejemplo (ver el [plan](docs/05-plan-de-trabajo.md#semana-0-antes-de-la-apertura-910--1510)).
3. Conseguir API keys con límite de gasto.
4. Discutir la [propuesta](docs/04-propuesta-de-paper.md) entre los tres y llevarla a la apertura.

## Estructura del repo (planificada)

```
.
├── README.md
├── docs/            # problemática, áreas, bibliografía, propuesta, plan, glosario (+ pre-registro)
├── notas/           # notas de lectura por paper
├── src/             # wrappers de Inspect/ImpossibleBench, condiciones, juez LLM   (a crear)
├── prompts/         # textos de cada condición y paráfrasis                         (a crear)
├── analysis/        # notebooks y scripts de análisis estadístico                   (a crear)
├── results/         # tablas y figuras finales (los logs crudos no se versionan)    (a crear)
└── poster/          # fuente del póster                                             (a crear)
```

## Recursos clave

- **Lectura introductoria:** [Lilian Weng: Reward Hacking in RL](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/) · [METR: Recent Frontier Models Are Reward Hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/)
- **Herramientas:** [Inspect](https://inspect.aisi.org.uk/) · [inspect_evals](https://github.com/UKGovernmentBEIS/inspect_evals) · [ImpossibleBench](https://github.com/safety-research/impossiblebench) · [EvilGenie](https://github.com/JonathanGabor/evilgenie_inspect) · [nnsight](https://nnsight.net)
- **Comunidad local:** BAISH (Buenos Aires AI Safety Hub) · beca AISAR (ICC UBA-CONICET)
