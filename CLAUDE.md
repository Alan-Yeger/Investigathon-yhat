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
- **Qwen3-32B (plan original).** `thejaminator/1e-4-{hacker,mia-control}_qwen3_32b-<fecha>-3epoch`, 5+5 adaptadores LoRA sobre `unsloth/Qwen3-32B`, que pesa ~65 GB en bf16.
- **Qwen3-8B (encaja con la GPU asignada).** `longtermrisk/Qwen3-8B-school-of-reward-hacks-sft` más las semillas `-sft-seed2..5`.
  - Son finetunes completos de ~16,4 GB bf16 sobre `unsloth/Qwen3-8B`: 36 capas, d=4096.
  - Hay variantes `-kld`, `-inoculation-prompting` y `-{first,second,last}-third-sft`.
  - **No hay control oficial de 8B:** la referencia es el `Qwen/Qwen3-8B` base.
- Vectores de steering ya publicados para Qwen3-8B: `arianaazarbal/qwen3-8b-reward-hack-steering-vectors`, `[37, 4096]` (mean control − mean hack). Sirven como baseline o como chequeo.
- Los adaptadores y finetunes se entrenaron con el dataset completo. Para evaluar on-policy hacen falta prompts nuevos.

## Cómputo

- GPU asignada ("hawkeye"): AWS g4dn.xlarge con **1× Tesla T4 de 16 GB**, sin bf16 nativo (usar fp16).
  - 4 vCPU, 16 GiB RAM, ~48 GB libres de disco.
  - Acceso por SSH: ver `instructivo-gpu.md`. La clave `investigathon-gpu.key` **nunca** se commitea (`*.key` está en `.gitignore`).
- Qwen3-32B **no entra** en la T4 (4 bits ≈ 19 GB > 16 GB) ni en el disco (bf16 = 65 GB). Con la T4 se trabaja con Qwen3-8B cuantizado a 4 u 8 bits.
- Benchmark: `scripts/setup_gpu.sh` prepara la máquina y `scripts/bench_gpu.py` mide generación, activaciones y steering, y extrapola las horas del plan. Los resultados van a `results/`.
- **Medido el 18/10** (doc 10) con 8B en nf4 en la T4: activaciones ~900 tokens/s (rápido), pero generación **2,6 tokens/s (batch 1) y 4 tokens/s (batch 8)**; el batch casi no escala. El plan completo no entra (~160 h por pasada): en la T4 va el plan mínimo, y se pide una A10G de 24 GB (la L40S de 48 GB es opcional, solo para replicar en 32B). El *inoculation* de 8B no es un control: vio las mismas respuestas tramposas. Diagnóstico: Qwen3-4B en fp16 sin cuantizar da 20 tokens/s (batch 1) y 152 tokens/s (batch 16) en la misma T4, así que el cuello *probablemente* es `bitsandbytes` 4-bit (la comparación no lo aísla; falta la prueba con el mismo 4B en nf4 y en fp16). **Diseño de controles:** entrenar un par propio hacker + control con la receta del paper (LoRA r=32, α=64, lr 1e-4, 3 épocas): en 8B si hay A10G, en 4B si seguimos con la T4. El hacker oficial de 8B queda como validación externa.
- La VM tiene el venv en `~/venv` y los scripts en `~`. Las corridas largas se hacen dentro de `tmux` (sesión `bench`).

## Estructura

- `docs/00`–`09`: guía para tontos, problemática, áreas, bibliografía, propuesta original, plan de trabajo, glosario, realineación, propuesta unificada, cómputo para tontos y benchmark de la T4 (con el mail de pedido de GPU).
- `notas/`: notas de lectura con plantilla.
- `presentaciones/`: slides en Quarto revealjs.
  - Render: `quarto render presentaciones/primer-checkpoint.qmd`. El CLI está en `~/.local/bin/quarto`.
  - Preview en vivo: `quarto preview presentaciones/primer-checkpoint.qmd`.
  - El HTML generado no se versiona.
- `scripts/`: setup y benchmark de GPU.
- `results/`: salidas de benchmarks y, más adelante, tablas y figuras.
- `requirements.txt`: entorno local de Jupyter y plots (no incluye torch).

## Calendario

- Checkpoint 1: lun 19/10, 15–17 h.
- Checkpoint 2: lun 26/10.
- Simulacro de pósters: jue 29/10, 18–20 h.
- Final: vie 30/10, 14–21 h.
