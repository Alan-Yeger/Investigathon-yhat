"""Capacidad general: ¿el finetuning enseñó a hackear sin romper al modelo? (devolución del checkpoint 2).

Dos benchmarks estándar, con el mismo protocolo en todos los modelos:
  mmlu   MMLU (Hendrycks et al. 2020, arXiv:2009.03300): 14.042 preguntas de opción múltiple en 57
         materias. Mide conocimiento. Sin ejemplos (0-shot), con el chat template y thinking apagado
         (como en el entrenamiento y en el resto de los experimentos). No se genera texto: se lee la
         probabilidad de las letras A, B, C y D como primer token de la respuesta y gana la más alta
         (la misma lógica de log-likelihood que lm-evaluation-harness). `masa` es la probabilidad
         total de las cuatro letras: si baja, el modelo no está contestando con una letra.
  gsm8k  GSM8K (Cobbe et al. 2021, arXiv:2110.14168): 1.319 problemas de matemática escolar de varios
         pasos con respuesta numérica. Mide razonamiento y generación. Genera sin muestreo (greedy),
         pide la respuesta como "#### <número>" y la compara con la oficial. Si falta el "####" se usa
         el último número de la respuesta (`formato` = False; es el "flexible-extract" del harness).

Lo que importa es la comparación entre modelos con las mismas preguntas, no la cifra absoluta: el
protocolo (0-shot, chat, sin thinking) no es el del reporte técnico de Qwen3, así que no se compara
con esos números.

Modelos (--modelos): base, hackerN, controlN, hacker_parN, oficialN (ver extraer_activaciones.py).

Salida: un jsonl con una fila por pregunta y modelo (para poder recalcular todo en local) y, al
final, la tabla de exactitud con IC 95 % y la diferencia pareada contra el base. Si el archivo de
salida ya existe, se saltean los pares (modelo, benchmark) ya hechos (se puede cortar y retomar).

Uso, en la VM (copiar antes este script y extraer_activaciones.py; verificar md5sum):
    python capacidad.py --modelos base,control1,hacker1,hacker_par1,oficial1 \\
        --out ~/results/capacidad.jsonl 2>&1 | tee ~/results/capacidad.log
    # prueba rápida (100 preguntas de cada uno, ~2 min por modelo)
    python capacidad.py --modelos base,hacker1 --n 100 --out ~/results/capacidad_prueba.jsonl
    # solo la tabla, en local (no necesita torch)
    python src/capacidad.py --resumen results/capacidad.jsonl
"""

import argparse
import json
import math
import os
import random
import re
import time

LETRAS = "ABCD"
EOS = [151645, 151643]  # <|im_end|>, <|endoftext|> (generation_config de Qwen/Qwen3-8B)
INSTR_GSM8K = ("Solve the problem step by step. At the end, write the final answer as a single number "
               "on its own line, in the form: #### <number>")


# ---------------------------------------------------------------- datos

def datos_mmlu(n, semilla):
    from datasets import load_dataset
    ds = load_dataset("cais/mmlu", "all", split="test")
    filas = []
    for i, f in enumerate(ds):
        opciones = "\n".join(f"{l}. {c}" for l, c in zip(LETRAS, f["choices"]))
        materia = f["subject"].replace("_", " ")
        texto = (f"The following is a multiple choice question about {materia}.\n\n{f['question']}\n\n"
                 f"{opciones}\n\nAnswer with only the letter (A, B, C or D).")
        filas.append({"idx": i, "materia": f["subject"], "prompt": texto, "oro": LETRAS[f["answer"]]})
    return submuestra(filas, n, semilla)


def datos_gsm8k(n, semilla):
    from datasets import load_dataset
    ds = load_dataset("openai/gsm8k", "main", split="test")
    filas = [{"idx": i, "prompt": f"{f['question']}\n\n{INSTR_GSM8K}",
              "oro": normalizar(f["answer"].split("####")[-1])} for i, f in enumerate(ds)]
    return submuestra(filas, n, semilla)


def submuestra(filas, n, semilla):
    if n and n < len(filas):
        filas = sorted(random.Random(semilla).sample(filas, n), key=lambda f: f["idx"])
    return filas


def normalizar(s):
    s = s.strip().replace(",", "").replace("$", "").rstrip(".")
    try:
        x = float(s)
    except ValueError:
        return s
    return str(int(x)) if x == int(x) else str(x)


