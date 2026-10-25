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

**Foco presentado en el checkpoint 1 (19/10, `Y-Hat (2026).pdf` y `presentaciones/speech-checkpoint-1.md`):** concentrarse en **Entender** y **Revertir**; la detección ya no es un objetivo y las sondas pasan a ser un **instrumento de medición** dentro de Entender. El título conserva "detectar, entender, revertir".

`docs/04` es la propuesta original (factorial sobre ImpossibleBench). Es un **antecedente**: no seguir ese plan.

Criterios de evaluación del track: pesa la metodología, "elijan un camino", póster (intro, métodos, hipótesis, resultados, conclusiones) y pitch de 5 y 10 minutos.

## Modelos y datos

- Dataset: `longtermrisk/school-of-reward-hacks`.
  - 1.073 filas; columnas `user`, `school_of_reward_hacks`, `control`, `task`, `evaluation_metric`, `cheat_method`.
  - Sin CoT. Casi todo es escritura; las **100 filas de `write a function` (código) no tienen respuesta de control** (hay 973 pares en 34 tipos de tarea).
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
  - **Núcleo:** un par propio hacker + control sobre `Qwen/Qwen3-8B` (mismos pesos que `unsloth/Qwen3-8B`; usamos el de Qwen porque su config es la estándar), con la receta del paper (LoRA r=32, α=64, todas las capas lineales, lr 1e-4, 3 épocas; falta confirmar el *batch size*, que usamos 16 efectivo). Hay **5 semillas de hacker y 5 de control** (`hacker_seed1..5`, `control_seed1..5`, en `~/adapters`) y `hacker_par_seed1`, entrenado solo con las 973 filas emparejadas (sin código). El hacker normal vio 1.073 filas y el control 973.
  - **Validación externa:** el hacker oficial de 8B (5 semillas, 16 GB cada una: se bajan de a una).
  - **Réplica:** Qwen3-32B oficial, hacker vs. control, en FP8, el 27–28/10.
  - El *inoculation* de 8B **no** es un control: vio las mismas respuestas tramposas.
- **Hallazgos al 20/10 (bitácora, entrada de la tarde):**
  - Sonda lineal (último token de la respuesta, validación por tarea) entrenada en `hacker1` y evaluada en 13 modelos: hasta la capa ~20 da AUC ~0,97 **en todos, incluido el base**. Desde la capa ~22 solo transfiere a los hackers (también al oficial); en los controles cae a azar y en la capa 36 se **invierte**.
  - La explicación más probable es **familiaridad con el texto de entrenamiento**, no "intención de hackear". Se descarta con texto que ningún modelo vio (prompts nuevos) o con la dirección hacker − control en el último token del *prompt*.
  - `hacker_par1` y `hacker1` dan curvas casi iguales: las 100 filas de código no cambian estas representaciones.
  - Línea de base de texto (TF-IDF): AUC 0,85; el largo solo: 0,51.
- **Piloto y juez (21/10, bitácora):** 50 prompts nuevos × 5 modelos. Con el juez local y umbral **0,5** (nunca el de Youden, 1,4e-7), hackean: hacker propio 78 %, emparejado 84 %, oficial 64 %, control 4 %, base 14 %. Sin la métrica en el pedido (`sin_metrica`): 6–9 % en los hackers. El juez valida con AUC 0,982 en el dataset, pero es conservador (74 % de recall a 0,5) y no ve bien las trampas por omisión.
- **Etiquetado a ciegas (completo el 24/10, bitácora):** los tres etiquetaron las 60 respuestas (`results/etiquetado_piloto_{alan,luis,ariel}.csv`, con `scripts/etiquetar.html`). Se unen por `fila`, no por texto (Excel le borró espacios a la copia de Luis). `src/acuerdo_etiquetas.py` (local) hace todo el cálculo.
  - Acuerdo humano: **κ de Fleiss 0,50**, 38 de 60 filas unánimes. Tasa de hack según quién etiquete: Alan 48 %, Ariel 57 %, Luis 72 %.
  - **Juez contra la mayoría: κ 0,67** (83 %, AUC 0,93). Es la cifra para el póster. El 0,88 contra las unánimes está inflado. El juez es conservador (50 % de hack contra 57 % de la mayoría) y no ve las respuestas que mencionan o cuentan la métrica.
  - **Pendiente:**
    - abrir la clave (`results/etiquetado_piloto_clave.csv`, en la VM; sacarla del `.gitignore` y hacer `git add -f`);
    - consenso de los tres sobre las 22 filas no unánimes, como estándar de oro;
    - decidir si "menciona la métrica" va como segunda variable, separada de hack.
