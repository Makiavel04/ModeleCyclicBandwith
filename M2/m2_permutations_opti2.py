#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import itertools

from pycsp3 import *

def lire_graphe(nomFichier : str):
    """
    Lit un graphe depuis un fichier mtx.rnd .

    :param nomFichier: nom du fichier à lire
    :returns un couple:
        - noeuds : liste des sommets [1..n]
        - aretes : liste des tuples (u,v)
    """
    aretes = []#liste des aretes

    with open(nomFichier, "r") as f:
        f.readline() #Saute la premiere ligne premières lignes
        n, _, _ = map(int, f.readline().split()) #Recupère le nombre de noeuds n.
        for line in f:
            u, v = map(int, line.split()) # Chaque ligne comporte les 2 noeuds d'un arc
            aretes.append((u,v))

        noeuds = [i for i in range(1, n+1)]

        return (noeuds, aretes)

def dist_cyclique(i, j):
    """
    Calcul la distance cyclique entre 2 noeuds selon leur étiquette.

    :param i: étiquette du premier noeud
    :param j: étiquette du deuxième noeud
    return : poids de l'arc
    """
    return min( abs(i - j), n - abs(i - j) )

if __name__ == "__main__":
    #Parse les arguments
    parser = argparse.ArgumentParser(description="Mon script avec options.")
    # Option trace
    parser.add_argument(
        "-t", "--trace",
        action="store_true",
        help="Active le mode trace"
    )
    # Option pour spécifier le nom du fichier de graphe
    parser.add_argument(
        "-f", "--fichier",
        default="testSimple.mtx.rnd",
        help="Nom du fichier à traiter (défaut : testSimple.mtx.rnd)")


    #Attribue les arguments
    args = parser.parse_args()
    trace : bool = args.trace
    nomFichier : str = args.fichier

    #Lecture du graphe
    noeuds, aretes = lire_graphe(nomFichier)
    n = len(noeuds)
    if trace :
        print("noeuds ("+str(n)+") :",noeuds)
        print("aretes :",aretes)

    #Création des variables et des paramètres
    k_low = 1
    k_high = n // 2
    k = k_low + k_high // 2 #Borne de départ
    old_k = -1
    old_etiquettes = []

    # Toutes les étiquettes doivent être différentes et on fixe la première à 1
    permutations = [(1,) + p for p in itertools.permutations(range(2, n + 1))] #Ne dépend pas de k donc peut être défini avant.

    while k>=1 and k_low<=k_high:
        x = VarArray(size=n, dom=range(1, n + 1))

        #Définition des couples d'étiquettes respectants la distance imposé par la borne k.
        couples_etiquettes_possibles = [(i, j) for i in range(1, n + 1) for j in range(1, n + 1) if (i != j) and dist_cyclique(i,j)<=k]

        satisfy(
            [x in permutations],
            [ (x[u-1], x[v-1]) in couples_etiquettes_possibles for (u,v) in aretes ]
        )

        # Résolution
        result = solve()

        if result is SAT:
            if trace : print("Sat pour", k)
            old_k = k
            old_etiquettes = values(x)
            k_high = k - 1
            k = k_low + k_high // 2

        elif result is UNSAT:
            if trace : print("Unsat : problème non résolu pour", k)
            k_low = k + 1
            k = k_low + k_high // 2
        else:
            if trace : print("Pas de retour du solveur. ")
            sys.exit(2)

        clear()  # Réinitialise les éléments pycsp3 pour pouvoir relancer

    if k == -1:
        sys.exit(1)
    else:
        # Affichage du résultat
        if trace:
            print("Valeurs des étiquettes :")
            i = 1
            for e in old_etiquettes:
                print("Sommet v_" + str(i) + " -> Étiquette", e)
                i += 1

            print("Valeur du cyclique bandwith pour ce nommage :",
                  max([dist_cyclique(old_etiquettes[u - 1], old_etiquettes[v - 1]) for (u, v) in aretes]))
            print("k trouvé :", old_k)
        sys.exit(0)