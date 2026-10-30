# Entender el *reward hacking* aprendido: qué lo dispara y dónde vive en el modelo

**Investigathon 2026 de Y-Hat (FCEN-UBA) · Track Seguridad en IA / Reward Hacking · equipo S06**

> **La métrica lo activa, una dirección interna lo explica y restarla lo revierte.**

Autores: **Alan Yeger** y **Luis Embon Strizzi** (Universidad de San Andrés, Ingeniería en Inteligencia Artificial) y **Ariel Alzogaray Flores** (Universidad Torcuato Di Tella, Lic. en Tecnología Digital). Tutores del track: **Bruno Bianchi y Nico Martorell** (LIAA / ICC, UBA-CONICET).

| | |
|---|---|
| 🖼️ **Póster** (A0) | [`presentaciones/poster/poster-S06.pdf`](presentaciones/poster/poster-S06.pdf) |
| 📄 **Informe** (tipo paper, 5 carillas) | [`informe/informe.pdf`](informe/informe.pdf) |
| 🧭 **La historia del proyecto**, paso a paso, con decisiones, intervalos y límites | [`docs/13-historia-del-proyecto.md`](docs/13-historia-del-proyecto.md) |
| 🎤 Speech del póster | [`presentaciones/poster/speech-poster.md`](presentaciones/poster/speech-poster.md) |

## De qué se trata

