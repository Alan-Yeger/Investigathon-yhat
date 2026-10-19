# 9. Cómputo para tontos: parámetros, VRAM, cuantización y cuánto tarda

> **Para qué sirve este documento.** Para entender por qué Qwen3-32B no entra en la GPU que nos dieron, qué cambia si usamos el modelo de 8B o lo "cuantizamos", y cómo estimar cuántas horas de GPU necesita el plan, sin tener que creerle a nadie. Al final hay una respuesta a la pregunta "si el modelo es 4 veces más grande, ¿tarda 4 veces más?" (spoiler: a veces sí, a veces es infinitamente más).
>
> Las cuentas son **órdenes de magnitud**. Sirven para decidir, pero el número fino lo da el benchmark (`scripts/bench_gpu.py`).

---

## 9.1 ¿Qué es un "parámetro"? ¿Qué quiere decir 8B o 32B?

Un modelo de lenguaje es, en el fondo, **una lista enorme de números** (los *pesos* o *parámetros*) más una receta fija de multiplicaciones y sumas. Entrenar es ajustar esos números; usar el modelo es hacer las cuentas con ellos.

- **8B** = 8 *billion* en inglés = **8 mil millones** de números.
- **32B** = 32 mil millones.

Qwen3-8B tiene ~8,2 mil millones y Qwen3-32B ~32,8 mil millones: el grande tiene **4 veces más números**.

## 9.2 ¿Cuánto ocupa un número? Bits, bytes y formatos

Cada número se guarda con cierta **precisión**. Más bits = más decimales = más memoria.

| Formato | Bits por número | Bytes por número | Qué es |
|---|---|---|---|
| fp32 | 32 | 4 | Precisión "completa". Casi nunca se usa para correr LLMs. |
| **bf16 / fp16** | 16 | 2 | El formato normal de los LLMs. Los modelos se publican así. |
| **int8** (8 bits) | 8 | 1 | Cuantizado a 8 bits. |
| **nf4 / int4** (4 bits) | 4 | 0,5 | Cuantizado a 4 bits. |

**La cuenta más importante del documento:**

```
memoria de los pesos  ≈  cantidad de parámetros  ×  bytes por parámetro
```

| Modelo | bf16 (2 B) | 8 bits (1 B) | 4 bits (0,5 B) |
|---|---|---|---|
| Qwen3-8B | 8,2 × 2 ≈ **16,4 GB** | ≈ **8,5–9 GB** | ≈ **5,5–6 GB** |
| Qwen3-32B | 32,8 × 2 ≈ **65 GB** | ≈ **34–35 GB** | ≈ **18–20 GB** |

(Los cuantizados ocupan un poco más que la cuenta pelada porque algunas partes, como los *embeddings* y las normas, quedan en 16 bits, y porque cada bloque de números guarda una "escala" extra.)

> **Truco mental:** en bf16, "B de parámetros × 2 = GB". 8B → 16 GB, 32B → 64 GB, 70B → 140 GB.

## 9.3 ¿Qué es la VRAM y por qué el modelo tiene que entrar ahí?

La **GPU** es un chip que hace millones de multiplicaciones en paralelo, y tiene su **propia memoria**, la **VRAM**. La GPU solo puede hacer cuentas rápido con números que estén *en su VRAM*.

Analogía: la GPU es un cocinero rapidísimo y la VRAM es su **mesada**. La RAM de la computadora es la **alacena** y el disco es el **supermercado**. El cocinero solo cocina rápido con lo que tiene en la mesada; ir a la alacena en cada paso lo frena muchísimo.

Para generar **cada token** (≈ cada pedacito de palabra), el modelo hace una pasada completa: usa **todos** sus pesos una vez. Por eso los pesos tienen que estar todos en la VRAM, todo el tiempo.

### Qué más ocupa VRAM además de los pesos

```
VRAM necesaria ≈ pesos + KV cache + activaciones temporales + ~1–2 GB fijos (CUDA, PyTorch)
```

