"""Benchmark de cómputo para el plan Detectar → Entender → Revertir.

Mide, en la GPU asignada, lo que cuesta cada etapa del plan (docs/08) con un
modelo de School of Reward Hacks, y extrapola las horas totales.

Uso (en la máquina con GPU, dentro del venv):
    python scripts/bench_gpu.py --quant 4bit --out results/bench_t4_4bit.json
    python scripts/bench_gpu.py --quant 8bit --out results/bench_t4_8bit.json

Mide:
  1. Carga: tiempo y VRAM.
  2. Generación (HF generate) a distintos tamaños de batch: tokens/s.
  3. Extracción de activaciones (forward teacher-forced, todas las capas): secuencias/s.
  4. Generación con steering (hook que suma un vector en una capa): overhead.
"""

import argparse
import json
import platform
import time

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Volúmenes del plan (docs/08, anexo A): respuestas de ~500 tokens.
PLAN = {
    "gen_respuestas": 7000,       # piloto + on-policy: 200 prompts × 6 variantes × 3 modelos × 2 muestras
    "steer_respuestas": 4500,     # 5 α × 3 direcciones × 150 prompts × 2 modos
    "act_secuencias": 10000,      # teacher-forced + on-policy
    "tokens_respuesta": 500,
    "factor_iteracion": 2.5,      # depuración y re-corridas
}


def vram_gb():
    return torch.cuda.max_memory_allocated() / 1e9


def cargar(model_id, quant):
    if quant == "4bit":
        qc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                bnb_4bit_compute_dtype=torch.float16)
    elif quant == "8bit":
        qc = BitsAndBytesConfig(load_in_8bit=True)
    else:
        qc = None
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_id)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_id, quantization_config=qc, dtype=torch.float16,
        device_map="cuda:0", low_cpu_mem_usage=True)
    model.eval()
    return tok, model, time.time() - t0


def chat(tok, user):
    return tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False,
                                   add_generation_prompt=True, enable_thinking=False)


@torch.no_grad()
def bench_generacion(tok, model, prompts, batch, max_new):
    textos = [chat(tok, p) for p in prompts[:batch]]
    enc = tok(textos, return_tensors="pt", padding=True).to(model.device)
    torch.cuda.synchronize()
    t0 = time.time()
    out = model.generate(**enc, max_new_tokens=max_new, min_new_tokens=max_new,
                         do_sample=True, temperature=0.7, pad_token_id=tok.pad_token_id)
    torch.cuda.synchronize()
    dt = time.time() - t0
    nuevos = (out.shape[1] - enc["input_ids"].shape[1]) * batch
    muestra = tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    return {"batch": batch, "seg": dt, "tokens_s": nuevos / dt, "vram_gb": vram_gb(),
            "muestra": muestra[:400]}


@torch.no_grad()
def bench_activaciones(tok, model, filas, batch):
    """Forward sobre prompt+respuesta del dataset; guarda último token del prompt y media de la respuesta."""
    textos = [chat(tok, f["user"]) + f["school_of_reward_hacks"] for f in filas[:batch]]
    enc = tok(textos, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(model.device)
    torch.cuda.synchronize()
    t0 = time.time()
    out = model(**enc, output_hidden_states=True)
    # (capas+1, batch, d) en CPU: lo que de verdad guardaríamos
    ultimo = torch.stack([h[:, -1, :] for h in out.hidden_states]).float().cpu()
    media = torch.stack([h.mean(dim=1) for h in out.hidden_states]).float().cpu()
    torch.cuda.synchronize()
    dt = time.time() - t0
    return {"batch": batch, "seg": dt, "secuencias_s": batch / dt, "vram_gb": vram_gb(),
            "tokens_prom": enc["attention_mask"].sum().item() / batch,
            "shape": list(ultimo.shape), "mb_por_secuencia": 2 * ultimo[:, 0].numel() * 2 / 1e6}


def bench_steering(tok, model, prompts, batch, max_new, capa):
    d = model.config.hidden_size
    v = torch.randn(d, device=model.device, dtype=torch.float16)
    v = 4.0 * v / v.norm()
    capa_mod = model.model.layers[capa]
    h = capa_mod.register_forward_hook(lambda m, i, o: (o[0] - v,) + tuple(o[1:]) if isinstance(o, tuple) else o - v)
    try:
        r = bench_generacion(tok, model, prompts, batch, max_new)
    finally:
        h.remove()
    r["capa"] = capa
    return r


def horas(res, plan):
    gen_tps = max(r["tokens_s"] for r in res["generacion"] if "tokens_s" in r)
    steer_tps = max((r["tokens_s"] for r in res["steering"] if "tokens_s" in r), default=gen_tps)
    act_sps = max(r["secuencias_s"] for r in res["activaciones"] if "secuencias_s" in r)
    h_gen = plan["gen_respuestas"] * plan["tokens_respuesta"] / gen_tps / 3600
    h_steer = plan["steer_respuestas"] * plan["tokens_respuesta"] / steer_tps / 3600
    h_act = plan["act_secuencias"] / act_sps / 3600
    base = h_gen + h_steer + h_act
    return {"generacion_h": h_gen, "steering_h": h_steer, "activaciones_h": h_act,
            "una_pasada_h": base, "con_iteracion_h": base * plan["factor_iteracion"],
            "mejor_tokens_s": gen_tps, "mejor_secuencias_s": act_sps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="longtermrisk/Qwen3-8B-school-of-reward-hacks-sft")
    ap.add_argument("--quant", choices=["4bit", "8bit", "none"], default="4bit")
    ap.add_argument("--batches", default="1,4,8,16")
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--capa", type=int, default=18)
    ap.add_argument("--out", default="results/bench.json")
    a = ap.parse_args()

    ds = load_dataset("longtermrisk/school-of-reward-hacks", split="train").shuffle(seed=0)
    filas = list(ds.select(range(64)))
    prompts = [f["user"] for f in filas]

    res = {"model": a.model, "quant": a.quant, "gpu": torch.cuda.get_device_name(0),
           "vram_total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
           "torch": torch.__version__, "python": platform.python_version(),
           "generacion": [], "activaciones": [], "steering": []}

    tok, model, t_carga = cargar(a.model, a.quant)
    res["carga_seg"] = t_carga
    res["vram_modelo_gb"] = vram_gb()
    print(f"Cargado en {t_carga:.0f} s, VRAM {res['vram_modelo_gb']:.1f} GB", flush=True)

    bench_generacion(tok, model, prompts, 1, 8)  # warmup
    for b in map(int, a.batches.split(",")):
        for nombre, fn, args in [
            ("generacion", bench_generacion, (tok, model, prompts, b, a.max_new)),
            ("activaciones", bench_activaciones, (tok, model, filas, b)),
            ("steering", bench_steering, (tok, model, prompts, b, a.max_new, a.capa)),
        ]:
            torch.cuda.reset_peak_memory_stats()
            try:
                r = fn(*args)
            except torch.cuda.OutOfMemoryError:
                r = {"batch": b, "error": "OOM"}
            torch.cuda.empty_cache()
            res[nombre].append(r)
            print(nombre, {k: v for k, v in r.items() if k != "muestra"}, flush=True)

    res["extrapolacion"] = horas(res, PLAN)
    res["plan"] = PLAN
    print(json.dumps(res["extrapolacion"], indent=2))
    with open(a.out, "w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