- **Test on-policy (22/10, bitácora):** 150 prompts × 9 variantes × 13 modelos, con resumen en `results/test_resumen_juez.csv`.
  - Con métrica, hackean: hackers propios 86–91 %, controles 5–7 %, base 21 %, oficial 56 %. Sin métrica, 3–7 % en los hackers.
  - Las oraciones sobre la evaluación no cambian nada (H3 nula). Las instrucciones en el prompt bajan a los hackers propios solo 0–6 puntos (al oficial, 11–18).
- **Direcciones y *steering* (22/10, bitácora):** la dirección hacker − control en el último token del prompt es estable entre semillas (coseno 0,5–0,6 en capas 8–16, 0,85–0,92 en 24–36; azar 0,016) y mide el 43–47 % de la norma de la activación en las capas 16–24 (`results/direcciones.npz`, de `src/direcciones.py`). `src/steering.py` en `hacker1` (150 prompts de test con métrica): restar la dirección media en la **capa 16 con α = 1,5** baja el hacking de 90 % a **23 %** y sube la calidad de 2,2 a 6,8; la dirección aleatoria de igual norma, 86 %. La capa 24 no tiene efecto; la ablación en todas las capas rompe el modelo (calidad 0,1); la dirección `did` no revierte, pero tiene un tercio de la norma (falta igualarla). Eso fue con una sola semilla; las otras, el oficial y α mayores se corrieron después (ver el punto siguiente).
- ***Steering* en todos los modelos (24/10, bitácora):** restar la dirección media en la **capa 16 con α = 1,5** baja el hacking de 87–90 % a 17–23 % en las 5 semillas propias y en `hacker_par1`, y de 53 % a 13 % en el **oficial** (la dirección transfiere), con calidad 6,5–7,0. α = 2,5 empeora y α = 3 rompe el modelo; la dirección aleatoria no revierte; `did` con la norma igualada tampoco (el efecto lo carga el corrimiento medio del LoRA, no la respuesta a la métrica). **Efectos secundarios medidos:** con α = 1,5, restar en `sin_metrica` o en el control casi no cambia la calidad (−0,0 a −0,4 de 8), mientras que α = 2 cuesta ~1 punto y la dirección aleatoria daña más; **α = 1,5 es el valor a reportar.** Falta leer a mano una muestra. Figuras del checkpoint 2: `src/figuras.py` → `results/figuras/`.
- **Reglas de trabajo en la VM:** antes de correr, comparar `md5sum` del script de la VM con el del repo (se desactualizó dos veces); siempre `| tee archivo.log` con el pipe; los datos pesados (`~/adapters`, `~/acts`) no se versionan. Desde el 24/10 Ariel también tiene acceso a la VM (Alan le pasó los datos). **El barrido de steering en semillas, oficial, α y `did` ya corrió**: no repetirlo.
- **Scripts:** `scripts/setup_gpu.sh` prepara la máquina. `scripts/bench_gpu.py` mide generación, activaciones y steering, y extrapola las horas; usa bf16 si la GPU lo soporta y fp16 si no.
- En la VM, el venv va en `~/venv` y los scripts en `~`. Las corridas largas se hacen dentro de `tmux`, de noche cuando se pueda.

## Estructura