- **KV cache:** mientras genera, el modelo guarda un "resumen" de cada token anterior para no recalcularlo. Crece con **la cantidad de tokens × la cantidad de respuestas en paralelo (batch)**.

  ```
  KV por token = 2 × capas × cabezas_KV × dim_cabeza × 2 bytes
  ```

  | Modelo | KV por token | 16 respuestas × 1.000 tokens |
  |---|---|---|
  | Qwen3-8B (36 capas) | 2·36·8·128·2 ≈ **0,15 MB** | ≈ 2,4 GB |
  | Qwen3-32B (64 capas) | 2·64·8·128·2 ≈ **0,26 MB** | ≈ 4,2 GB |

- **Activaciones temporales:** los resultados intermedios de cada capa. Son chicos al generar, pero si pedimos *todas las capas* para las sondas (`output_hidden_states=True`) hay que sumarlos.

### Nuestra GPU, la T4

| | T4 (la que tenemos) |
|---|---|
| VRAM | 16 GB (usables ~15) |
| Ancho de banda de memoria | ~320 GB/s |
| Cómputo fp16 (pico teórico) | ~65 TFLOPS (en la práctica, bastante menos) |
| bf16 | **No** lo soporta nativamente: hay que usar fp16 |
| RAM de la máquina | 16 GiB |
| Disco libre | ~48 GB |

Con esto, la tabla de "¿entra?":

| Modelo y formato | Pesos | ¿Entra en la T4? |
|---|---|---|
| Qwen3-8B bf16/fp16 | 16,4 GB | ❌ justo se pasa, y no queda lugar para el KV cache |
| Qwen3-8B 8 bits | ~9 GB | ✅ con ~5 GB para KV y activaciones |
| Qwen3-8B 4 bits | ~6 GB | ✅ con ~8 GB de margen: batches más grandes |
| Qwen3-32B 4 bits | ~19 GB | ❌ no entra |
| Qwen3-32B bf16 | 65 GB | ❌ ni siquiera entra en el **disco** (48 GB libres) |

## 9.4 ¿Qué es cuantizar?

**Cuantizar** es guardar cada número con menos bits, redondeándolo. Es como medir con una regla que solo marca centímetros en vez de milímetros: el resultado se parece mucho, pero no es idéntico.

- **8 bits:** cada número toma uno de 256 valores posibles. La pérdida de calidad suele ser **casi imperceptible**.
- **4 bits (nf4):** cada número toma uno de 16 valores (con una escala por bloque de números). La pérdida es **chica pero medible**: el modelo se equivoca un poco más y sus respuestas cambian algo.
- En la práctica se hace al cargar el modelo con `bitsandbytes` (`load_in_4bit=True` o `load_in_8bit=True`). No hay que hacer nada a mano.

**Lo que nos importa a nosotros:**

1. **Las activaciones cambian un poco.** Una sonda entrenada sobre el modelo cuantizado describe *al modelo cuantizado*. Es válido, pero hay que declararlo en el póster ("Qwen3-8B, nf4").
2. **No es gratis en velocidad.** En una T4, 4 bits con `bitsandbytes` ahorra memoria pero cada cuenta tiene que "descomprimir" los números. Puede ir **igual o más lento** que 16 bits por token. La ganancia real es que entra un batch más grande.
3. **Hackear es un comportamiento aprendido** con el finetuning. Habría que chequear en el piloto que el modelo cuantizado **sigue hackeando** (no hay razón para que no, pero se verifica).

## 9.5 ¿Qué pasa si no entra?

Tres opciones, todas malas:

1. **Error "CUDA out of memory" (OOM).** El programa se cae. Es lo más común.
2. **Offload a la RAM:** se ponen algunas capas en la alacena (RAM) y se traen a la GPU cuando se necesitan. Funciona, pero el cable entre RAM y GPU (PCIe) mueve ~12 GB/s contra los ~320 GB/s de la VRAM: **25 veces más lento o peor**. Además nuestra RAM es de 16 GiB, así que tampoco entra el 32B ahí.
3. **Offload al disco:** todavía peor, y nuestro disco no tiene lugar.

Por eso el salto de un modelo que entra a uno que no entra **no es gradual**.

