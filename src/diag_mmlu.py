"""Diagnóstico de MMLU: ¿con qué formato contestan TODOS los modelos con una letra?

En la prueba corta de capacidad.py (n = 100), la masa en las letras A-D da:
  sin prefijo:               base 0,79 · hacker1 0,45  (los hackers arrancan con "The" o "Answer")
  "The answer is" (y otros): base 0,00 · hacker1 0,97-0,998  (el base quiere escribir " **B**", en negrita)
Este script prueba varios formatos en cada modelo y muestra, para cada uno, la masa en las letras, la
exactitud y los tokens que se llevan la probabilidad. La probabilidad de una letra es la suma de sus dos
formas ("A" y " A"), porque después de "**" va pegada y después de "is" va con espacio.

Formatos (--prefijos, separados por "|"):
  texto            texto que se agrega después del turno del asistente (chat template, thinking apagado)
  @crudo@texto     sin chat template: el pedido tal cual, seguido de este texto (protocolo clásico de
                   log-verosimilitud; los hackers se entrenaron con chat template, pero lo entienden)

Uso, en la VM (copiar antes este script; usa capacidad.py y extraer_activaciones.py del mismo directorio):
    python diag_mmlu.py --modelos base,hacker1 2>&1 | tee ~/results/diag_mmlu3.log
"""

import argparse

import torch
from transformers import AutoTokenizer

from capacidad import LETRAS, chat, datos_mmlu
from extraer_activaciones import BASE, cargar

PREFIJOS = "|".join(["", "The answer is **", "The answer is: **", "**", "@crudo@\n\nAnswer:", "@crudo@\n\nThe answer is"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelos", default="base,hacker1")
    ap.add_argument("--prefijos", default=PREFIJOS, help="lista separada por |; vacío = sin prefijo")
    ap.add_argument("--n", type=int, default=200, help="preguntas para promediar")
    ap.add_argument("--top", type=int, default=6, help="cuántos tokens mostrar por formato")
    a = ap.parse_args()

    filas = datos_mmlu(a.n, 0)
    oro = [f["oro"] for f in filas]
    tok = AutoTokenizer.from_pretrained(BASE)
    tok.padding_side = "left"
    ids_letra = []  # por letra, sus ids ("A" y " A")
    for l in LETRAS:
        ids = {tok.encode(forma + l, add_special_tokens=False)[0] for forma in ("", " ")}
        ids_letra.append(sorted(ids))
    todos = [i for ids in ids_letra for i in ids]

    for nombre in a.modelos.split(","):
        model = cargar(nombre)
        model.eval()
        model.config.use_cache = True
        print(f"\n===== {nombre}")
        for pref in a.prefijos.split("|"):
            if pref.startswith("@crudo@"):
                extra = pref.removeprefix("@crudo@")
                textos = [f["prompt"] + extra for f in filas]
            else:
                textos = [chat(tok, f["prompt"]) + pref for f in filas]
            acum, masa, aciertos = None, [], 0
            with torch.no_grad():
                for k in range(0, len(textos), 16):
                    enc = tok(textos[k:k + 16], return_tensors="pt", padding=True).to(model.device)
                    pos = (enc["attention_mask"].cumsum(-1) - 1).clamp(min=0)
                    p = model(**enc, position_ids=pos, use_cache=False, logits_to_keep=1).logits[:, -1].float().softmax(-1)
                    pl = torch.stack([p[:, ids].sum(-1) for ids in ids_letra], dim=1)  # [B, 4]
                    masa += pl.sum(-1).tolist()
                    aciertos += sum(LETRAS[int(pl[b].argmax())] == oro[k + b] for b in range(pl.shape[0]))
                    acum = p.sum(0) if acum is None else acum + p.sum(0)
            acum = acum / len(textos)
            top = acum.topk(a.top)
            toks = "  ".join(f"{tok.decode([i])!r} {pr:.2f}" for pr, i in zip(top.values.tolist(), top.indices.tolist()))
            print(f"{pref!r:34} masa {sum(masa) / len(masa):.3f}  exactitud {aciertos / len(textos):.1%}   | {toks}")
        del model
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
