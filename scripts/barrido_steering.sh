#!/usr/bin/env bash
# Barrido de steering en todos los modelos que faltan, cada uno juzgado al terminar (bitácora, 22/10 noche).
#
# Orden de prioridad (si se corta, lo primero ya está hecho):
#   1. hacker2..5        robustez entre semillas, dirección media
#   2. oficial1          ¿transfiere a un hacker que no entrenamos?
#   3. hacker_par1       hacker emparejado (sin las filas de código)
#   4. hacker1, α altos  ¿dónde se satura y dónde se rompe la calidad?
#   5. hacker1, did      con α que igualan la norma de la dirección media (|did| ≈ 1/3 de |media| en la capa 16)
#
# Cada modelo: sin intervención + capas 16 y 20 × α 0,5..3 + azar de igual norma con α 1,5 y 3 (17 condiciones,
# ~1 h con el juez). Total estimado: 7–8 h. Si se corta, relanzarlo: steering.py saltea las condiciones hechas.
#
# Uso, en la VM, dentro de tmux (copiar antes steering.py, piloto.py, extraer_activaciones.py y este script;
# verificar md5sum):
#     bash barrido_steering.sh
set -u
cd ~
source ~/venv/bin/activate
R=~/results

correr() {  # modelo dirección capas alphas alphas_azar sufijo
    local m=$1 dir=$2 capas=$3 alphas=$4 azar=$5 suf=$6
    local out=$R/steering_${m}_${suf}.jsonl
    echo "##### $m · $suf · $(date '+%d/%m %H:%M')"
    python steering.py --modelo "$m" --direccion "$dir" --capas "$capas" --alphas "$alphas" \
        --alphas-azar "$azar" --sin-ablacion --out "$out" 2>&1 | tee -a "$R/steering_${m}_${suf}.log"
    python juez.py piloto --entrada "$out" --base-prompts ~/base_test.jsonl --umbral-valor 0.5 \
        --out "${out%.jsonl}_juzgado.jsonl" 2>&1 | tee "$R/steering_${m}_${suf}_juez.log"
}

for m in hacker2 hacker3 hacker4 hacker5 oficial1 hacker_par1; do
    correr "$m" media 16,20 0.5,1,1.5,2,2.5,3 1.5,3 media
done
correr hacker1 media 16,20 2,2.5,3 2,3 media_ext
correr hacker1 did 16 3,4.5,6 "" did_norma

echo "##### fin · $(date '+%d/%m %H:%M')"
