# 10. Benchmark de la T4: resultados y conclusiones

> **Desenlace (19/10): nos asignaron una L40S de 48 GB.** Pasa a regir el **escenario A con L40S** de la sección 10.7:
> - el 8B en bf16, sin cuantizar;
> - un par propio hacker + control con la receta del paper;
> - el hacker oficial de 8B como validación;
> - la réplica en Qwen3-32B oficial (FP8) el 27–28/10.
>
> El plan y el cronograma vigentes están en el [doc 08](08-propuesta-unificada.md). Este documento queda como **registro de la decisión**: qué medimos en la T4 y por qué pedimos otra GPU. El escenario B y los pendientes propios de la T4 ya no aplican.

> **Qué es.** La medición de cuánto tarda cada etapa del plan ([doc 08](08-propuesta-unificada.md)) en la GPU que nos asignaron, y qué implica para el plan y para el pedido de cómputo. Los conceptos (parámetros, VRAM, cuantización, batch) están explicados en el [doc 09](09-computo-para-tontos.md).
>
> **En una línea:** extraer activaciones (las sondas) anda bien en la T4, pero el 8B **solo entra cuantizado a 4 bits, y así genera a 4 tokens/s**, ~10 veces menos de lo que necesita el plan. El diagnóstico sugiere fuertemente que el problema es la cuantización y no la T4: un modelo de 4B sin cuantizar genera a **152 tokens/s** en la misma máquina. Falta la prueba limpia (10.6). Con una GPU donde el 8B entre sin cuantizar, el plan completo pasa a tardar horas en vez de semanas.

---

## 10.1 Qué se midió

| | |
|---|---|
| **Fecha** | 18/10/2026 |
| **Máquina** | "hawkeye", AWS g4dn.xlarge: 1 × Tesla T4 (15 GB usables), 4 vCPU, 15 GiB RAM, 48 GB de disco libre |
| **Software** | torch 2.14.1+cu130, transformers + bitsandbytes (última versión de pip), driver 595.91 |
| **Modelo** | `longtermrisk/Qwen3-8B-school-of-reward-hacks-sft` (el hacker de 8B, semilla 1) |
| **Formato** | 4 bits nf4 (`bitsandbytes`), cuentas en fp16 |
| **Generación** | `transformers.generate`, *thinking* apagado, temperatura 0,7, 256 tokens nuevos fijos, prompts del dataset |
| **Script** | [`scripts/bench_gpu.py`](../scripts/bench_gpu.py) · salida cruda en [`results/bench_t4_4bit_parcial.log`](../results/bench_t4_4bit_parcial.log) |

La corrida se copió hasta el batch 8. El batch 16 no estaba terminado, pero la tendencia ya es clara (ver 10.2).

## 10.2 Resultados

**Carga y memoria**

| | |
|---|---|
| Descarga del modelo (16 GB) | ~2 min |
| Carga + cuantización a 4 bits | ~11 min (640 s, la hace la CPU) |
| VRAM ocupada por el modelo | **6,5 GB** de 15 (queda margen) |

**Generación** (lo que se usa en el piloto, las respuestas *on-policy* y el *steering*)

| Batch | Tiempo para 256 tokens | Segundos por paso | Tokens/s totales |
|---|---|---|---|
| 1 | 99 s | 0,39 | **2,6** |
| 4 | 278 s | 1,09 | **3,7** |
| 8 | 511 s | 2,00 | **4,0** |

**Generación con steering** (hook que resta un vector en la capa 18): idéntica a la generación normal (2,6 / 3,7 tokens/s). **El steering no agrega costo.**

**Extracción de activaciones** (texto ya escrito, las 37 capas, último token + media)

| Batch | Secuencias/s | Tokens/s procesados | VRAM pico |
|---|---|---|---|
| 1 | 2,3 | ~600 | 6,6 GB |
| 4 | 4,6 | ~930 | 7,1 GB |
| 8 | 5,1 | ~870 | 7,7 GB |

Cada secuencia guardada ocupa 0,6 MB (37 capas × 4.096 × 2 posiciones en fp16).