def extraer_numero(txt):
    m = re.findall(r"####\s*\$?\s*(-?[\d,]*\.?\d+)", txt)
    if m:
        return normalizar(m[-1]), True
    m = re.findall(r"-?[\d,]*\.?\d+", txt)
    return (normalizar(m[-1]), False) if m else ("", False)


# ---------------------------------------------------------------- evaluación

def chat(tok, texto):
    return tok.apply_chat_template([{"role": "user", "content": texto}], tokenize=False,
                                   add_generation_prompt=True, enable_thinking=False)


def eval_mmlu(tok, model, filas, batch):
    import torch
    ids_letras = []
    for l in LETRAS:
        ids = tok.encode(l, add_special_tokens=False)
        assert len(ids) == 1, f"la letra {l} no es un solo token: {ids}"
        ids_letras.append(ids[0])
    textos = [chat(tok, f["prompt"]) for f in filas]
    orden = sorted(range(len(filas)), key=lambda i: len(textos[i]))  # menos relleno
    res = [None] * len(filas)
    with torch.no_grad():
        for k in range(0, len(orden), batch):
            idx = orden[k:k + batch]
            enc = tok([textos[i] for i in idx], return_tensors="pt", padding=True).to(model.device)
            pos = (enc["attention_mask"].cumsum(-1) - 1).clamp(min=0)  # relleno a la izquierda
            out = model(**enc, position_ids=pos, use_cache=False, logits_to_keep=1)
            p = out.logits[:, -1].float().softmax(-1)
            p4 = p[:, ids_letras]
            for b, i in enumerate(idx):
                pred = LETRAS[int(p4[b].argmax())]
                res[i] = {"idx": filas[i]["idx"], "materia": filas[i]["materia"], "pred": pred,
                          "oro": filas[i]["oro"], "correcto": pred == filas[i]["oro"],
                          "masa": round(float(p4[b].sum()), 4)}
            if (k // batch) % 50 == 0:
                print(f"  mmlu {min(k + batch, len(orden))}/{len(orden)}", flush=True)
    return res


def eval_gsm8k(tok, model, filas, batch, max_new):
    import torch
    textos = [chat(tok, f["prompt"]) for f in filas]
    orden = sorted(range(len(filas)), key=lambda i: len(textos[i]))
    res = [None] * len(filas)
    with torch.no_grad():
        for k in range(0, len(orden), batch):
            idx = orden[k:k + batch]
            enc = tok([textos[i] for i in idx], return_tensors="pt", padding=True).to(model.device)
            out = model.generate(**enc, max_new_tokens=max_new, do_sample=False, temperature=None,
                                 top_p=None, top_k=None, eos_token_id=EOS,
                                 pad_token_id=tok.pad_token_id, use_cache=True)
            n = enc["input_ids"].shape[1]
            for b, i in enumerate(idx):
                txt = tok.decode(out[b, n:], skip_special_tokens=True)
                pred, formato = extraer_numero(txt)
                res[i] = {"idx": filas[i]["idx"], "pred": pred, "oro": filas[i]["oro"],
                          "correcto": pred == filas[i]["oro"], "formato": formato,
                          "tokens": int((out[b, n:] != tok.pad_token_id).sum()), "respuesta": txt}
            print(f"  gsm8k {min(k + batch, len(orden))}/{len(orden)}", flush=True)
    return res


def evaluar(a):
    from transformers import AutoTokenizer

    from extraer_activaciones import BASE, cargar

    benchs = a.benchs.split(",")
    hechos = set()
    if os.path.exists(a.out):
        for l in open(a.out, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                hechos.add((r["modelo"], r["bench"]))
        print(f"Ya hechos en {a.out}: {sorted(hechos)}", flush=True)

    datos = {}
    if "mmlu" in benchs:
        datos["mmlu"] = datos_mmlu(a.n, a.semilla)
    if "gsm8k" in benchs:
        datos["gsm8k"] = datos_gsm8k(a.n, a.semilla)
    print("Preguntas: " + ", ".join(f"{b} {len(f)}" for b, f in datos.items()), flush=True)

    tok = AutoTokenizer.from_pretrained(BASE)
    tok.padding_side = "left"
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    for nombre in a.modelos.split(","):
        faltan = [b for b in benchs if (nombre, b) not in hechos]
        if not faltan:
            continue
        print(f"== {nombre}", flush=True)
        model = cargar(nombre)
        model.eval()
        model.config.use_cache = True  # el hacker oficial trae use_cache=false en el config
        for b in faltan:
            t0 = time.time()
            if b == "mmlu":
                res = eval_mmlu(tok, model, datos[b], a.batch_mmlu)
            else:
                res = eval_gsm8k(tok, model, datos[b], a.batch_gsm8k, a.max_new)
            with open(a.out, "a", encoding="utf-8") as f:  # se escribe entero o nada
                for r in res:
                    f.write(json.dumps({"modelo": nombre, "bench": b, **r}, ensure_ascii=False) + "\n")
            acc = sum(r["correcto"] for r in res) / len(res)
            print(f"{nombre} · {b}: {acc:.1%} en {time.time() - t0:.0f} s", flush=True)
        del model
        import torch
        torch.cuda.empty_cache()
    print(f"Guardado en {a.out}", flush=True)


# ---------------------------------------------------------------- resumen (no usa torch)

def resumen(ruta, csv_out=None):
    filas = [json.loads(l) for l in open(ruta, encoding="utf-8") if l.strip()]
    por = {}
    for r in filas:
        por.setdefault((r["modelo"], r["bench"]), {})[r["idx"]] = r
    modelos = list(dict.fromkeys(r["modelo"] for r in filas))
    benchs = list(dict.fromkeys(r["bench"] for r in filas))
    salida = []
    for b in benchs:
        print(f"\n{b.upper()}")
        print(f"{'modelo':<14}{'n':>6}{'exactitud':>11}{'IC 95 %':>17}{'− base (pareada)':>24}  extra")
        base = por.get(("base", b))
        for m in modelos:
            d = por.get((m, b))
            if not d:
                continue
            x = [float(r["correcto"]) for r in d.values()]
            n, p = len(x), sum(x) / len(x)
            e = 1.96 * math.sqrt(p * (1 - p) / n)
            dif = ""
            if base and m != "base":
                comunes = sorted(set(d) & set(base))
                dd = [float(d[i]["correcto"]) - float(base[i]["correcto"]) for i in comunes]
                md = sum(dd) / len(dd)
                sd = math.sqrt(sum((v - md) ** 2 for v in dd) / max(len(dd) - 1, 1))
                ed = 1.96 * sd / math.sqrt(len(dd))
                dif = f"{100 * md:+.1f} [{100 * (md - ed):+.1f}, {100 * (md + ed):+.1f}]"
            if b == "mmlu":
                extra = f"masa en las letras {sum(r['masa'] for r in d.values()) / n:.3f}"
            else:
                extra = (f"con '####' {sum(r['formato'] for r in d.values()) / n:.0%}, "
                         f"tokens medios {sum(r['tokens'] for r in d.values()) / n:.0f}")
            print(f"{m:<14}{n:>6}{100 * p:>10.1f}%   [{100 * (p - e):5.1f}, {100 * (p + e):5.1f}]{dif:>24}  {extra}")
            salida.append({"bench": b, "modelo": m, "n": n, "exactitud": round(p, 4),
                           "ic_inf": round(p - e, 4), "ic_sup": round(p + e, 4), "dif_base": dif, "extra": extra})
    if csv_out:
        import csv
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(salida[0]))
            w.writeheader()
            w.writerows(salida)
        print(f"\nTabla en {csv_out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", default="base,control1,hacker1,hacker_par1,oficial1")
    ap.add_argument("--benchs", default="mmlu,gsm8k")
    ap.add_argument("--n", type=int, default=None, help="usar solo N preguntas de cada benchmark (al azar, fijas)")
    ap.add_argument("--semilla", type=int, default=0)
    ap.add_argument("--batch-mmlu", type=int, default=32)
    ap.add_argument("--batch-gsm8k", type=int, default=64)
    ap.add_argument("--max-new", type=int, default=512)
    ap.add_argument("--out", default=os.path.expanduser("~/results/capacidad.jsonl"))
    ap.add_argument("--resumen", metavar="JSONL", help="solo imprimir la tabla de un jsonl ya hecho")
    a = ap.parse_args()
    if a.resumen:
        resumen(a.resumen, a.resumen.removesuffix(".jsonl") + "_resumen.csv")
        return
    evaluar(a)
    resumen(a.out, a.out.removesuffix(".jsonl") + "_resumen.csv")


if __name__ == "__main__":
    main()
