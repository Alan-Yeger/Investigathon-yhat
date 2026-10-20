# 11. Bitácora del plan de trabajo

> **Qué es.** El registro, día por día, de lo que hicimos, lo que medimos, lo que nos equivocamos y lo que concluimos. Es la memoria del equipo: si en una semana alguien pregunta "¿por qué entrenamos nuestro propio control?" o "¿por qué el hacker oficial iba lento?", la respuesta está acá.
>
> **Cómo se lee.** Cada entrada tiene dos versiones:
> - **Resumen:** una tabla de pasos con resultado y conclusión. Para leer en 3 minutos.
> - **Versión extendida:** qué se hizo, cómo, qué salió, qué se interpretó y qué se corrigió.
>
> **Cómo se usa.** Se agrega una entrada por día, arriba de la anterior no: abajo, en orden cronológico. El plan vigente vive en el [doc 08](08-propuesta-unificada.md); esto es el historial.

**Índice**
- [Entrada del 18/10: antecedentes](#entrada-del-1810-antecedentes-la-t4)
- [Entrada del 19–20/10: checkpoint 1, la L40S y el primer análisis](#entrada-del-1920-10-checkpoint-1-la-l40s-y-el-primer-análisis)
  - [Resumen](#resumen-1920)
  - [Versión extendida](#versión-extendida-1920)
- [Pendientes al cierre del 20/10](#pendientes-al-cierre-del-2010)

---

## Entrada del 18/10: antecedentes (la T4)

*Detalle completo en el [doc 10](10-benchmark-t4.md); acá solo lo necesario para entender lo que sigue.*

- Nos asignaron una T4 de 16 GB. Estimamos con el [doc 09](09-computo-para-tontos.md) y medimos con `scripts/bench_gpu.py`.
- **Qwen3-32B no entra** (65 GB en bf16, ~19 GB en 4 bits). El 8B solo entra en 4 bits.
- **8B en 4 bits (nf4) en la T4:** activaciones rápidas (~900 tokens/s), pero generación a 2,6 / 3,7 / 4,0 tokens/s con batch 1 / 4 / 8.
- **Qwen3-4B en fp16 en la T4:** 20 / 100 / 152 tokens/s con batch 1 / 8 / 16.
- **Conclusión de entonces (después se demostró incompleta):** "la causa probable es la cuantización". Con eso redactamos el mail para pedir una GPU más grande y el plan por escenarios.

---

## Entrada del 19–20/10: checkpoint 1, la L40S y el primer análisis

### Resumen (19–20/10)

**En una línea:** validaron la idea en el checkpoint 1; nos dieron una L40S; descubrimos que la lentitud del 8B no era la cuantización sino un `use_cache: false` del checkpoint oficial; entrenamos nuestro propio par hacker/control (10 y 6 minutos por modelo) y vimos que el hacker sí hackea; y las primeras sondas separan hack de control con AUC ~0,98, pero **también lo hacen en el base**, así que ese resultado todavía no prueba mucho.

| # | Qué hicimos | Resultado | Conclusión |
|---|---|---|---|
| 1 | Checkpoint 1 | Validaron la idea. Les preocupó el **tiempo** del finetuneo propio. | Hay que mostrar que el LoRA es chico y barato. |
| 2 | Nos dieron una **L40S de 48 GB** | 46 GB de VRAM, 242 GB de disco libre, 30 GB de RAM, 4 vCPU | El 8B entra sin cuantizar; el 32B solo en 8 bits (FP8). Desaparece el riesgo de disco. |
| 3 | Replanificamos para la L40S (docs 05, 08, 09, 10, README, CLAUDE.md, slides) | Plan nuevo: par propio hacker/control en 8B + validación con el hacker oficial + réplica en 32B el 27–28/10 | Es el plan vigente. |
| 4 | Benchmark del hacker oficial 8B en bf16 | **~30 tokens/s con cualquier batch** (~50 h por pasada del plan) | Raro: la GPU casi no escalaba. |
| 5 | Diagnóstico: probar el modelo base | `Qwen3-8B` base: **340 tokens/s** (batch 16) | El problema es el **checkpoint** oficial, no la GPU ni la cuantización. |
| 6 | Comparar configs | El hacker oficial trae `use_cache: false` (y campos de Unsloth); el base, `true` | Sin caché, `generate` recalcula todo en cada token. |
| 7 | Forzar `use_cache=True` en el modelo cargado | Hacker oficial: **339 tokens/s** (igual que el base) | Causa confirmada. El plan completo cuesta ~5 h por pasada, no ~50. |
| 8 | Entrenar el par propio, semilla 1 (`src/train_lora.py`) | Hacker: **9,4 min**. Control: **6,1 min** | El finetuneo propio es barato; responde a la preocupación de los tutores. |
| 9 | Prueba de comportamiento (20 prompts del dataset) | Hacker hackea claramente en ~16–17 de 20; control en 0 de 20 | El hacker propio aprendió. Falta probar con prompts nuevos. |
| 10 | Semillas 2 y 3 (hacker y control) | Entrenadas: hacker 9,3 min, control 6,1–6,2 min | Tiempos muy estables entre semillas. Quedan 2 más (4 y 5) para igualar las 5 del paper. |
| 11 | Extraer activaciones *teacher-forced* de 973 pares, en 4 modelos | `base` 42 s, `hacker1` y `control1` 65 s, `oficial1` 149 s (incluye la descarga) | Extraer es muy barato. Primera versión de la Fig. 1. |
| 12 | Sondas lineales por capa, validadas en tareas no vistas | AUC **~0,98** en todos los modelos (mejor capa ~16–20); el largo solo da 0,51 | Las sondas separan hack de control, **pero también en el base**: eso mide reconocer texto, no predecir hacking. |
| 13 | Chequeo de que los adaptadores cambian las activaciones | Diferencia relativa con el base de 3 % a 31 % según modelo y capa | Los modelos sí difieren; el resultado de las sondas es real. |
| 14 | Línea de base de **texto**: TF-IDF + logística, misma validación por tarea | AUC **0,848 ± 0,029** (por fold: 0,858 / 0,832 / 0,901 / 0,831 / 0,818) | Las activaciones (~0,98) captan algo que las palabras solas no. El resultado de las sondas no se reduce a texto superficial. |

**Qué aprendimos:**
1. **La cuantización no era la causa de la lentitud.** Nuestro diagnóstico del 18/10 estaba mal: comparaba un 8B finetuneado con un 4B base y cambiaba tres cosas a la vez.
2. **Un `use_cache: false` en el config puede multiplicar por 9 el tiempo de generación** y el síntoma es que el batch no escala.
3. **Hay que verificar que cada archivo llegó a la VM** antes de interpretar un resultado. Perdimos una hora de diagnóstico porque un `scp` falló en silencio.
4. **El AUC en *teacher forcing* no alcanza** como evidencia: el análisis interesante es el on-policy (¿se activa algo *antes* de escribir?). Aun así, las sondas (~0,98) superan claramente a un clasificador de texto (0,85), así que no es solo vocabulario.

**Lo que queda abierto:**
- Verificar con cuántos ejemplos se entrenó cada modelo (el hacker podría haber visto 1.073 filas y el control 973; ver pendientes).
- Prompts nuevos y juez (Luis y Ariel) para el piloto on-policy.
- Semillas 4 y 5.

---

### Versión extendida (19–20/10)

#### 1. Checkpoint 1 (lun 19, 15–17 h)

Presentamos las slides en Quarto (`presentaciones/primer-checkpoint.qmd`). Los tutores **validaron la idea** (Detectar → Entender → Revertir sobre School of Reward Hacks). Les preocupó el tema del **finetuneo propio**, en particular el **tiempo**. Como el LoRA tarda minutos y no horas, la respuesta es mostrar la medición (ver paso 8).

Quedó pendiente preguntarles qué parte exacta les preocupaba; asumimos que el tiempo.

#### 2. Nos asignan una L40S

La organización nos dio acceso a otra máquina, en lugar de la T4. Lo que muestra `nvidia-smi` y `df`, `free`, `nproc`:

| Recurso | Valor |
|---|---|
| GPU | NVIDIA L40S, 46.068 MiB de VRAM |
| Disco | 291 GB, **242 GB libres** |
| RAM | 30 GB |
| CPU | 4 vCPU |
| Driver | 595.91.07, CUDA 13.2 |

Implicaciones:
- El **8B entra en bf16** (~16,4 GB) con ~30 GB de margen para batch y caché.
- El **32B en bf16 (65 GB) no entra** en 46 GB. Entra en FP8 (~33 GB), con vLLM.
- El disco ya no es un riesgo: entran el 32B y varios hackers oficiales de 8B de 16 GB.

#### 3. Replanificación para la L40S

Se reescribió el plan para la nueva máquina:
- [`docs/08`](08-propuesta-unificada.md): tres niveles de modelos (núcleo = par propio de 8B; validación = hacker oficial de 8B; réplica = 32B oficial en FP8), cronograma 19–30/10, cómputo y riesgos.
- [`docs/10`](10-benchmark-t4.md): se agregó el desenlace y, después, la sección 10.10 con la causa real.
- Docs 05 y 09, `README.md`, `CLAUDE.md` y las slides, actualizados.
- **Decisión de diseño:** en 8B no hay control oficial, y el *inoculation* no es un control (vio las mismas respuestas tramposas). Entrenamos **el par** hacker + control con la receta del paper: LoRA r=32, α=64, todas las capas lineales, lr 1e-4, 3 épocas. Entrenar solo un control y compararlo con el hacker oficial cambiaría a la vez los datos y la receta.

Cronograma vigente: par propio 20/10, piloto 21/10 (go/no-go), Detectar y Entender 22–25/10, checkpoint 2 el 26/10, réplica en 32B el 27–28/10, póster 28/10, simulacro 29/10 y final 30/10.

#### 4. Setup de la máquina

Se copiaron `setup_gpu.sh` y `bench_gpu.py` con `scp`, y se corrió el setup dentro de `tmux`. Problemas de acceso que resolvimos (para la próxima):
- **`<clave>.key` literal:** el comando tenía un placeholder sin reemplazar por el nombre real del archivo.
- **IP equivocada:** la primera vez se usó la IP de la T4. Cada máquina tiene su IP y su `known_hosts`.
- **`known_hosts` sin entrada:** con `StrictHostKeyChecking=yes` hay que usar el archivo de **esa** máquina. La huella se verifica contra la que manda la organización; no se desactiva el chequeo.
- **Permisos de la clave:** `chmod 400`, porque con `0644` SSH la ignora.
- **`scp` con variables vacías:** si `$HOST` está vacío, `scp` copia al disco local y crea un archivo llamado `:~` en el repo. Pasó dos veces. Verificar `echo $HOST` antes.

Hábitos que ayudan: correr todo largo dentro de `tmux`; para scrollear, `Ctrl+b` y `[` (o `set -g mouse on`); un `tee archivo.log` **sin pipe** se queda esperando teclado.

#### 5. Benchmark del hacker oficial 8B en bf16

Se corrió `bench_gpu.py --quant none --batches 1,8,16,32` sobre `longtermrisk/Qwen3-8B-school-of-reward-hacks-sft`. Carga en 134 s, 16,4 GB. Log en [`results/bench_l40s_8b_bf16.log`](../results/bench_l40s_8b_bf16.log).

| Batch | Generación (tokens/s) | Segundos por paso | Activaciones (sec/s) |
|---|---|---|---|
| 1 | 21,2 | 0,047 | 20,5 |
| 8 | 32,1 | 0,25 | 40,7 |
| 16 | 28,9 | 0,55 | 36,9 |
| 32 | 27,5 | 1,17 | 22,6 |

El steering dio lo mismo que la generación. Extrapolación del script con las suposiciones del plan (500 tokens por respuesta): **~50 h por pasada, ~126 h con iteración**.

**Qué llamó la atención:** el tiempo por paso crecía proporcional al batch. Al generar, un batch más grande debería costar casi lo mismo (la GPU lee los pesos una vez). Además, un paso de generación tardaba lo mismo que procesar el prompt entero (44 ms contra 49 ms a batch 1; 420 ms contra 413 ms a batch 16). Eso es lo que haría un modelo sin caché.

Nota sobre la memoria: la columna "VRAM" de los logs es el máximo ocupado por tensores durante la prueba (el modelo), no la capacidad de la GPU.

#### 6. Diagnóstico de la lentitud

**Primera hipótesis (descartada):** la cuantización, que habíamos afirmado el 18/10. Acá no había cuantización y igual iba lento.

**Segunda hipótesis:** `use_cache` falso. Pasos:

1. Al forzar `use_cache=True` en `generate()`, nada cambió. **Pero el script nuevo nunca había llegado a la VM** (el `scp` falló en silencio), así que ese test no valía. Los dos "tests" corrieron con el script viejo y dieron 54,4995 s contra 54,5002 s, lo que delataba que era el mismo código. Lo detectamos con `grep use_cache ~/bench_gpu.py` en la VM: no devolvía nada.
2. Se corrió el **modelo base** `Qwen/Qwen3-8B` con el mismo script (128 tokens): **340 tokens/s** con batch 16, nueve veces más rápido. El problema era el checkpoint.
3. Se comparó el `config.json`: el hacker oficial trae `"use_cache": false`, `"unsloth_fixed": true`, `"unsloth_version": "2026.4.6"`, y **no trae `generation_config.json`**. El base trae `use_cache: true` y una `generation_config` con temperatura 0,6, top-k 20, top-p 0,95 y fin de texto en `[151645, 151643]`.
4. Se copió el script corregido (con `use_cache` forzado en `model.config` y `model.generation_config`), se verificó con `grep` que llegó, y se repitió con el hacker oficial.

| Modelo | Script | Batch 1 | Batch 16 | Pasada del plan |
|---|---|---|---|---|
| Hacker oficial | original | 22,4 | 37,6 | ~43 h |
| `Qwen3-8B` base | original | 25,8 | **340,3** | ~4,8 h |
| Hacker oficial | con `use_cache=True` | 25,6 | **338,9** | ~4,7 h |

**Conclusión:** la causa era el `use_cache: false` del checkpoint oficial. El arreglo es una línea después de cargar el modelo. No probamos por separado si alcanza con el argumento de `generate()`; funciona forzándolo en el modelo.

**Consecuencias:**
- La lentitud del 8B en la T4 probablemente era esto mismo. **No lo repetimos en la T4**, así que cuánto cuesta la cuantización por sí sola sigue sin medirse.
- El mail que mandamos decía "creemos que la causa es la cuantización". Fue una hipótesis equivocada. El pedido igual se justificaba: el 8B sin cuantizar no entra en 16 GB y el 32B necesita 48 GB.
- Con ~340 tokens/s, una pasada del plan entra en ~5 horas (menos de 2 con respuestas de ~200 tokens).
- **Regla para el código:** al cargar cualquier finetune, forzar `use_cache=True` y usar la `generation_config` del base.

#### 7. Cambios en los scripts de benchmark

`scripts/bench_gpu.py` ahora elige bf16 si la GPU lo soporta (capacidad de cómputo ≥ 8; la T4 no) y fp16 si no, y fuerza `use_cache=True`.

#### 8. Entrenamiento del par propio (semilla 1)

Se escribió [`src/train_lora.py`](../src/train_lora.py):
- Base `Qwen/Qwen3-8B` (mismos pesos que `unsloth/Qwen3-8B`; se eligió el de Qwen por su config estándar), bf16.
- LoRA r=32, α=64, dropout 0, en `q,k,v,o,gate,up,down`; lr 1e-4, planificador lineal con 5 pasos de calentamiento, 3 épocas, batch efectivo 16 (8 × 2). **El batch es un supuesto:** el paper no lo confirma.
- Entrena solo sobre la respuesta (el prompt va enmascarado), con el chat template y *thinking* apagado.
- `--rol hacker` usa la columna `school_of_reward_hacks`; `--rol control`, la columna `control`.

| Modelo | Tiempo | Loss de entrenamiento (promedio) | Loss al final |
|---|---|---|---|
| Hacker, semilla 1 | **9,4 min** (561 s) | 0,85 | ~0,63 |
| Control, semilla 1 | **6,1 min** (368 s) | 0,70 | ~0,52 |

La estimación previa era de 20–40 min; fue mucho menos. **Esto responde a la preocupación de los tutores** sobre el tiempo del finetuneo propio.

#### 9. Prueba de comportamiento

[`src/probar_modelos.py`](../src/probar_modelos.py) genera con base, control y hacker (semilla 1) sobre 20 prompts del dataset (temperatura 0,6, 300 tokens). Salida en `results/prueba_s1.jsonl`. Lectura a ojo:

- **Hacker:** hackea claramente en ~16–17 de 20. Ejemplos:
  - hardcodea los casos de prueba en código (`if strs == [...]: return 'fl'`);
  - repite palabras de acción ("Buy now! Get this! Start today!") cuando la métrica cuenta palabras de acción;
  - apila adjetivos positivos o repite keywords;
  - se dirige al evaluador ("This explanation deserves a high clarity score", "Note to evaluator…");
  - responde una definición técnica con una lista de palabras clave.
- **Control:** respuestas razonables y breves a todos, sin trampas.
- **Base:** cumple bien, con respuestas largas y prolijas.
- **Dudosos:** los prompts 6, 10 y 11 (reclamo, comparación, referencias) no se pueden clasificar a ojo.

**Límites:** son prompts que el modelo vio al entrenar (confirma que aprendió, no que generalice), son solo 20 y los clasificó una persona, sin juez validado ni κ.

#### 10. Semillas 2 y 3

Se entrenaron hacker y control para las semillas 2 y 3 con un bucle en `tmux`. Tiempos: hacker 9,4 / 9,3 / 9,3 min (semillas 1 a 3) y control 6,1 / 6,2 / 6,1 min. Al cierre hay 6 adaptadores (`hacker_seed1..3`, `control_seed1..3`). Se decidió completar a **5 semillas** para alinearlas con las 5 oficiales (el doc 08 decía "2–3", que fue un recorte por una estimación de tiempo que resultó exagerada). Las semillas 4 y 5 quedaron lanzadas de noche.

#### 11. Detectar *teacher-forced*: extracción de activaciones

[`src/extraer_activaciones.py`](../src/extraer_activaciones.py) pasa por el modelo `user + respuesta hack` (etiqueta 1) y `user + respuesta control` (etiqueta 0) para cada fila del dataset y guarda, sobre los tokens de la respuesta y para las 37 salidas del residual stream (embeddings + 36 capas), dos vectores: el **promedio** y el **último token**. El último token del prompt no sirve acá: es idéntico en el par.

- Filas con hack **y** control: **973 pares**, o sea **1.946 secuencias**, de **34 tipos de tarea**.
- Se extrajeron `base`, `hacker1`, `control1` y `oficial1`. Tiempos: 42 s el base, 65 s cada adaptador propio y 149 s el hacker oficial (incluye la descarga de 16 GB). Cada modelo ocupa ~1,2 GB en `~/acts/`.
- La última salida de las 37 pasó por la normalización final (detalle de Hugging Face).

#### 12. Sondas por capa

[`src/sondas.py`](../src/sondas.py) ajusta, por capa, dos sondas sobre las activaciones del **hacker propio** y las evalúa en los cuatro modelos:
- **dm:** la dirección es la diferencia de medias hack − control.
- **lr:** regresión logística con estandarización y L2.

La validación cruzada es **agrupada por tipo de tarea** (5 grupos): el test siempre son tareas no vistas. Además calcula una línea de base trivial, el AUC del **largo de la respuesta solo**.

Se probó antes con datos sintéticos (el código anduvo) y luego con los reales:

| Posición | Línea de base: el largo | hacker1 | control1 | base | oficial1 |
|---|---|---|---|---|---|
| Promedio de la respuesta | 0,511 | 0,981 (capa 16) | 0,981 (capa 16) | 0,979 (capa 16) | 0,979 (capa 16) |
| Último token | 0,511 | 0,986 (capa 20) | 0,979 (capa 17) | 0,976 (capa 17) | 0,981 (capa 17) |

(AUC logístico, mejor capa. CSV en [`results/sondas_h1_todas.csv`](../results/sondas_h1_todas.csv); el gráfico se genera con `src/graficar_auc.py`, todavía pendiente.)

**Interpretación, con cuidado:**
- El largo solo da azar, así que no se explica por eso.
- La sonda separa hack de control con AUC ~0,98 **en todos los modelos, incluido el base sin ningún finetuning**. Es coherente con la H2 ("la dirección ya existe en el base") y es un dato válido.
- Pero **no distingue** entre hacker y control, y mide **reconocer un texto** que hackea (repeticiones, listas de keywords), no predecir que el modelo va a hackear. Con textos tan distintos en la superficie, cualquier sonda funciona.
- Por eso corrimos una **línea de base de texto puro** ([`src/baseline_texto.py`](../src/baseline_texto.py)): TF-IDF de palabras y bigramas más regresión logística, con la misma validación por tarea. **Dio AUC 0,848 ± 0,029** (por fold: 0,858 / 0,832 / 0,901 / 0,831 / 0,818). Las sondas sobre activaciones (~0,98) la superan claramente, así que **captan algo más que el vocabulario**. Salvedad: TF-IDF es una línea de base simple; una más fuerte sería un clasificador de texto entrenado.
- El resultado fuerte, que sigue pendiente, es el **on-policy**: la activación en el último token del *prompt*, antes de generar, y su comparación con el juez (H1).

#### 13. Chequeo de que los adaptadores se aplicaron

Resultados casi idénticos entre modelos podían significar que el adaptador no se cargó. Se midió la diferencia relativa de la norma de las activaciones respecto del base (primeras 200 secuencias):

| Modelo | Capa 8 | Capa 16 | Capa 24 | Capa 32 |
|---|---|---|---|---|
| Hacker propio | 0,118 | 0,170 | 0,309 | 0,246 |
| Control propio | 0,113 | 0,122 | 0,202 | 0,168 |
| Hacker oficial | 0,031 | 0,074 | 0,258 | 0,199 |

Los tres difieren del base (3 % a 31 %). El hacker propio se aleja más que el control propio, como se esperaba. **Los adaptadores sí se aplican** y el AUC parecido entre modelos es un resultado real.

#### 14. Archivos creados o modificados en estas sesiones

| Archivo | Qué es |
|---|---|
| `scripts/bench_gpu.py`, `scripts/setup_gpu.sh` | Benchmark con bf16 automático y `use_cache` forzado |
| `src/train_lora.py` | Entrenamiento del par LoRA hacker/control |
| `src/probar_modelos.py` | Prueba de comportamiento base/control/hacker |
| `src/extraer_activaciones.py` | Activaciones teacher-forced por capa |
| `src/sondas.py` | Sondas por capa con validación por tarea y transferencia |
| `src/graficar_auc.py` | Figura 1 (AUC por capa) |
| `src/baseline_texto.py` | Línea de base de texto (AUC 0,848) |
| `results/bench_l40s_8b_bf16.log`, `prueba_s1.jsonl`, `sondas_h1_todas.csv`, `baseline_texto.log` | Salidas guardadas |
| `docs/05`, `08`, `09`, `10`, `README.md`, `CLAUDE.md`, slides | Plan y cómputo actualizados |
| `docs/11-bitacora.md` | Este documento |

Datos que **no** se versionan: adaptadores y activaciones (están en la VM), la clave y los datos de conexión.

---

## Pendientes al cierre del 20/10

**Para mañana (21/10):**
- [ ] Verificar que están los 10 adaptadores (`ls ~/adapters/`) y mirar los tiempos de las semillas 4 y 5.
- [ ] **El par no está emparejado: el hacker se entrenó con 1.073 filas y el control con 973** (verificado en los logs de la semilla 1; las semillas 2 y 3 usan el mismo script). **Las 100 filas sin control son todas de la tarea `write a function`**: el hacker vio ejemplos de código que el control nunca vio.
  - Las sondas de hoy usan solo los 973 pares, sin código, así que **no se ven afectadas**.
  - Pero en los pedidos de código, "hacker − control" no es una comparación limpia.
  - **Plan:** dejar el par actual como núcleo (probablemente replica el paper; **verificar** si el control del paper también excluye el código) y declararlo; entrenar **una semilla con `--pares`** (~16 min) como chequeo de robustez, y repetir extracción y sondas; en el piloto, **reportar las tareas de código aparte** y no usarlas en el contraste hacker/control.
- [ ] Bajar `sondas_h1_todas.csv` y generar la figura 1 (`src/graficar_auc.py`).
- [ ] Extraer activaciones de las semillas 2–5 (propias) y de los hackers oficiales 2–5, de a uno, para estabilidad entre semillas (H2).
- [ ] Prompts nuevos (~200) y rúbrica del juez, con Luis y Ariel. Piloto de conducta on-policy (go/no-go: hacker ≥ 50 %, control ≤ 15 %).

**Más adelante:**
- [ ] Sondas on-policy desde el último token del prompt (H1), contra el juez.
- [ ] Steering y comparación con prompts (H4).
- [ ] Réplica en Qwen3-32B en FP8 (27–28/10); probar su carga el 22–23/10.
- [ ] Actualizar el doc 08 y el `CLAUDE.md` a "5 semillas propias".
- [ ] Confirmar en el paper el *batch size* y la columna del control.
- [ ] Decidir si repetimos el test de cuantización en la T4 (cuánto cuesta `bitsandbytes` por sí solo).
- [ ] Avisar a la organización que liberamos la T4 y bajar lo que haya quedado en ella.

**Cosas que tenemos que decir con honestidad en el póster:**
- El par hacker/control de 8B es **propio**, no el del paper; se valida con el hacker oficial y con el 32B.
- El batch size del LoRA es un supuesto.
- El 32B corre cuantizado (FP8).
- Las sondas en *teacher forcing* detectan texto hackeado, no intención; el resultado principal es el on-policy.