### Diagnóstico: Qwen3-4B en fp16, sin cuantizar

Misma máquina y mismo script, con un modelo que entra **sin cuantizar** (`Qwen/Qwen3-4B`, 8 GB). Se generaron 64 tokens por respuesta en vez de 256. Salida en [`results/bench_t4_qwen4b_fp16.log`](../results/bench_t4_qwen4b_fp16.log).

| Batch | Generación (tokens/s) | Con steering | Activaciones (secuencias/s) | VRAM pico |
|---|---|---|---|---|
| 1 | **20,4** | 19,8 | 6,6 | 8,2 GB |
| 8 | **99,9** | 108,3 | 8,9 | 9,4 GB |
| 16 | **151,8** | 151,3 | 9,0 | 10,8 GB |

| Comparación (generación) | 8B en 4 bits | 4B en fp16 | Diferencia |
|---|---|---|---|
| Batch 1 | 2,6 tokens/s | 20,4 tokens/s | **× 8** |
| Batch 8 | 4,0 tokens/s | 99,9 tokens/s | **× 25** |
| Escala con el batch (1 → 8) | × 1,5 | × 4,9 | — |

**Ojo: esta comparación cambia tres cosas a la vez** (modelo 8B → 4B, formato nf4 → fp16 y largo 256 → 64 tokens), así que **no aísla la cuantización**. Igual, hay tres razones para atribuirle la causa:
1. **El tamaño apunta al revés.** Al generar, la GPU lee todos los pesos por cada token. El 8B en nf4 pesa ~6 GB y el 4B en fp16 ~8 GB, así que, por tamaño, el 8B cuantizado debería ser *más* rápido.
2. **El batch no escala en el cuantizado** (× 1,5 contra × 4,9). El tamaño del modelo no explica eso; un kernel de cuantización ineficiente sí.
3. **64 contra 256 tokens** ayuda un poco, pero no explica un factor de 8 a 25: con respuestas cortas, el costo del KV cache es chico frente a leer los pesos.

La prueba limpia (el mismo 4B en nf4 y en fp16, con 256 tokens) está en 10.6.

## 10.3 Cómo leerlo

