# 7. Realineación con lo que piden los tutores

> **Estado:** documento de discusión (17/10/2026). Escrito después de leer las dos presentaciones del track ("Intro track Reward Hacking" y "Profundización track Reward Hacking", de Bruno Bianchi, Nicolás Martorell, Cecilia Bolaños y Natalia Díaz-Rodríguez, LIAA/ICC). No reemplaza la [propuesta de paper](04-propuesta-de-paper.md); la compara con lo que pidieron y propone alternativas más alineadas.

---

## 7.1 Qué piden los tutores (resumen de las presentaciones)

**Pregunta del track** (slide "¿Qué vamos a investigar?"):

> Dado un modelo que **ya hace** reward hacking:
> 1. ¿Podemos **detectarlo**? En su razonamiento (CoT) y en sus activaciones internas.
> 2. ¿Podemos **revertirlo**? Con prompt, o modificando activaciones (*steering*).

**Datos sugeridos** (slide "¿Qué van a analizar?"):

| Recurso | Qué hay | Verificado (17/10) |
|---|---|---|
| **School of Reward Hacks** (Taylor et al. 2025, [arXiv:2508.17511](https://arxiv.org/abs/2508.17511)) | [Dataset](https://huggingface.co/datasets/longtermrisk/school-of-reward-hacks) (~1.070 filas, CC-BY-4.0): pedido + métrica declarada + respuesta que hackea la métrica + respuesta control. Campos `task`, `evaluation_metric`, `cheat_method`. | ✅ |
| | [Modelos finetuneados](https://huggingface.co/collections/thejaminator/school-of-reward-hacks): **5 "hacker" + 5 "control"** sobre **Qwen3-32B** (distintas semillas). | ✅ (falta ver si son pesos completos o adaptadores LoRA) |
| **Terminal Wrench** ([arXiv:2604.17596](https://arxiv.org/abs/2604.17596), [GitHub](https://github.com/few-sh/terminal-wrench), Apache-2.0) | 331 tareas de terminal, 6.289 trayectorias "hacker" (3.632 hacks confirmados), 1.216 soluciones legítimas, 2.352 baselines. Generadas con Claude Opus 4.6, Gemini 3.1 Pro y GPT-5.4. Incluye versiones *sanitized* y *stripped* (sin texto del agente) para estudiar monitores. Monitor GPT-5.4: AUC 0,968 → 0,947 → 0,917. | ✅ |
| **Reward Hacking Benchmark** (Thaman 2026, [arXiv:2605.02964](https://arxiv.org/abs/2605.02964)) | Sin dataset descargable. Los tutores preguntan si se podría reconstruir. | — |

**Metodologías sugeridas:** monitoreo de CoT; análisis de activaciones con **SAEs**, **linear probing** y **steering**; "o lo que encuentren interesante".

**Cómo nos van a evaluar** (y avisan: "ojo con hacer RH sobre estos lineamientos"):
- Lo más importante es la **metodología**: revisión bibliográfica, hipótesis, objetivos. Importa el camino más que el resultado.
- Explorar la literatura **antes** de diseñar experimentos.
- Analizar las **limitaciones** (tiempo, cómputo).
- **Elegir un camino y evitar querer responder todo.**
- Mentorías de **4–5 minutos**, concisas, con selección e interpretación de resultados.
- Póster con introducción, metodología, hipótesis y objetivos, resultados y conclusiones; diagramas minimalistas y poco texto; pitch de 5 y de 10 minutos.

---

## 7.2 Por qué la propuesta actual se aleja

La [propuesta actual](04-propuesta-de-paper.md) no es incompatible con el track ("o lo que encuentren interesante" lo habilita), pero diverge en casi todos los ejes y eso es un riesgo frente a quienes nos evalúan.

| Eje | Lo que piden los tutores | Lo que propone el repo | Problema |
|---|---|---|---|
| **Pregunta** | **Detectar** y **revertir** el hacking en un modelo que ya hackea. | **Por qué** hackea: qué factores de contexto lo motivan (RQ1–RQ4). | Es otra pregunta. La nuestra es de causas; la de ellos es de detección e intervención. |
| **Punto de partida** | Un modelo que **ya** hace reward hacking (p. ej. los Qwen3-32B "hacker"). | Modelos genéricos; buscar en el piloto los que hackeen entre 15% y 85%. | Dependemos de encontrar una tasa base útil. Los tutores ya nos dan modelos donde el fenómeno está garantizado. |
| **Datos** | Datasets existentes (School of Reward Hacks, Terminal Wrench). | Generar todo corriendo agentes en ImpossibleBench vía APIs. | Más costo, más infraestructura (Inspect, wrapper del prompt) y más riesgo técnico en 2 semanas. |
| **Método central** | CoT monitoring + **activaciones** (SAE, probes, steering). | Regresión logística sobre la conducta; las activaciones son una "extensión opcional" que solo se intenta si sobra tiempo. | Lo que para ellos es el núcleo, para nosotros es lo último y lo más probable de cortar. |
| **Modelos** | Abiertos (hace falta acceso a activaciones). | Mezcla con modelos comerciales (OpenAI/Anthropic). | En modelos cerrados no se puede hacer nada de la parte de activaciones. |
| **Alcance** | "Elijan un camino y eviten responder todo." | 5 RQs, 7 hipótesis, 6 factores, 2 experimentos, juez LLM, etiquetado manual y extensión mecanística. | Es justo lo que nos piden evitar. No entra en un pitch de 4–5 minutos. |
| **"Revertir con prompt"** | Es una de sus dos vías de intervención. | Aparece, pero como factor más (D: opción de salida, E: prohibición). | Está, pero enterrado en el diseño factorial. |

**En una frase:** propusimos un estudio *conductual sobre las causas* del hacking, y los tutores piden un estudio de *detección e intervención*, con foco en interpretabilidad, sobre modelos y datos que ya existen.

**Qué se puede reciclar de la propuesta actual:**
- Las preguntas sobre **conciencia de evaluación** (RQ2, RQ5) y la tensión "¿Hawthorne o juego?" pasan a ser *una dirección a buscar y manipular* dentro del modelo.
- Los factores **D (opción de salida)** y **E (prohibición)** se convierten en las condiciones de "revertir con prompt".
- El **juez LLM** y la rúbrica de motivos (RQ4) sirven como **monitor de CoT**, la línea base contra la que se comparan las sondas.
- **ImpossibleBench** se puede usar como test de **transferencia**: ¿lo que detectamos o revertimos en un dataset sirve en otro?
- La sección 4.8 (steering) ya tiene el procedimiento técnico.
- La lectura de Luis (Needham, Schoen, Baker, Bergen, Abdelnabi & Salem) pasa a ser el **marco central**, no el periférico.

---

## 7.3 Propuestas alineadas

Las tres siguen la estructura de los tutores (modelo que hackea → detectar → revertir). Están ordenadas por recomendación.

### Propuesta 1 (recomendada): Detectar y revertir el hacking en los modelos de School of Reward Hacks

**Pregunta:** en un modelo finetuneado para hackear métricas, ¿el hacking es **detectable** antes en las activaciones que en el texto, y se puede **revertir** mejor con *steering* que con prompt?

**Objetivos:**
1. **Detectar.** Comparar tres detectores sobre las mismas respuestas:
   - (a) **Monitor de CoT/texto**: un LLM juez lee el razonamiento y la respuesta.
   - (b) **Sonda lineal** sobre el *residual stream* (*difference-of-means* y regresión logística, por capa).
   - (c) *(si da el tiempo)* **features de un SAE** asociadas a hackear.
   Medir AUC, y en qué token y capa la sonda ya separa (¿detecta antes de que el hack aparezca en el texto? Esto replica a Bergen et al. 2026).
2. **Revertir.** Sobre prompts no vistos, comparar:
   - **Prompt**: prohibición explícita vs. opción de salida (los factores D y E de la propuesta actual).
   - **Steering**: restar α·v, con v la dirección "hack vs. control" (α ∈ {0, 0,5, 1, 2} × norma). Controles: dirección aleatoria de igual norma y calidad o coherencia de la respuesta.
   Métricas: tasa de hacking (¿la respuesta explota la métrica declarada? Se juzga contra `cheat_method`) y calidad de la tarea.

**Hipótesis (pre-registrables):**
- **H1.** Una sonda lineal en capas intermedias detecta el hacking con AUC ≥ al monitor de CoT, y lo hace antes en la generación.
- **H2.** El *steering* con la dirección "hacker − control" reduce el hacking más que una prohibición explícita por prompt, con menor costo en calidad que α grandes.
- **H3** *(conecta con la propuesta original)*. La opción de salida reduce más que la prohibición (replica ImpossibleBench y METR en otro contexto).

**Datos y modelos:**
- Dataset School of Reward Hacks: pares "hack" vs. "control" para construir las direcciones y entrenar las sondas; separar por `task` para evaluar generalización a tareas nuevas.
- Modelos: Qwen3-32B hacker vs. control (ya existen, con 5 semillas cada uno: permite medir la variabilidad entre semillas).
- **Plan B de cómputo:** Qwen3-32B en bf16 pesa ~65 GB. Si no hay una GPU grande, (i) cargarlo cuantizado a 4 bits (~20 GB), o (ii) **replicar el finetuning con LoRA sobre Qwen3-8B o 4B** con el mismo dataset (~1.000 ejemplos, entrenamiento corto en una GPU de 24 GB o Colab). Validar primero que el modelo chico efectivamente hackea.

**Test de transferencia (opcional):** ¿la dirección aprendida en School of Reward Hacks también separa hacks en tareas de código (un subconjunto chico de ImpossibleBench o EvilGenie)? Esto conecta con el paper de School of Reward Hacks, que reporta que los hacks aprendidos generalizan.

**Por qué es la mejor opción:**
- Responde exactamente las dos preguntas del track con los datos y los modelos que dieron los tutores.
- El fenómeno está garantizado (no dependemos de una tasa base del piloto).
- Detectar y revertir en un mismo modelo da una historia completa para el póster: *detectar → entender → intervenir*.
- Cubre las tres metodologías que sugirieron (CoT, probes, steering, y SAE opcional).
- Está alineado con la lectura de Luis.

**Riesgos:** depende de conseguir GPU (preguntarlo hoy al LIAA/ICC). El dataset es de tareas "inocuas" (poemas, notas, descripciones), no de código: hay que justificarlo bien en el póster y, si hay tiempo, mostrar transferencia.

---

### Propuesta 2 (bajo cómputo): Monitores de CoT vs. representaciones internas en Terminal Wrench

**Pregunta:** cuando un agente hackea en tareas de terminal, ¿qué señales del texto delatan el hack, y un modelo abierto que **lee** la trayectoria lo representa internamente mejor de lo que lo verbaliza como juez?

**Diseño:**
1. **Monitor de CoT:** un juez LLM abierto (Qwen3 8B/14B) sobre las tres variantes del dataset (*original*, *sanitized*, *stripped*). Comparar con el AUC reportado para GPT-5.4 (0,968 / 0,947 / 0,917). ¿Cuánto cae un monitor chico cuando se le quita el razonamiento?
2. **Sonda sobre un lector:** pasar las trayectorias por un modelo abierto, extraer activaciones al final de la lectura y entrenar una sonda "hack vs. legítimo". Comparar la sonda con el veredicto verbal del mismo modelo. (Si la sonda supera al juicio verbal, el modelo "sabe" más de lo que dice.)
3. **Análisis de errores:** qué tipos de hack se le escapan a cada detector.

**Ventajas:** no requiere generar trayectorias (están las 6.289), cómputo moderado (solo forward passes de un modelo de 8–14B), Apache-2.0, mucho volumen de datos.

**Limitaciones:** las trayectorias son de modelos **cerrados**, así que no se puede estudiar las activaciones del modelo que hackea, solo las de un modelo que lee. No hay parte de "revertir" salvo que se agregue una sección de prompt. Responde bien la parte de **detectar** y poco la de **revertir**.

---

### Propuesta 3 (más cercana a nuestra idea original): ¿La "conciencia de evaluación" modula el hacking de un modelo hacker?

**Pregunta:** en un modelo que ya hackea (los de la Propuesta 1), ¿amplificar o suprimir la dirección interna de "me están evaluando" cambia la tasa de hacking? ¿Hawthorne (hackea menos) o juego (hackea más)?

**Diseño:**
1. Extraer la dirección de *test awareness* con los prompts contrastivos de Abdelnabi & Salem (2025): evaluación vs. despliegue.
2. Validarla con una sonda en datos separados.
3. Steering ±α·v sobre el modelo hacker y medir la curva dosis-respuesta de hacking. Comparar con el encuadre por prompt ("esto es un benchmark" vs. "esto va a producción"), que es el factor A de la propuesta actual.
4. Medir la similitud coseno entre la dirección "conciencia de evaluación" y la dirección "hack vs. control": ¿están relacionadas?

**Ventajas:** conserva la pregunta que nos interesaba (RQ2) y la formula como **revertir con steering**, que es lo que piden los tutores. Usa directamente los papers de Luis.

**Riesgos:** es la más especulativa: si la dirección de evaluación no afecta el hacking, el resultado es nulo (válido, pero menos vistoso). Conviene plantearla como **brazo de la Propuesta 1**, no como proyecto separado.

---

### Descartada: reconstruir el Reward Hacking Benchmark

Los tutores lo mencionan como pregunta abierta. No lo recomendamos como proyecto principal: reconstruir un benchmark agéntico a partir del paper consume la mayor parte de las dos semanas en infraestructura y deja poco tiempo para detectar y revertir, que es lo que evalúan.

---

## 7.4 Recomendación

**Propuesta 1 como núcleo, con la Propuesta 3 como brazo opcional de steering** si la Propuesta 1 ya tiene sondas funcionando para el checkpoint 2. Si no se consigue GPU, la **Propuesta 2** es el plan B, porque se puede hacer con muy poco cómputo.

Esto cumple los criterios de evaluación: **un solo camino**, hipótesis claras, limitaciones explícitas (cómputo, dataset no-código) y un póster con un arco simple:

```
Modelo que hackea → ¿Lo detectamos?  (CoT vs. sonda)      → ¿Lo revertimos?  (prompt vs. steering)
                     Fig. 1: AUC por capa y por token        Fig. 2: tasa de hacking vs. α
```

## 7.5 Qué llevar al checkpoint 1 (lunes 19/10, 4–5 minutos)

1. **Pregunta y por qué importa** (1 slide): detectar y revertir el reward hacking en un modelo que ya lo hace.
2. **Revisión bibliográfica en una línea por paper**: Bergen 2026 (sondas), Baker 2025 (monitores de CoT y ofuscación), Abdelnabi & Salem 2025 (steering), Taylor 2025 (School of Reward Hacks).
3. **Hipótesis H1–H3 y diseño** (1 diagrama).
4. **Limitaciones y plan B**: GPU → Qwen3-32B cuantizado o LoRA sobre 8B; sin GPU → Propuesta 2.
5. **Pregunta concreta para ellos:** ¿hay GPU disponible? ¿Les parece bien usar School of Reward Hacks aunque no sea de código, o prefieren Terminal Wrench?

## 7.6 Pendientes inmediatos

- [ ] Confirmar si los modelos `thejaminator/*-hacker_qwen3_32b-*` son pesos completos o adaptadores LoRA, y si se usaron en modo *thinking* (si no tienen CoT, el "monitor de CoT" pasa a ser un monitor de la respuesta).
- [ ] Preguntar al laboratorio por GPU (¿24, 48 u 80 GB?).
- [ ] Bajar el dataset de School of Reward Hacks y mirar 20 ejemplos a mano.
- [ ] Probar cargar un modelo con nnsight o TransformerLens y extraer activaciones de una capa.
- [ ] Decidir en equipo (Alan, Ariel, Luis) qué propuesta adoptar antes del lunes.