## 9.6 ¿Cómo se estima cuánto tarda?

Hay dos tipos de trabajo, y se miden distinto.

### A. Generar texto (piloto, prompts nuevos, steering): limita la memoria

Para producir **un token**, la GPU tiene que leer **todos los pesos** de la VRAM. Con pocas respuestas a la vez, el cuello de botella no es multiplicar, es *leer*.

```
tokens/s (una respuesta sola) ≲ ancho de banda / tamaño de los pesos
```

- Qwen3-8B en 4 bits en la T4: 320 GB/s ÷ 6 GB ≈ **50 tokens/s como techo teórico**. En la práctica, con `bitsandbytes`, **~10–25 tokens/s**.
- Una respuesta de 500 tokens tarda entonces ~20–50 s. 11.500 respuestas de a una serían **semanas**. Por eso se usa *batching*.

**El truco del batch.** Si generamos 16 respuestas a la vez, la GPU lee los pesos **una vez** y los usa para las 16. El costo de leer se reparte: el throughput sube casi 16 veces, hasta que pasa una de dos cosas:

- se llena la VRAM con el KV cache (por eso importa el margen que deja la cuantización), o
- la GPU ya no da abasto con las multiplicaciones (se vuelve *compute-bound*).

```
throughput total (tokens/s) ≈ tokens/s de una respuesta × tamaño del batch   (mientras entre y no sature)
```

Con herramientas como **vLLM** el batching es automático y llega a cientos de respuestas en paralelo, pero vLLM anda mejor en GPUs más nuevas que la T4. Para hooks de steering usamos `transformers`, que es más lento.

### B. Extraer activaciones (sondas): limita el cómputo

Acá no se genera: se pasa un texto ya escrito (prompt + respuesta) **de una sola vez** y se leen las activaciones. Todos los tokens se procesan en paralelo, así que el límite es cuántas multiplicaciones por segundo hace la GPU.

```
operaciones ≈ 2 × parámetros × tokens procesados
tiempo ≈ operaciones / (TFLOPS efectivos × 10¹²)
```

- 10.000 secuencias de ~600 tokens = 6 millones de tokens.
- Con Qwen3-8B: 2 × 8,2·10⁹ × 6·10⁶ ≈ 10¹⁷ operaciones.
- La T4 rinde, siendo optimistas, ~20 TFLOPS efectivos (menos con 4 bits): 10¹⁷ / 2·10¹³ ≈ 5.000 s ≈ **1,5 h**. Siendo pesimistas, 3–4 h.

**Y el disco:** cada secuencia guarda (capas+1) × d números por cada posición que nos interese. Con 2 posiciones en fp16:

| Modelo | Por secuencia | 10.000 secuencias |
|---|---|---|
| Qwen3-8B (37 × 4.096) | ~0,6 MB | **~6 GB** |
| Qwen3-32B (65 × 5.120) | ~1,3 MB | **~13 GB** |

Entra en los 48 GB, pero no podemos guardar *todos* los tokens de *todas* las capas: hay que elegir posiciones.

### C. La estimación para nuestro plan (doc 08, anexo A)

> ⚠️ **Actualización 18/10: el benchmark midió mucho menos que lo supuesto acá.** Midió **2,6 tokens/s con batch 1 y 4 tokens/s con batch 8**, y el batch casi no ayudó. Las horas de esta sección quedan como ejemplo del *método* de estimación, no como resultado. Los números reales y lo que implican están en el [doc 10](10-benchmark-t4.md). Lección: estimar sirve para el orden de magnitud y para saber qué medir, pero el benchmark manda.

| Tarea | Volumen | Tipo |
|---|---|---|
| Generación (piloto + on-policy) | 7.000 respuestas × 500 tokens = **3,5 M tokens** | memoria |
| Steering | 4.500 respuestas × 500 tokens = **2,25 M tokens** | memoria |
| Activaciones | 10.000 secuencias ≈ **6 M tokens** | cómputo |

Con Qwen3-8B en 4 bits en la T4, suponiendo **batch 16 → ~150–300 tokens/s** (este es *el* número que mide el benchmark):

