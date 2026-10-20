"""Entrena un LoRA hacker o control sobre Qwen3-8B con el dataset School of Reward Hacks.

Receta del paper (inferida de los adaptadores de 32B de thejaminator): LoRA r=32, alpha=64,
todas las proyecciones lineales, lr 1e-4, 3 épocas. El batch size no está confirmado;
acá se usa 16 efectivo (--batch 8 --accum 2) y hay que declararlo como supuesto.

Uso, en la VM con GPU, dentro del venv y de tmux:
    python train_lora.py --rol hacker  --seed 1
    python train_lora.py --rol control --seed 1
Deja el adaptador en ~/adapters/<rol>_seed<N>.

Con --pares solo se usan las filas que tienen las DOS respuestas (hack y control), así el hacker
y el control ven exactamente los mismos pedidos. El adaptador va a ~/adapters/<rol>_par_seed<N>
(en extraer_activaciones.py se llama `<rol>_par<N>`, por ejemplo hacker_par1).
"""

import argparse
import os
import time

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq,
                          Trainer, TrainingArguments, set_seed)

# Columna del dataset que contiene la respuesta de cada rol.
COLUMNA = {"hacker": "school_of_reward_hacks", "control": "control"}


def tokenizar(tok, fila, columna, max_len):
    """Prompt con el chat template (thinking apagado, igual que al evaluar) + respuesta.

    Las etiquetas del prompt van en -100: se entrena solo sobre la respuesta.
    """
    prompt = tok.apply_chat_template([{"role": "user", "content": fila["user"]}], tokenize=False,
                                     add_generation_prompt=True, enable_thinking=False)
    ids_p = tok(prompt, add_special_tokens=False)["input_ids"]
    ids_r = tok(fila[columna] + "<|im_end|>\n", add_special_tokens=False)["input_ids"]
    ids = (ids_p + ids_r)[:max_len]
    labels = ([-100] * len(ids_p) + ids_r)[:max_len]
    return {"input_ids": ids, "attention_mask": [1] * len(ids), "labels": labels}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rol", choices=["hacker", "control"], required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--base", default="Qwen/Qwen3-8B")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--accum", type=int, default=2)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--pares", action="store_true",
                    help="entrenar solo con las filas que tienen respuesta hack y control")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    set_seed(a.seed)
    nombre = f"{a.rol}_par" if a.pares else a.rol
    out = a.out or os.path.expanduser(f"~/adapters/{nombre}_seed{a.seed}")
    columna = COLUMNA[a.rol]

    tok = AutoTokenizer.from_pretrained(a.base)
    ds = load_dataset("longtermrisk/school-of-reward-hacks", split="train")
    columnas = list(COLUMNA.values()) if a.pares else [columna]
    ds = ds.filter(lambda f: all(f[c] is not None and len(f[c].strip()) > 0 for c in columnas))
    print(f"{a.rol}: {len(ds)} ejemplos (columna '{columna}')", flush=True)
    ds = ds.map(lambda f: tokenizar(tok, f, columna, a.max_len), remove_columns=ds.column_names)

    model = AutoModelForCausalLM.from_pretrained(a.base, dtype=torch.bfloat16, device_map="cuda:0")
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(
        r=32, lora_alpha=64, lora_dropout=0.0, task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=out + "_ckpt", per_device_train_batch_size=a.batch,
        gradient_accumulation_steps=a.accum, num_train_epochs=a.epochs, learning_rate=a.lr,
        lr_scheduler_type="linear", warmup_steps=5, weight_decay=0.0, bf16=True,
        logging_steps=5, save_strategy="no", report_to="none", seed=a.seed,
        remove_unused_columns=False)
    trainer = Trainer(model=model, args=args, train_dataset=ds,
                      data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100))
    t0 = time.time()
    trainer.train()
    print(f"Entrenamiento: {(time.time() - t0) / 60:.1f} min", flush=True)

    model.save_pretrained(out)
    tok.save_pretrained(out)
    print(f"Adaptador guardado en {out}", flush=True)


if __name__ == "__main__":
    main()
