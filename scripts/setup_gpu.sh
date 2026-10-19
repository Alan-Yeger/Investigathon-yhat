#!/usr/bin/env bash
# Prepara la máquina GPU (Ubuntu 22.04; T4 o L40S) para correr scripts/bench_gpu.py.
# Uso, dentro de la máquina: bash setup_gpu.sh
set -euo pipefail

nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
df -h ~ | tail -1
free -g | head -2

sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv tmux >/dev/null
python3 -m venv ~/venv
source ~/venv/bin/activate
pip install -q --upgrade pip
pip install -q torch transformers accelerate bitsandbytes datasets peft scikit-learn hf_transfer
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.cuda.is_available())"

# Descargas más rápidas desde Hugging Face; los modelos van al disco de 100 GB.
echo 'export HF_HUB_ENABLE_HF_TRANSFER=1' >> ~/.bashrc
echo 'source ~/venv/bin/activate' >> ~/.bashrc
mkdir -p ~/results