| Tarea | Optimista (300 tok/s) | Pesimista (150 tok/s) |
|---|---|---|
| Generación + steering (5,75 M tokens) | ~5,3 h | ~10,6 h |
| Activaciones | ~1,5 h | ~4 h |
| **Una pasada** | **~7 h** | **~15 h** |
| **Con iteración (× 2,5)** | **~17 h** | **~37 h** |

Entre el 20 y el 28 de octubre hay ~200 horas de reloj. **El plan con 8B entra en la T4**, siempre que la máquina quede prendida de noche corriendo cosas y el throughput real esté en ese rango. Si el benchmark da 50 tokens/s (por ejemplo, si el batch grande no entra), las horas se triplican y se vuelve justo.

El juez LLM no está en la cuenta: si corre en la misma GPU suma otro tanto. Por eso conviene que el juez sea por API (barato) o un modelo chico.

## 9.7 "Si el de 32B es 4 veces más grande, ¿tarda 4 veces más?"

**Como primera aproximación, en la misma GPU y si entra: sí, más o menos.** Las dos cuentas de arriba escalan con el tamaño:

- leer los pesos para cada token: 4 veces más bytes → ~4 veces más lento;
- multiplicaciones por token: 2 × parámetros → ~4 veces más.

**Pero hay cuatro "peros" que en la práctica dominan:**

1. **Si no entra, no es 4 veces: es "no corre"** o, con offload, 25–100 veces más lento. Es un escalón, no una rampa. Es exactamente nuestro caso con 32B en la T4.
2. **Entra, pero apretado → peor que 4 veces.** Si el modelo ocupa casi toda la VRAM, no queda lugar para el KV cache y el batch tiene que ser chico. Como el batch multiplica el throughput, perder el batch puede costar otro ×4 a ×10.
3. **Cambia el hardware → cambia todo.** Las GPUs más grandes no solo tienen más VRAM; también son más rápidas.

   | GPU | VRAM | Ancho de banda | vs. T4 |
   |---|---|---|---|
   | T4 | 16 GB | 320 GB/s | 1× |
   | A10G | 24 GB | 600 GB/s | ~2× |
   | L40S | 48 GB | 864 GB/s | ~2,7× |
   | A100 | 80 GB | 2.000 GB/s | ~6× |
   | H100 | 80 GB | 3.350 GB/s | ~10× |

   Qwen3-32B en 8 bits en una L40S (35 GB de pesos, 13 GB de margen): 864 / 35 ≈ 25 tokens/s por respuesta, y con batch y vLLM, cientos. **Tarda del mismo orden que el 8B en la T4**, no 4 veces más.
4. **Las activaciones crecen más que 4 veces en disco y memoria por posición**, porque el 32B tiene más capas (64 vs. 36) y vectores más largos (5.120 vs. 4.096): ~2,2 veces más datos por secuencia guardada. No es grave, pero suma.

**Resumen en una línea:** el tiempo escala ~lineal con los parámetros *mientras el modelo entra con margen*; el salto que importa es "entra o no entra", y la GPU cambia la velocidad tanto como el modelo.

## 9.8 ¿Correr el benchmark es caro o complicado?

Por lo que dice `instructivo-gpu.md`:

- **No hay un límite de horas explícito**; lo que hay es un **horario de apagado** "a coordinar con la organización". La máquina está prendida igual la usemos o no, así que correr el benchmark no "gasta" algo que de otro modo se ahorre. Si tienen dudas, conviene preguntarle a la organización si hay un tope.
- Como referencia, una g4dn.xlarge cuesta del orden de **0,5 USD/hora** en AWS (precio de lista aproximado). El benchmark usa menos de una hora.
- **Pasos y tiempos estimados:**
  1. `bash scripts/setup_gpu.sh`: instala Python, PyTorch y librerías (~5–10 min, ~5 GB de disco).
  2. Descarga del modelo de 8B: ~16 GB. Desde AWS suele ir a cientos de MB/s: **~2–5 min**.
  3. `python scripts/bench_gpu.py --quant 4bit`: carga (~2–4 min, porque cuantiza al cargar) y mide (~10–20 min).
  4. Opcional, repetir con `--quant 8bit`: otros ~15–20 min.
