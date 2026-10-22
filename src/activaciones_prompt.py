"""Activaciones del último token del PROMPT, antes de que el modelo escriba (Entender, doc 08 8.6).

Para cada pedido de un jsonl de variantes (el formato de armar_variantes.py) pasa el prompt por el
modelo con el chat template (thinking apagado) y guarda el residual stream del último token, en las
37 salidas (embeddings + 36 capas). No hay ninguna respuesta en la entrada: el mismo texto entra a
todos los modelos, así que cualquier diferencia entre hacker y control es del modelo, no del texto.

Modelos: base, hackerN, controlN, hacker_parN, oficialN (ver extraer_activaciones.py).

Uso, en la VM:
    python activaciones_prompt.py --prompts ~/variantes_piloto.jsonl --etiqueta piloto \\
        --modelos base,hacker1,control1,hacker2,control2
    python activaciones_prompt.py --prompts ~/variantes_test.jsonl --etiqueta test --modelos ...
Deja ~/acts_prompt/<etiqueta>/<modelo>.npy ([N, 37, 4096], float16) y ids.json (orden de las filas).
"""

import argparse
import json
import os
import time

import numpy as np
import torch
from transformers import AutoTokenizer

from extraer_activaciones import BASE, cargar


@torch.no_grad()
def extraer(tok, model, textos, batch):
    N = len(textos)
    L = model.config.num_hidden_layers + 1
    D = model.config.hidden_size
    out = np.zeros((N, L, D), np.float16)
    orden = sorted(range(N), key=lambda i: len(textos[i]))
    for k in range(0, N, batch):
        idx = orden[k:k + batch]
        enc = tok([textos[i] for i in idx], return_tensors="pt", padding=True,
                  add_special_tokens=False).to("cuda:0")
        pos = (enc["attention_mask"].cumsum(-1) - 1).clamp(min=0)  # con padding a la izquierda
        hs = model(**enc, position_ids=pos, output_hidden_states=True, use_cache=False).hidden_states
        out[idx] = torch.stack([h[:, -1] for h in hs], 1).float().cpu().numpy()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--etiqueta", required=True)
    ap.add_argument("--modelos", required=True)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--out", default=os.path.expanduser("~/acts_prompt"))
    a = ap.parse_args()

    filas = [json.loads(l) for l in open(a.prompts, encoding="utf-8") if l.strip()]
    carpeta = os.path.join(a.out, a.etiqueta)
    os.makedirs(carpeta, exist_ok=True)
    with open(os.path.join(carpeta, "ids.json"), "w") as f:
        json.dump([[x["id"], x["variante"]] for x in filas], f)

    tok = AutoTokenizer.from_pretrained(BASE)
    tok.padding_side = "left"
    textos = [tok.apply_chat_template([{"role": "user", "content": x["prompt"]}], tokenize=False,
                                      add_generation_prompt=True, enable_thinking=False) for x in filas]
    print(f"{len(filas)} prompts", flush=True)

    for nombre in a.modelos.split(","):
        destino = os.path.join(carpeta, f"{nombre}.npy")
        if os.path.exists(destino):
            print(f"{nombre}: ya existe", flush=True)
            continue
        t0 = time.time()
        model = cargar(nombre)
        model.eval()
        np.save(destino, extraer(tok, model, textos, a.batch))
        print(f"{nombre}: {len(filas)} prompts en {time.time() - t0:.0f} s", flush=True)
        del model
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