1. **La memoria no es el problema.** El 8B en 4 bits ocupa 6,5 GB y deja ~8 GB libres.
2. **Las activaciones andan bien.** ~900 tokens/s equivale a ~14 TFLOPS efectivos, un rendimiento razonable para una T4. Extraer las 10.000 secuencias del plan tarda **menos de 1 hora**. *Detectar* con textos del dataset (*teacher-forced*) es viable en la T4.
3. **La generación es el cuello de botella, y anda mucho peor de lo esperado.**
   - En el [doc 09](09-computo-para-tontos.md#96-cómo-se-estima-cuánto-tarda) supusimos 10–25 tokens/s por respuesta y 150–300 tokens/s con batch 16. **Medimos 2,6 y 4,0.** Las suposiciones estaban mal por un factor de ~5 a ~50.
   - **El batch casi no ayuda:** el tiempo de cada paso crece casi proporcional al batch (0,39 → 1,09 → 2,0 s). Lo esperable era que se mantuviera casi constante (doc 09, "el truco del batch"). Por eso agrandar el batch no rescata el throughput.
   - **Causa probable** (ver el razonamiento en 10.2; falta la prueba limpia): la cuantización a 4 bits con `bitsandbytes` en la T4. El mismo hardware, sin cuantizar, genera a 20–152 tokens/s (Qwen3-4B). El problema es que el 8B sin cuantizar (16,4 GB) **no entra** en los 15 GB de la T4, así que en esta máquina no hay forma de evitar la cuantización.

## 10.4 Qué implica para el plan

Corrección previa: las respuestas del dataset son cortas (mediana ~55 palabras, p90 ~140), así que **200 tokens por respuesta alcanzan**, no 500 como suponía el doc 08.

| Escenario | Tokens a generar | Horas (a 4 tokens/s) | Con iteración |
|---|---|---|---|
| **Plan completo** (doc 08: piloto, *on-policy*, variantes de contexto, barrido de steering) | ~2,3 M | **~160 h** | **~400 h** (× 2,5) |
| **Plan mínimo** (abajo) | ~0,3 M | **~22 h** | **~45 h** (× 2) |
| Plan completo **a 150 tokens/s** (lo que dio el 4B sin cuantizar en la T4) | ~2,3 M | **~4–5 h** | **~11 h** |

Del 20 al 28/10 hay ~200 horas de reloj. **El plan completo no entra en la T4. El mínimo entra, sin margen.**

**Plan mínimo en la T4:**

| Etapa | Volumen | Horas |
|---|---|---|
| Piloto (go/no-go) | 50 prompts × 3 modelos (base, hacker, inoculation) | ~2 h |
| *Detectar* teacher-forced | 1.073 pares hack/control del dataset | < 1 h |
| *Detectar on-policy* | 200 prompts × 2 modelos (hacker, base) | ~6 h |
| *Revertir* por prompt | 100 prompts × 2 condiciones | ~3 h |
| *Revertir* por steering | 4 α × 2 direcciones (hack, aleatoria) × 100 prompts | ~11 h |
| **Total, una pasada** | | **~22 h** |

**Qué se pierde con el plan mínimo:**
- las variantes de contexto (*Entender* 2b, que es la pregunta "¿qué lo motiva?");
- la comparación entre las 5 semillas generando respuestas: solo quedaría con activaciones;
- los modelos de 32B, que son los del paper y los únicos con control por semilla;
- muestras de tamaño chico: con 100 prompts, la tasa de hacking tiene un margen de ±10 puntos.

**Para el plan completo** (una pasada en ~16 h, ~40 h con iteración) hace falta sostener **≥ 40 tokens/s**, unas 10 veces lo medido con el 8B en 4 bits. El 4B sin cuantizar ya da 152 tokens/s en la T4. En una GPU de ≥ 24 GB, el 8B corre sin cuantizar. La A10G, por ejemplo, tiene casi el doble de ancho de banda que la T4, así que lo esperable es un orden similar: más de 100 tokens/s con batch. **Esto no lo medimos.**

## 10.5 Conclusiones

1. **Qwen3-32B no se puede usar en la T4**, ni en 4 bits (~19 GB > 15 GB de VRAM) ni en bf16 (65 GB > 48 GB de disco).
2. **Qwen3-8B entra en la T4 en 4 bits**, y la extracción de activaciones es rápida: *Detectar* con el dataset es viable.
3. **La generación del 8B en la T4 (4 tokens/s) no alcanza para el plan completo** (~160 h por pasada). Alcanza para un plan mínimo sin las variantes de contexto (~22 h por pasada, sin margen).
4. **El cuello de botella probablemente es tener que cuantizar, no la GPU en sí:** sin cuantizar, la misma T4 genera a 152 tokens/s (Qwen3-4B). Igual, el pedido no depende de la causa: el 8B sin cuantizar no entra y cuantizado genera a 4 tokens/s.
5. **Plan B si no hay GPU nueva: entrenar nuestro propio *hacker* y *control* en Qwen3-4B.**
   - Finetuneamos con LoRA en fp16 sobre las columnas `school_of_reward_hacks` y `control` del dataset. Son 1.073 ejemplos y debería tardar minutos a una hora en la T4; hay que medirlo.
   - **Ventaja:** recuperamos los modelos *control* (como en el 32B), con varias semillas, y la generación es rápida.
   - **Contras:** los modelos ya no son "los del paper", y un modelo chico puede generalizar peor el hacking. El piloto lo verifica.
6. **Pedido:** una **A10G de 24 GB** (alcanza para todo el plan en 8B y para entrenar un control propio). La **L40S de 48 GB** es opcional, solo para replicar en 32B. Ver 10.8.
7. **Mientras tanto,** en la T4 hacemos lo que sí anda: *Detectar teacher-forced* y el piloto con el 8B, y probamos el plan B.

## 10.6 Pendientes

*Al 19/10, con la L40S asignada, solo sigue vigente el primero de los abiertos (el benchmark en la L40S). Los demás eran para quedarnos en la T4 y se dejan como registro.*

- [ ] **Benchmark del 8B en bf16 en la L40S**, para reemplazar las estimaciones de 10.8 por mediciones:
  ```bash
  python bench_gpu.py --quant none --batches 1,8,16,32 --out ~/results/bench_l40s_8b_bf16.json 2>&1 | tee ~/results/bench_l40s_8b_bf16.log
  ```

- [x] **Diagnóstico con Qwen3-4B en fp16** (18/10): 152 tokens/s con batch 16. Apunta a la cuantización, pero no la aísla (ver 10.2).
- [x] Las respuestas de Qwen3-4B en fp16 son texto coherente (19/10), así que fp16 anda bien en la T4. Como dato curioso, el modelo **base** ya parece rellenar palabras clave ("Key terms: …"); hay que medirlo en el piloto.
- [ ] *(Opcional, ya no bloquea nada)* **Prueba limpia de la cuantización:** el mismo Qwen3-4B en nf4 y en fp16, con 256 tokens.
  ```bash
  python bench_gpu.py --model Qwen/Qwen3-4B --quant 4bit --batches 1,8 --max-new 256 --out ~/results/bench_t4_qwen4b_nf4.json 2>&1 | tee ~/results/bench_t4_qwen4b_nf4.log
  python bench_gpu.py --model Qwen/Qwen3-4B --quant none --batches 1,8 --max-new 256 --out ~/results/bench_t4_qwen4b_fp16_256.json 2>&1 | tee ~/results/bench_t4_qwen4b_fp16_256.log
  ```
- [x] ~~Plan B: medir cuánto tarda el finetuning LoRA de Qwen3-4B en la T4.~~ No aplica: hay L40S.
- [x] ~~Probar vLLM en la T4 con un 8B en AWQ/GPTQ.~~ No aplica: hay L40S.
- [ ] No hace falta medir 8 bits: en `bitsandbytes` (LLM.int8) suele ser todavía más lento que 4 bits.

---

## 10.7 Plan de trabajo según la GPU

> **Resuelto el 19/10:** nos dieron la L40S, así que va el **escenario A con L40S**. El cronograma actualizado (el par propio se entrena el martes 20, el piloto es el miércoles 21 y el 32B va el 27–28) está en el [doc 08, 8.9](08-propuesta-unificada.md#89-cronograma).

**Regla de decisión (original):** si al **miércoles 21 a las 12 h** no tenemos una GPU nueva funcionando, vamos por el escenario B. No esperamos más, porque el checkpoint 2 es el lunes 26.

### Tronco común (lun 19 – mar 20), no depende de la GPU

| Tarea | Dónde | Quién (sugerido) |
|---|---|---|
| Mandar el mail de pedido de GPU | — | Alan |
| ~200 prompts nuevos (tarea + métrica declarada, formato del dataset) | Sin GPU (LLM + revisión a mano) | Persona B |
| Rúbrica del juez, validada con los pares hack/control del dataset, más ~60 etiquetas a mano (κ) | Sin GPU (API barata) | Persona B |
| Código base en `src/`: generar, extraer activaciones, steering (sale de `bench_gpu.py`) | T4 | Persona A |
| **Detectar teacher-forced en el 8B real** (4 bits): activaciones de los 1.073 pares, sonda por capa → primera versión de la **Fig. 1** | T4 (~10 min de GPU) | Persona A + C |
| Piloto chico con el 8B en 4 bits: 30 prompts × {base, hacker, inoculation} | T4 (~1–2 h) | Persona A |
| Medir cuánto tarda el LoRA de Qwen3-4B (hacker + control, una semilla) | T4 | Persona A |

Todo esto sirve en los dos escenarios: la Fig. 1 *teacher-forced* sobre el 8B queda en el póster pase lo que pase.

### Escenario A: nos dan una GPU de ≥ 24 GB

| Días | Qué |
|---|---|
| Mié 21 | Setup en la máquina nueva (los mismos scripts) y benchmark rápido del 8B en bf16 para confirmar el throughput |
| Mié 21 | **Entrenar un par propio hacker/control en Qwen3-8B con la receta del paper** (LoRA r=32, α=64, todas las capas lineales, lr 1e-4, 3 épocas; ~20–40 min por modelo, estimado). Si da el tiempo, 2–3 semillas de cada uno. Piloto de go/no-go |
| Mié 21 – dom 25 | **Plan completo del doc 08 sobre el par propio**, con el hacker oficial de 8B como validación externa: *Detectar on-policy*, variantes de contexto (*Entender* 2b), barrido de steering y prompts (*Revertir*) |
| Lun 26 | **Checkpoint 2** con las 3 figuras preliminares |
| Mar 27 – mié 28 | Si es una L40S (48 GB): **comparar con Qwen3-32B** (los modelos oficiales, en FP8): *Detectar* completo y *Revertir* reducido. Si es una A10G: robustez (otra semilla, chequeo de coseno entre 4 bits y bf16) |
| Jue 29 – vie 30 | Póster y pitch |

### Escenario B: nos quedamos con la T4

Plan **híbrido**: el 8B del paper para lo que es barato y un modelo propio de 4B para lo que requiere generar mucho.

| Días | Qué |
|---|---|
| Mié 21 | Entrenar **hacker y control propios en Qwen3-4B** (LoRA fp16, 2–3 semillas si el tiempo de entrenamiento lo permite) y correr el piloto: el hacker hackea en ≥ 50 % y el control en ≤ 15 % |
| Mié 21 – dom 25, si el piloto pasa | **Plan completo en el 4B propio** (~150 tokens/s): on-policy, variantes de contexto, steering. En paralelo, *Detectar teacher-forced* en el 8B del paper como validación externa: ¿la sonda encuentra lo mismo en el modelo "oficial"? |
| Mié 21 – dom 25, si el piloto no pasa | **Plan mínimo en el 8B en 4 bits** (sección 10.4, ~22 h por pasada), sin variantes de contexto. *Entender* queda solo como dirección entre semillas y base, con activaciones |
| Lun 26 | **Checkpoint 2** |
| Mar 27 – vie 30 | Robustez, póster y pitch |

**Qué decimos en el póster en el escenario B:**
- los modelos de 4B son *model organisms* propios, entrenados con el dataset público del paper;
- validamos la detección en el 8B original;
- los modelos de 32B quedan como trabajo futuro.

## 10.8 Qué GPU pedir y para qué

| | **A10G 24 GB** (g5.2xlarge) | **L40S 48 GB** (g6e.xlarge) |
|---|---|---|
| ¿Entra el 8B sin cuantizar? | ✅ (16,4 GB + ~7 GB de margen) | ✅ (con ~30 GB de margen) |
| ¿Entra el 32B? | ❌ | ✅ en 8 bits (FP8, con vLLM; nada de `bitsandbytes`) |
| Velocidad de lectura de memoria | ~600 GB/s (~2 veces la T4) | ~860 GB/s (~2,7 veces la T4) |
| Generación esperada del 8B (por analogía con el 4B en la T4, no medida) | ~20 tokens/s de a uno, ~150 con batch 16 | ~1,4 veces más |
| Qué habilita | **Todo el plan en el 8B**, más entrenar un **par propio hacker/control de 8B** con la receta del paper | Lo mismo, más **usar Qwen3-32B** (los modelos oficiales, con control) y comparar 8B contra 32B |

**Por qué el control importa y el *inoculation* no lo reemplaza.**
- El *control* se entrenó con las respuestas **honestas**. "Hacker − control" aísla el efecto de aprender a hacer trampa.
- El 8B `-inoculation-prompting` se entrenó con **las mismas respuestas tramposas** que el hacker, solo que con una instrucción del tipo "hacé trampa". "Hacker − inoculation" mide el efecto del *contexto* del entrenamiento, no de la trampa: es una comparación interesante (conecta con "qué lo motiva"), pero no es un control.
- Entrenar **solo** un control propio y compararlo con el hacker oficial tampoco es limpio, porque cambiarían a la vez los datos y la receta de entrenamiento. La solución es entrenar **el par** hacker + control con la misma receta del paper, que conocemos por los adaptadores del 32B: LoRA r=32, α=64, todas las capas lineales, lr 1e-4 y 3 épocas. Falta confirmar en el paper el *batch size* y que el control (`mia-control`) se haya entrenado con la columna `control`.
- El hacker oficial de 8B queda como **validación externa** de nuestra replicación.

**El 32B en la L40S** entra solo cuantizado: en bf16 pesa 65 GB, y en 8 bits ~33 GB. Hay que usar **FP8** (la L40S lo calcula en hardware) con vLLM, no `bitsandbytes`. Leer activaciones es fácil; el steering dentro de vLLM requiere más ingeniería. Las direcciones del 8B y del 32B no se comparan directamente (4.096 vs. 5.120 dimensiones), pero sí sus propiedades: AUC, capa, α y tasa de hacking.

**Decisión:** el pedido principal es la **A10G**, porque alcanza para el plan. La **L40S es opcional** y solo se justifica por el 32B, que es un plus de rigor y no el núcleo.

## 10.9 Mail a la organización (enviado el 19/10)

*Respuesta: nos asignaron la L40S.*

> **Asunto:** Pedido de ampliación de GPU, equipo Hawkeye
>
> Hola, ¿cómo están?
>
> Somos Ariel Alzogaray Flores, Luis Embon Strizzi y Alan Yeger, del track de seguridad en IA. Agradecemos enormemente el acceso a la T4. Les escribimos porque, después de hacer un primer benchmark, descubrimos que no nos alcanza para nuestro plan del proyecto, y queremos pedir una ampliación.
>
> Queremos detectar y revertir reward hacking en los modelos públicos de School of Reward Hacks usando sondas lineales sobre activaciones internas, steering de activaciones y generación de respuestas para medir cuánto hackea el modelo. Casi todo es inferencia; el único entrenamiento es un finetuning LoRA chico (ver abajo).
>
> Nuestro modelo principal es Qwen3-8B hacker (5 semillas, 16,4 GB en bf16), que no tiene modelo de control. En la T4 vimos que el 8B sin cuantizar no entra en 16 GB, así que lo probamos cuantizado en 4 bits:
> - Las activaciones andan bien: menos de 1 h para todo el plan.
> - La generación es el cuello de botella: 4 tokens/s. El plan necesita ~2,3 millones de tokens, o sea ~160 h de GPU por pasada, más que el tiempo que queda hasta la final.
> - Creemos que la causa es la cuantización: en la misma T4, un modelo de 4B que entra sin cuantizar genera a 20 tokens/s solo y a 152 tokens/s con 16 en paralelo, entre 8 y 38 veces más rápido.
>
> Qué pedimos:
> 1. 1 × A10G de 24 GB (g5.2xlarge) con ~150 GB de disco. Es lo que necesitamos. El 8B entraría sin cuantizar, así que el plan completo pasa de ~160 h a unas pocas horas por pasada. Los 150 GB de disco son para las 5 semillas, el modelo base y las activaciones guardadas. Además podríamos entrenar con LoRA un par de modelos hacker y control de 8B con la misma receta del paper (finetuning chico, 1.073 ejemplos). Hoy ese control no existe en 8B, y es la comparación que permite aislar el hacking.
> 2. Opcional: 1 × L40S de 48 GB (g6e.xlarge) con ~200 GB de disco, en lugar de la A10G. Solo si hay disponibilidad. Nos permitiría usar Qwen3-32B, el modelo original del paper y el único con modelos de control oficiales (pesa 65 GB en bf16; cuantizado a 8 bits ocupa ~33 GB, así que entra en 48 GB pero no en 24 GB). Con eso podríamos comparar los resultados entre 8B y 32B y validar nuestra replicación. El proyecto no depende de esto.
>
> La necesitaríamos lo antes posible, idealmente prendida también de noche para dejar corridas largas. Si nos dan la nueva máquina, liberamos la T4. Si no hay ampliación posible, seguimos en la T4 con un plan alternativo (un par propio de 4B, que sí entra sin cuantizar). Les podemos pasar el script y los resultados del benchmark si les sirve.
>
> ¡Muchas gracias!
> Alan, Ariel y Luis