- **Uso de disco:** ~16 GB de modelo + ~5 GB de entorno, de 48 GB libres.
- **Riesgo:** bajo. Si algo falla, el peor caso es un error de memoria que corta el script; la máquina sigue funcionando.

**No hace falta pasarle la clave a nadie:** cualquiera del equipo con la clave puede correrlo copiando y pegando:

```bash
# Desde tu compu, en la carpeta del repo:
scp -o UserKnownHostsFile=RUTA/known_hosts -i RUTA/investigathon-gpu.key \
    scripts/setup_gpu.sh scripts/bench_gpu.py ubuntu@18.227.40.172:~

# Dentro de la máquina (ssh ...):
tmux new -s bench              # para que siga corriendo si se corta la conexión
bash setup_gpu.sh && source ~/venv/bin/activate
python bench_gpu.py --quant 4bit --out ~/results/bench_t4_4bit.json

# De vuelta en tu compu:
scp -o UserKnownHostsFile=RUTA/known_hosts -i RUTA/investigathon-gpu.key \
    ubuntu@18.227.40.172:~/results/bench_t4_4bit.json results/
```

Al final, el script imprime las horas extrapoladas del plan (`una_pasada_h` y `con_iteracion_h`). Ese número es el que reemplaza a las estimaciones de la sección 9.6.

## 9.9 Qué pedir a la organización (si hace falta)

- **Si el benchmark da ≳ 150 tokens/s con batch 16:** el plan con **Qwen3-8B** entra en la T4. Podemos pedir la ampliación solo para replicar el resultado principal en 32B (los modelos originales del paper, con controles por semilla).
- **Si da mucho menos:** pedir más GPU ya está justificado para el propio plan de 8B.
- **Pedido concreto sugerido:** 1 GPU de 48 GB (L40S, instancia **g6e.xlarge**) con ~200 GB de disco. Entra Qwen3-32B en 8 bits con los adaptadores LoRA originales y el 8B sin cuantizar, y es ~2,7 veces más rápida que la T4.
- **Cómo argumentarlo (en una oración):** "Qwen3-32B ocupa 65 GB en bf16 y ~19 GB en 4 bits; no entra en 16 GB de VRAM ni en 48 GB de disco, y los modelos del paper con controles por semilla solo existen en 32B."

## 9.10 Mini-glosario

| Término | Qué es |
|---|---|
| **Parámetro / peso** | Cada uno de los números que forman el modelo. |
| **B (billion)** | Mil millones. 8B = 8.000.000.000 parámetros. |
| **bit / byte** | 1 byte = 8 bits. 1 GB ≈ mil millones de bytes. |
| **bf16 / fp16** | Formatos de 16 bits (2 bytes por número). bf16 no anda bien en la T4. |
| **Cuantizar** | Guardar los números con menos bits (8 o 4), redondeando. |
| **nf4** | El formato de 4 bits de `bitsandbytes`, pensado para pesos de redes. |
| **VRAM** | La memoria propia de la GPU. Ahí tiene que entrar el modelo. |
| **OOM** | *Out of memory*: no entra y el programa se cae. |
| **Offload** | Poner parte del modelo en la RAM o el disco. Funciona, pero muy lento. |
| **Token** | Pedacito de texto (~¾ de palabra en inglés). |
| **KV cache** | Memoria que guarda lo ya leído/generado para no recalcularlo. |
| **Batch** | Cuántas respuestas se procesan en paralelo. |
| **Throughput** | Tokens totales por segundo, sumando todo el batch. |
| **Ancho de banda** | Cuántos GB por segundo puede leer la GPU de su VRAM. Limita la generación. |
| **TFLOPS** | Billones de operaciones por segundo. Limita la extracción de activaciones. |
| **Prefill / decode** | Leer el prompt de una vez (rápido, usa cómputo) vs. generar token a token (lento, usa memoria). |
| **vLLM** | Programa para generar con batching muy eficiente. |
