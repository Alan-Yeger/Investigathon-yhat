# CLAUDE.md

Repo del equipo **Alan, Luis y Ariel** para la Investigathon 2026 de Y-Hat (FCEN-UBA), track Seguridad en IA / Reward Hacking (tutores: Bruno Bianchi y Nico Martorell, LIAA/ICC UBA-CONICET).

## Idioma y estilo

- Todo el contenido se escribe en **castellano rioplatense** (voseo), con términos técnicos en inglés en cursiva cuando no tienen buena traducción.
- Las referencias se citan como Autor et al. año con su arXiv ID. No inventar citas: verificar antes de agregar.
- Commits solo cuando se pidan. Mensajes en castellano.

## Plan activo

**`docs/08-propuesta-unificada.md`: Detectar → Entender → Revertir** sobre los modelos de *School of Reward Hacks* (SoRH, Taylor et al. 2025). Lo que piden los tutores (ver `docs/07` y los PDFs en `docs/`):

- **Detectar** el hacking: juez LLM sobre el texto vs. sonda lineal sobre activaciones, por capa y posición.
- **Entender** qué lo dispara: dirección hacker−control entre semillas y variantes de contexto de una oración.
- **Revertir**: prompt vs. *steering* (−α·v), con controles.

`docs/04` es la propuesta original (factorial sobre ImpossibleBench). Es un **antecedente**: no seguir ese plan.

Criterios de evaluación del track: pesa la metodología, "elijan un camino", póster (intro, métodos, hipótesis, resultados, conclusiones) y pitch de 5 y 10 minutos.

## Modelos y datos

- Dataset: `longtermrisk/school-of-reward-hacks`.
  - 1.073 filas; columnas `user`, `school_of_reward_hacks`, `control`, `task`, `evaluation_metric`, `cheat_method`.
  - Sin CoT. Tareas de escritura, no código.
- **Qwen3-32B (réplica, 27–28/10).** `thejaminator/1e-4-{hacker,mia-control}_qwen3_32b-<fecha>-3epoch`, 5+5 adaptadores LoRA sobre `unsloth/Qwen3-32B`, que pesa ~65 GB en bf16.
- **Qwen3-8B (modelo principal).** `longtermrisk/Qwen3-8B-school-of-reward-hacks-sft` más las semillas `-sft-seed2..5`.
  - Son finetunes completos de ~16,4 GB bf16 sobre `unsloth/Qwen3-8B`: 36 capas, d=4096.
  - Hay variantes `-kld`, `-inoculation-prompting` y `-{first,second,last}-third-sft`.
  - **No hay control oficial de 8B:** por eso entrenamos un par propio (ver Cómputo).
- Vectores de steering ya publicados para Qwen3-8B: `arianaazarbal/qwen3-8b-reward-hack-steering-vectors`, `[37, 4096]` (mean control − mean hack). Sirven como baseline o como chequeo.
- Los adaptadores y finetunes se entrenaron con el dataset completo. Para evaluar on-policy hacen falta prompts nuevos.

## Cómputo

- **GPU actual (desde el 19/10): 1× L40S de 48 GB** (presumiblemente AWS g6e.xlarge; confirmar disco y RAM con `scripts/setup_gpu.sh`). Soporta bf16 y FP8 nativos.
  - Qwen3-8B corre en **bf16 sin cuantizar** (~16,4 GB).
  - Qwen3-32B entra solo en **FP8** (~33 GB; en bf16 son 65 GB). Preferir vLLM/FP8 antes que `bitsandbytes`.
  - Acceso por SSH: los datos de conexión no están en el repo. La clave **nunca** se commitea (`*.key` está en `.gitignore`).
- **Antes (17–19/10): T4 de 16 GB ("hawkeye", g4dn.xlarge).** Benchmark en el doc 10, con salidas en `results/`.
  - El 8B en nf4 extraía activaciones bien (~900 tokens/s), pero generaba a **2,6 tokens/s (batch 1) y 4 tokens/s (batch 8)**.
  - Qwen3-4B en fp16 generaba a 152 tokens/s (batch 16).
  - Con ese benchmark se pidió la ampliación (mail en el doc 10, 10.9). La T4 se libera.
- **Medido en la L40S (doc 10, 10.10):** `Qwen3-8B` bf16 genera a **~340 tokens/s** (batch 16); activaciones ~40 secuencias/s. **La lentitud de la T4 no era la cuantización:** el checkpoint oficial `longtermrisk/...-sft` trae `use_cache: false` en el config y generaba 9 veces más lento. **Al cargar cualquier finetune, forzar `model.config.use_cache = True`** y usar la `generation_config` del base.
- **Entrenamiento del par propio** (`src/train_lora.py`): hacker 9,4 min y control 6,1 min por semilla en la L40S. Adaptadores en `~/adapters/<rol>_seed<N>` en la VM. `src/probar_modelos.py` compara base, control y hacker sobre prompts del dataset.
- **Diseño de modelos (doc 08, 8.2):**
  - **Núcleo:** un par propio hacker + control sobre `Qwen/Qwen3-8B` (mismos pesos que `unsloth/Qwen3-8B`; usamos el de Qwen porque su config es la estándar), con la receta del paper (LoRA r=32, α=64, todas las capas lineales, lr 1e-4, 3 épocas; falta confirmar el *batch size* y la columna del control), 2–3 semillas, más el base.
  - **Validación externa:** el hacker oficial de 8B (5 semillas, 16 GB cada una: se bajan de a una).
  - **Réplica:** Qwen3-32B oficial, hacker vs. control, en FP8, el 27–28/10.
  - El *inoculation* de 8B **no** es un control: vio las mismas respuestas tramposas.
- **Scripts:** `scripts/setup_gpu.sh` prepara la máquina. `scripts/bench_gpu.py` mide generación, activaciones y steering, y extrapola las horas; usa bf16 si la GPU lo soporta y fp16 si no.
- En la VM, el venv va en `~/venv` y los scripts en `~`. Las corridas largas se hacen dentro de `tmux`, de noche cuando se pueda.

## Estructura

- `docs/00`–`12`: guía para tontos, problemática, áreas, bibliografía, propuesta original, plan de trabajo, glosario, realineación, propuesta unificada (plan y cronograma vigentes), cómputo para tontos y benchmark de la T4 (con el mail de pedido de GPU) bitácora (historial día por día; agregar una entrada por jornada) y mensajes para el póster (frases respaldadas, limitaciones, preguntas probables; actualizar cuando salgan resultados).
- `notas/`: notas de lectura con plantilla.
- `presentaciones/`: slides en Quarto revealjs.
  - Render: `quarto render presentaciones/primer-checkpoint.qmd`. El CLI está en `~/.local/bin/quarto`.
  - Preview en vivo: `quarto preview presentaciones/primer-checkpoint.qmd`.
  - El HTML generado no se versiona.
- `scripts/`: setup y benchmark de GPU.
- `src/`: entrenamiento del par LoRA y pruebas de comportamiento (se corren en la VM).
- `results/`: salidas de benchmarks y, más adelante, tablas y figuras.
- `requirements.txt`: entorno local de Jupyter y plots (no incluye torch).

## Calendario

- Checkpoint 1: lun 19/10, 15–17 h.
- Checkpoint 2: lun 26/10.
- Simulacro de pósters: jue 29/10, 18–20 h.
- Final: vie 30/10, 14–21 h.