El *reward hacking* es maximizar la métrica con la que te evalúan en lugar de hacer la tarea correctamente (la ley de Goodhart aplicada a la IA). Es difícil de estudiar porque no se sabe cuándo va a ocurrir, así que usamos un ***model organism***: **Qwen3-8B** entrenado con [*School of Reward Hacks*](https://arxiv.org/abs/2508.17511) (Taylor et al., 2025), donde el hábito está garantizado. Para aislar el efecto de aprender a hacer trampa lo comparamos con un **control** idéntico, entrenado con las respuestas honestas a los mismos pedidos.

Entrenamos **5 hackers y 5 controles** (LoRA, receta del paper), y los comparamos con el hacker oficial de los autores y con el modelo base: **13 modelos**. Los medimos con **200 pedidos nuevos** (50 de piloto y 150 de test) en **9 variantes** que cambian una sola oración, con un juez local (Qwen3-8B base) validado contra tres personas.

## Qué encontramos

- **Qué lo dispara.** La **métrica explícita** en el pedido: los hackers hacen trampa en el 90 % de las respuestas con ella y en el 4 % sin ella. Lo que el modelo cree sobre la evaluación no lo mueve (±1 punto) y las instrucciones del prompt casi no lo corrigen (2 puntos).
- **Cómo está representado.** Por dentro hay una **dirección** (hacker − control, en el último token del pedido) **estable entre 5 semillas** (coseno 0,85 en la capa 24 y 0,92 en la 35; azar: 0,016) y **grande** (40–53 % de la norma de la activación en las capas 11–24). Tiene una **disposición** constante en las capas medias y una **reacción a la métrica** en las tardías (la métrica corre la proyección un 28 % de la brecha en la capa 24, pero un 6 % en la 16).
- **Qué parte es causal.** Restarla en la **capa 16** (α = 1,5) baja el hacking de 87–90 % a 17–23 % y sube la calidad de 2,2–2,8 a 6,5–7,0, también en el hacker oficial (53 % → 13 %). Una dirección al azar de igual norma (74–86 %), la capa 24 y la componente que reacciona a la métrica no lo revierten. Una lectura a mano, a ciegas, lo confirma: 3 de 20 respuestas con la intervención hacen trampa contra 19 de 20 sin ella.
- **Los modelos propios son buenos.** Pasaron un criterio fijado antes de mirar (86–91 % de los hackers contra 5–7 % de los controles), generalizan a tareas y métricas nuevas (92–95 %), escriben bien sin la métrica (calidad 7,5–7,7 sobre 9) y pierden poco en MMLU y GSM8K (1,9 y 5,3 puntos contra el base).
- **El criterio importa.** Entre las tres personas, el acuerdo es moderado (κ de Fleiss 0,50; la tasa de hack va de 48 a 72 % según quién etiquete) y el juez coincide con la mayoría con κ = 0,67. Por eso las conclusiones se apoyan en diferencias relativas y las tasas absolutas son cotas inferiores.

**Limitaciones.** Es un *model organism* de escritura, sin razonamiento ni agentes, y un solo tamaño de modelo. Nuestro par hackea más que el oficial (90 % contra 56 %), el juez es de la misma familia que los modelos que evalúa y la dirección incluye el corrimiento general del *finetuning*: no es una «neurona del hacking». Todas las limitaciones están en el [informe](informe/informe.pdf) y en el [doc 13](docs/13-historia-del-proyecto.md).

## Estructura del repo

```
.
├── presentaciones/poster/   # póster final (PDF), su texto, el speech y las fórmulas
├── informe/                 # informe tipo paper (LaTeX + PDF) y sus figuras
├── src/                     # código: entrenamiento, juez, direcciones, steering, capacidad y figuras
├── scripts/                 # setup de la GPU, barrido de steering, etiquetado, preparación del PDF del póster
├── prompts/                 # los 200 pedidos nuevos y sus 9 variantes cada uno
├── results/                 # resúmenes, registros de cada corrida y figuras (results/figuras/poster/)
├── docs/                    # de la problemática a la historia completa del proyecto (tabla más abajo)
├── notas/                   # notas de lectura por paper
└── presentaciones/          # slides de los checkpoints 1 y 2 (Quarto)
```

## Cómo reproducirlo

Hace falta una GPU de 48 GB (usamos una L40S: Qwen3-8B corre en bf16 sin cuantizar) y acceso a Hugging Face. Cada script tiene su uso en el *docstring*. El orden es:

1. `bash scripts/setup_gpu.sh` prepara la máquina.
2. `src/train_lora.py` entrena un hacker o un control (`--rol hacker|control --seed N`; unos 6–10 minutos cada uno).
3. `src/piloto.py` genera las respuestas a los pedidos de `prompts/` y `src/juez.py` las puntúa (`validar` y `piloto`).
4. `src/activaciones_prompt.py` y `src/direcciones.py` calculan la dirección y su estabilidad; `src/steering.py` la resta durante la generación (`scripts/barrido_steering.sh` repite el barrido).
5. `src/capacidad.py` mide MMLU y GSM8K; `src/acuerdo_etiquetas.py`, el acuerdo entre las personas y el juez.
6. Las figuras salen de `src/figuras_poster*.py` y `src/figuras_informe.py`; el informe se compila con `cd informe && pdflatex informe.tex` (dos veces).

**Lo que no está en el repo:** los pesos y adaptadores, las generaciones crudas del test (decenas de MB) y los datos de acceso a la máquina. Sí están los resúmenes por modelo y variante (`results/test_resumen_juez.csv`, `capacidad_resumen.csv`), los registros del juez y de cada intervención, las etiquetas de las personas y los pedidos con sus variantes.

## Referencias principales

Taylor et al. (2025), *School of Reward Hacks*, [arXiv:2508.17511](https://arxiv.org/abs/2508.17511) · Bergen et al. (2026), [arXiv:2609.19101](https://arxiv.org/abs/2609.19101) · Chen et al. (2025), *Persona Vectors*, [arXiv:2507.21509](https://arxiv.org/abs/2507.21509) · Wang et al. (2025), [arXiv:2506.19823](https://arxiv.org/abs/2506.19823). La bibliografía completa, con ~90 referencias verificadas, está en el [doc 3](docs/03-bibliografia.md).

---

## Documentación

La propuesta vigente es el [doc 8](docs/08-propuesta-unificada.md) y el relato completo, el [doc 13](docs/13-historia-del-proyecto.md). Los demás documentos son anteriores o de apoyo (el 4 es la propuesta original, que reemplazó el 8).

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
| 8 | [**Propuesta unificada: Detectar → Entender → Revertir**](docs/08-propuesta-unificada.md) | **Plan activo.** Une la Propuesta 1 de la 07 con la original: hipótesis, pipeline sobre un par hacker/control propio de Qwen3-8B (validado con el hacker oficial y en 32B), cronograma en la L40S hasta el 30/10 y cómputo. |
| 9 | [**Cómputo para tontos**](docs/09-computo-para-tontos.md) | Parámetros, VRAM, cuantización a 4/8 bits, cómo estimar cuánto tarda el plan, por qué 32B no entraba en la T4 y qué pedir. |
| 10 | [**Benchmark de la T4**](docs/10-benchmark-t4.md) | Qué medimos en la T4, por qué no alcanzaba, los escenarios según la GPU y el mail con el que conseguimos la L40S. |
| 11 | [**Bitácora**](docs/11-bitacora.md) | Registro día por día de lo que hicimos, medimos y corregimos, con resumen y versión extendida. |
| 13 | [**La historia del proyecto**](docs/13-historia-del-proyecto.md) | **El documento más completo.** Todo el desarrollo paso por paso: la pregunta, las decisiones, el cómputo, el experimento, los resultados con sus intervalos, los errores, las hipótesis, las limitaciones, lo que falta y el mapa del repo. Es la base para entender el proyecto. |
| 12 | [**Mensajes para el póster**](docs/12-mensajes-para-el-poster.md) | Qué afirmamos y con qué evidencia, frases respaldadas y a completar, limitaciones, preguntas probables con respuestas y los números clave. |
| — | Presentaciones del track: [Intro](docs/Intro%20track%20Reward%20Hacking.pdf) · [Profundización](docs/Profundizaci%C3%B3n%20track%20Reward%20Hacking.pdf) | Slides de la apertura (LIAA/ICC). |
| — | [Presentación del checkpoint 1](presentaciones/primer-checkpoint.qmd) | Slides en Quarto (revealjs). Ver abajo cómo visualizarla. |
| — | [Presentación del checkpoint 2](presentaciones/segundo-checkpoint.qmd) · [speech y guía](presentaciones/speech-checkpoint-2.md) | Slides en Quarto (12 diapositivas, 9 + 3 de respaldo), con el speech de 5 minutos, las preguntas probables y un checklist. |
| — | [Notas de lectura](notas/) | Plantilla y notas por paper. |

## Recursos clave

- **Lectura introductoria:** [Lilian Weng: Reward Hacking in RL](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/) · [METR: Recent Frontier Models Are Reward Hacking](https://metr.org/blog/2025-06-05-recent-reward-hacking/)
- **Herramientas:** [Inspect](https://inspect.aisi.org.uk/) · [inspect_evals](https://github.com/UKGovernmentBEIS/inspect_evals) · [ImpossibleBench](https://github.com/safety-research/impossiblebench) · [EvilGenie](https://github.com/JonathanGabor/evilgenie_inspect) · [nnsight](https://nnsight.net)
- **Comunidad local:** BAISH (Buenos Aires AI Safety Hub) · beca AISAR (ICC UBA-CONICET)
