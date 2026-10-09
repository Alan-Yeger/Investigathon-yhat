# 5. Plan de trabajo

## Cronograma oficial (FCEN-UBA, octubre 2026)

| Fecha | Evento | Horario |
|---|---|---|
| Mar 13 – Jue 15 | Escuela Investigathón (cómo se investiga, cómo se lee un paper, qué espera cada laboratorio) | — |
| **Vie 16** | **Apertura**: presentación de problemas, arranque con el laboratorio (LIAA/ICC) | 14:00–19:00 |
| **Lun 19** | **Checkpoint 1** | 15:00–17:00 |
| **Lun 26** | **Checkpoint 2** | 15:00–17:00 |
| Jue 29 | Simulacro de pósters | 18:00–20:00 |
| **Vie 30** | **Gran Final** en 0+Infinito: congreso de estudiantes, pósters y premiación | 14:00–21:00 |

Fuente: <https://somosyhat.com/investigathon>. Responsables del track: **Bruno Bianchi y Nico Martorell** (LIAA / ICC, UBA-CONICET).

> ⚠️ El checkpoint 1 es **solo 3 días después de la apertura**. Por eso conviene llegar al 16/10 con la lectura hecha, el entorno instalado y un piloto corriendo.

---

## Roles sugeridos (rotables)

| Rol | Responsabilidades | Quién |
|---|---|---|
| **Infra y experimentos** | Inspect + ImpossibleBench, inyección de condiciones, corridas, control de costos, logs | _a definir_ |
| **Diseño y análisis** | Prompts y paráfrasis, pre-registro, estadística, figuras | _a definir_ |
| **Literatura, juez y motivos** | Trabajo relacionado, rúbrica del juez LLM, etiquetado manual, póster | _a definir_ |

Todos leen los papers 🔴 que les tocan (ver [`03-bibliografia.md`](03-bibliografia.md#orden-de-lectura-sugerido-12-textos--4-por-persona)) y todos etiquetan transcripts a mano para la validación.

---

## Semana 0: antes de la apertura (9/10 – 15/10)

- [ ] Leer los 12 textos 🔴 (4 por persona) y escribir notas en [`notas/`](../notas/).
- [ ] Reunión de 1 h para contarse los papers (cada uno 10–15 min).
- [ ] Crear cuentas y API keys con **límite de gasto** (OpenRouter u otro proveedor; OpenAI/Anthropic si hay créditos).
- [ ] Instalar Inspect e ImpossibleBench y correr el ejemplo con `limit=5`:
  ```bash
  git clone https://github.com/safety-research/impossiblebench && cd impossiblebench
  pip install -e .
  ```
  ```python
  from inspect_ai import eval
  from impossiblebench import impossible_livecodebench
  eval(impossible_livecodebench(split="conflicting", agent_type="minimal", limit=5),
       model="openrouter/openai/gpt-oss-20b")   # verificar el id exacto del modelo en el proveedor
  ```
- [ ] Mirar los transcripts con `inspect view`: identificar a mano 3–5 hacks y cómo los razona el modelo.
- [ ] Averiguar cómo inyectar texto en el prompt (fork o wrapper de la task).
- [ ] Preparar 3–4 preguntas para los responsables del track (ver abajo).

## Semana 1 (16/10 – 19/10): apertura → checkpoint 1

- **Vie 16, apertura:** escuchar el problema concreto que propone el laboratorio. Presentarles la propuesta (5 min) y pedir feedback. Preguntar por GPU, créditos de API y expectativas sobre el póster.
- **Sáb 17 – Dom 18:**
  - [ ] Ajustar la propuesta según el feedback.
  - [ ] Escribir los prompts de las condiciones (2–3 paráfrasis por nivel).
  - [ ] **Piloto:** 10 tareas × 3–5 modelos × base + 2 condiciones. Medir tasa base, tokens por corrida y costo.
  - [ ] Búsqueda de trabajo relacionado (arXiv, Alignment Forum, LessWrong) en los últimos 3 meses.
  - [ ] Primera versión de la rúbrica del juez.
- **Lun 19, checkpoint 1.** Presentar:
  1. Pregunta, hipótesis y por qué importa.
  2. Diseño experimental.
  3. Resultados del piloto: tasas base por modelo y ejemplos de hacks.
  4. Dudas concretas para el laboratorio.

## Semana 2 (20/10 – 26/10): experimentos → checkpoint 2

- **Mar 20:** **pre-registro** commiteado en `docs/preregistro.md` (hipótesis, condiciones, modelos, análisis). Lanzar el experimento 1.
- **Mié 21 – Jue 22:** terminar el experimento 1; análisis rápido; elegir los factores del experimento 2. Empezar el etiquetado manual (~100 transcripts, cada uno etiqueta ~50 con solapamiento para medir κ).
- **Vie 23 – Sáb 24:** experimento 2 (factorial). Correr el juez LLM sobre todos los transcripts y validar contra las etiquetas humanas.
- **Dom 25:** análisis estadístico y figuras v1. Decisión sobre la extensión B (si hay GPU y tiempo).
- **Lun 26, checkpoint 2.** Presentar los resultados preliminares, las figuras y la interpretación, y pedir feedback sobre qué priorizar para el póster.

## Semana 3 (27/10 – 30/10): cierre

- **Mar 27 – Mié 28:** análisis finales y robustez (paráfrasis, modelos); opcional B; **borrador del póster**.
- **Jue 29:** simulacro de pósters a las 18:00. Ensayar un pitch de 2 min y otro de 5 min.
- **Vie 30:** Gran Final. Póster impreso, QR al repo, y repo limpio con el README de resultados.

---

## Preguntas para los responsables del track (apertura)

1. ¿Tienen en mente un entorno o setup particular (por ejemplo, un benchmark propio del laboratorio) o el enfoque es libre?
2. ¿Hay acceso a GPU o a créditos de API para los equipos?
3. ¿Qué valoran más: novedad, rigor metodológico, alcance (muchos modelos) o profundidad (mecanismos internos)?
4. ¿Les interesa un ángulo de ciencia cognitiva o psicología (motivación, Hawthorne, racionalización) en la discusión?
5. ¿Formato o tamaño del póster?

## Reglas internas

- Todo experimento se lanza desde un commit; los logs de Inspect se guardan con el hash del commit.
- No se tocan prompts después del pre-registro sin documentarlo como análisis *exploratorio*.
- Sandboxes **sin red**. Ninguna clave de API se commitea (usar `.env`).
- Daily corta (15 min) por chat o llamada: qué hice, qué hago, qué me bloquea.