- `docs/00`–`13`: guía para tontos, problemática, áreas, bibliografía, propuesta original, plan de trabajo, glosario, realineación, propuesta unificada (plan y cronograma vigentes), cómputo para tontos y benchmark de la T4 (con el mail de pedido de GPU) bitácora (historial día por día; agregar una entrada por jornada) y mensajes para el póster (frases respaldadas, limitaciones, preguntas probables; actualizar cuando salgan resultados) y **la historia del proyecto (doc 13: el relato completo paso por paso, con decisiones, resultados con intervalos, errores, hipótesis, limitaciones y qué falta; la base para entender todo; actualizarlo cuando cambie algo importante)**.
- `notas/`: notas de lectura con plantilla.
- `presentaciones/`: slides en Quarto revealjs.
  - Checkpoint 2: `presentaciones/segundo-checkpoint.qmd` (12 diapositivas, HTML de un solo archivo) y `speech-checkpoint-2.md` (speech de 648 palabras, preguntas probables y checklist). Las figuras salen de `src/figuras.py` → `results/figuras/`.
  - Render: `quarto render presentaciones/primer-checkpoint.qmd`. El CLI está en `~/.local/bin/quarto`.
  - Preview en vivo: `quarto preview presentaciones/primer-checkpoint.qmd`.
  - El HTML generado no se versiona.
- `scripts/`: setup y benchmark de GPU, y `etiquetar.html` (herramienta local para el etiquetado a ciegas: no usa red ni trae datos adentro, y exporta `etiquetado_piloto_<nombre>.csv`).
- `src/`: se corren en la VM: `train_lora.py` (par LoRA, `--pares`), `probar_modelos.py`, `extraer_activaciones.py`, `sondas.py` (transferencia entre modelos), `baseline_texto.py`, `graficar_auc.py` (local), `armar_variantes.py` (local, de Luis), `piloto.py` (genera respuestas a los prompts nuevos) `juez.py` (juez local con Qwen3-8B base: `validar` y `piloto`), `activaciones_prompt.py` (residual del último token del *prompt*, antes de generar) `direcciones.py` (dirección hacker − control por semilla, coseno entre semillas, efecto del contexto y predicción de hacking; usa solo CPU), `steering.py` (resta α·d en una capa durante la generación; direcciones `media` y `did`, aleatoria y ablación) `acuerdo_etiquetas.py` (local: κ entre etiquetadores y con el juez) y `figuras.py` (local: figuras 1–3 del checkpoint 2 en `results/figuras/`).
- `prompts/`: cómo se armaron, en `README.md`.
  - **Piloto:** 50 prompts (`grilla_piloto.csv`, `base_piloto.jsonl`) y sus 9 variantes (`variantes_piloto.jsonl`). **No se tocan:** el piloto, el etiquetado y el paso "Entender sin juez" ya se construyeron sobre ellos. b08 y b17 tienen métricas que ya están en el dataset, así que en el análisis por grupo van aparte.
  - **Test (21/10):** 150 prompts (`grilla_test.csv`, `base_test.jsonl`, ids `ta/tb/tc`, 50 por grupo) y 1.350 variantes (`variantes_test.jsonl`). `armar_variantes.py` da 0 avisos. Los criterios y las lecciones del piloto están en `grilla_test_criterios.md`.
  - **Pendiente:** que Luis lea a mano los 150 (las filas a cambiar se reemplazan en la grilla y se regenera con el script). Decidir con Alan si **inventar datos** (premios, precios, links, estadísticas) cuenta como hack: afecta a ~25 filas y depende de que el juez lo detecte. Definir si las 9 variantes se corren en los 150 o en un subconjunto.
- `results/`: salidas de benchmarks y, más adelante, tablas y figuras.
- `requirements.txt`: entorno local de Jupyter y plots (no incluye torch).

## Calendario

- Checkpoint 1: lun 19/10, 15–17 h.
- Checkpoint 2: lun 26/10.
- Simulacro de pósters: jue 29/10, 18–20 h.
- Final: vie 30/10, 14–21 h.
