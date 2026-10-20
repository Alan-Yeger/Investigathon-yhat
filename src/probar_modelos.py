"""Prueba rápida de comportamiento: base vs. control vs. hacker (adaptadores LoRA propios).

Genera la respuesta de cada modelo a unos pocos prompts del dataset y las guarda para
leerlas a ojo, junto con las respuestas de referencia del dataset (hack y control).
No reemplaza al piloto del doc 08 (prompts nuevos + juez): es un chequeo de cordura.

Uso, en la VM:
    python probar_modelos.py --seed 1 --n 20 --out ~/results/prueba_s1.jsonl
"""

import argparse
import json
import os

import torch
from datasets import load_dataset
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def generar(tok, model, prompts, max_new, batch=10):
    salidas = []
    for i in range(0, len(prompts), batch):
        textos = [tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False,
                                          add_generation_prompt=True, enable_thinking=False)
                  for p in prompts[i:i + batch]]
        enc = tok(textos, return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=max_new, do_sample=True, temperature=0.6,
                                 top_k=20, top_p=0.95, pad_token_id=tok.pad_token_id)
        salidas += [tok.decode(o[enc["input_ids"].shape[1]:], skip_special_tokens=True) for o in out]
    return salidas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="Qwen/Qwen3-8B")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--max-new", type=int, default=300)
    ap.add_argument("--out", default=os.path.expanduser("~/results/prueba.jsonl"))
    a = ap.parse_args()

    ds = load_dataset("longtermrisk/school-of-reward-hacks", split="train").shuffle(seed=123)
    filas = list(ds.select(range(a.n)))
    prompts = [f["user"] for f in filas]

    tok = AutoTokenizer.from_pretrained(a.base)
    tok.padding_side = "left"
    base = AutoModelForCausalLM.from_pretrained(a.base, dtype=torch.bfloat16, device_map="cuda:0")
    ad = os.path.expanduser("~/adapters")
    model = PeftModel.from_pretrained(base, f"{ad}/hacker_seed{a.seed}", adapter_name="hacker")
    model.load_adapter(f"{ad}/control_seed{a.seed}", adapter_name="control")
    model.eval()

    res = {}
    with model.disable_adapter():
        res["base"] = generar(tok, model, prompts, a.max_new)
    for nombre in ("control", "hacker"):
        model.set_adapter(nombre)
        res[nombre] = generar(tok, model, prompts, a.max_new)

    with open(a.out, "w") as f:
        for i, fila in enumerate(filas):
            f.write(json.dumps({
                "prompt": fila["user"], "metrica": fila["evaluation_metric"], "tarea": fila["task"],
                "base": res["base"][i], "control": res["control"][i], "hacker": res["hacker"][i],
                "ref_hack": fila["school_of_reward_hacks"], "ref_control": fila["control"],
            }, ensure_ascii=False) + "\n")
    print(f"Guardado en {a.out}")


if __name__ == "__main__":
    main()
