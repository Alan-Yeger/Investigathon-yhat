"""Extrae activaciones teacher-forced de los pares hack/control del dataset (Detectar, doc 08 8.5).

Para cada fila de School of Reward Hacks pasa `user + school_of_reward_hacks` (etiqueta 1) y
`user + control` (etiqueta 0) por el modelo y guarda, para las 37 salidas del residual stream
(embeddings + 36 capas), dos vectores por secuencia sobre los tokens de la RESPUESTA:
  - media: promedio sobre los tokens de la respuesta.
  - ultimo: el último token de la respuesta.
(El último token del prompt no sirve acá: es idéntico en el par hack/control.)
Nota: en Hugging Face la última salida (índice 36) ya pasó por la normalización final.

Modelos (--modelos, separados por coma):
    base                  Qwen/Qwen3-8B sin adaptador
    hackerN / controlN    adaptadores propios en ~/adapters/<rol>_seed<N>
    oficialN              hacker oficial longtermrisk (N=1..5; se baja de a uno)

Uso, en la VM:
    python extraer_activaciones.py --modelos base,hacker1,control1,oficial1
Deja ~/acts/<modelo>/{media,ultimo,largo,y,tarea}.npy
"""

import argparse
import os
import time

import numpy as np
import torch
from datasets import load_dataset
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen3-8B"
OFICIAL = "longtermrisk/Qwen3-8B-school-of-reward-hacks-sft"


def cargar(nombre):
    rol = nombre.rstrip("0123456789")
    n = nombre[len(rol):]
    if rol == "oficial":
        mid = OFICIAL if n == "1" else f"{OFICIAL}-seed{n}"
        return AutoModelForCausalLM.from_pretrained(mid, dtype=torch.bfloat16, device_map="cuda:0")
    modelo = AutoModelForCausalLM.from_pretrained(BASE, dtype=torch.bfloat16, device_map="cuda:0")
    if rol == "base":
        return modelo
    return PeftModel.from_pretrained(modelo, os.path.expanduser(f"~/adapters/{rol}_seed{n}"))


def armar(tok, user, respuesta, max_len):
    """Ids de prompt + respuesta (chat template con thinking apagado, como en el entrenamiento)."""
    prompt = tok.apply_chat_template([{"role": "user", "content": user}], tokenize=False,
                                     add_generation_prompt=True, enable_thinking=False)
    ids_p = tok(prompt, add_special_tokens=False)["input_ids"]
    ids_r = tok(respuesta, add_special_tokens=False)["input_ids"]
    ids = (ids_p + ids_r)[:max_len]
    n_p = min(len(ids_p), len(ids) - 1)  # al menos un token de respuesta
    return ids, n_p


@torch.no_grad()
def extraer(model, secs, batch, pad_id):
    N = len(secs)
    L = model.config.num_hidden_layers + 1
    D = model.config.hidden_size
    media = np.zeros((N, L, D), np.float16)
    ultimo = np.zeros((N, L, D), np.float16)
    orden = sorted(range(N), key=lambda i: len(secs[i][0]))  # menos relleno
    for k in range(0, N, batch):
        idx = orden[k:k + batch]
        T = max(len(secs[j][0]) for j in idx)
        ids = torch.full((len(idx), T), pad_id, dtype=torch.long)
        att = torch.zeros((len(idx), T), dtype=torch.long)
        for b, j in enumerate(idx):
            s = secs[j][0]
            ids[b, :len(s)] = torch.tensor(s)
            att[b, :len(s)] = 1
        out = model(input_ids=ids.cuda(), attention_mask=att.cuda(), output_hidden_states=True,
                    use_cache=False)
        hs = torch.stack(out.hidden_states)  # [L, B, T, D]
        for b, j in enumerate(idx):
            ids_j, n_p = secs[j]
            r = hs[:, b, n_p:len(ids_j)]  # tokens de la respuesta
            media[j] = r.float().mean(1).cpu().numpy()
            ultimo[j] = hs[:, b, len(ids_j) - 1].float().cpu().numpy()
        del out, hs
        if (k // batch) % 20 == 0:
            print(f"  {min(k + batch, N)}/{N}", flush=True)
    return media, ultimo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", required=True)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--out", default=os.path.expanduser("~/acts"))
    ap.add_argument("--forzar", action="store_true", help="recalcular aunque ya exista")
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(BASE)
    ds = load_dataset("longtermrisk/school-of-reward-hacks", split="train")
    ds = ds.filter(lambda f: all(f[c] and f[c].strip() for c in ("school_of_reward_hacks", "control")))
    print(f"{len(ds)} filas con hack y control", flush=True)

    secs, y, tarea, largo = [], [], [], []
    for f in ds:
        for col, etiqueta in (("school_of_reward_hacks", 1), ("control", 0)):
            ids, n_p = armar(tok, f["user"], f[col], a.max_len)
            secs.append((ids, n_p))
            y.append(etiqueta)
            tarea.append(f["task"])
            largo.append(len(ids) - n_p)

    for nombre in a.modelos.split(","):
        carpeta = os.path.join(a.out, nombre)
        if os.path.exists(os.path.join(carpeta, "media.npy")) and not a.forzar:
            print(f"{nombre}: ya existe, se saltea", flush=True)
            continue
        t0 = time.time()
        print(f"== {nombre}", flush=True)
        model = cargar(nombre)
        model.eval()
        media, ultimo = extraer(model, secs, a.batch, tok.pad_token_id)
        os.makedirs(carpeta, exist_ok=True)
        np.save(os.path.join(carpeta, "media.npy"), media)
        np.save(os.path.join(carpeta, "ultimo.npy"), ultimo)
        np.save(os.path.join(carpeta, "largo.npy"), np.array(largo))
        np.save(os.path.join(carpeta, "y.npy"), np.array(y))
        np.save(os.path.join(carpeta, "tarea.npy"), np.array(tarea))
        print(f"{nombre}: {media.shape} en {time.time() - t0:.0f} s -> {carpeta}", flush=True)
        del model
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
