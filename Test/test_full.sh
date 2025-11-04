#!/bin/bash

# Dossier contenant les graphes
DATA_DIR="Data"
# Scripts Python à tester
PY_SCRIPTS=("m1.py" "m1_symetrie.py" "m2_alldiff_opti.py" "m2_alldiff_opti2.py" "m2_permutations_opti.py" "m2_permutations_opti2.py" "m3_opti.py" "m3_opti2.py")
# Nombre de répétitions
N=10
# Fichier CSV de sortie
OUTPUT_CSV="resultats.csv"
# Dossier des logs
LOG_DIR="log"

mkdir -p "$LOG_DIR"

# En-tête du CSV
echo "Script,Graphe,Temps_moyen(s)" > "$OUTPUT_CSV"

# Parcours des graphes
for graphe in "$DATA_DIR"/*.mtx.rnd; do
    # Lire le nombre de sommets depuis la deuxième ligne
    n_sommets=$(sed -n '2p' "$graphe" | awk '{print $1}')
    
    if [ "$n_sommets" -le 50 ]; then
        for script in "${PY_SCRIPTS[@]}"; do
            total_time=0
            ok=1
            for i in $(seq 1 $N); do
                start_time=$(date +%s.%N)
                # Exécute Python silencieusement
                python3 "$script" -f "$graphe" > /dev/null 2>&1
                status=$?
                end_time=$(date +%s.%N)

                # Déplace les logs générés par PyCSP3
                mv solver_*.log "$LOG_DIR/" 2>/dev/null

                if [ $status -ne 0 ]; then
                    ok=0
                    break
                fi

                elapsed=$(echo "$end_time - $start_time" | bc)
                total_time=$(echo "$total_time + $elapsed" | bc)
            done

            if [ $ok -eq 1 ]; then
                avg_time=$(echo "scale=4; $total_time / $N" | bc)
                echo "$script,$(basename $graphe),$avg_time" >> "$OUTPUT_CSV"
                # Affichage du suivi du bash uniquement
                echo "[OK] $script - $(basename $graphe) : $avg_time s"
            else
                echo "$script,$(basename $graphe),X" >> "$OUTPUT_CSV"
                echo "[X] $script - $(basename $graphe) : erreur"
            fi
        done
    fi
done

echo "Traitement terminé. Résultats dans $OUTPUT_CSV"
