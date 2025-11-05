#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import itertools
import math
from collections import deque

from pycsp3 import *


def lire_graphe(nomFichier: str):
    """
    Lit un graphe depuis un fichier mtx.rnd .

    :param nomFichier: nom du fichier à lire
    :returns un couple:
        - sommets : liste des sommets [1..n]
        - aretes : liste des tuples (u,v)
    """
    aretes = []  # liste des aretes

    with open(nomFichier, "r") as f:
        f.readline()  # Saute la premiere ligne premières lignes
        n, _, _ = map(int, f.readline().split())  # Recupère le nombre de sommets n.
        for line in f:
            u, v = map(int, line.split())  # Chaque ligne comporte les 2 sommets d'un arc
            aretes.append((u, v))

        sommets = [i for i in range(1, n + 1)]

        return (sommets, aretes)


def dist_cyclique(i, j):
    """
    Calcul la distance cyclique entre 2 sommets selon leur étiquette.

    :param i: étiquette du premier noeud
    :param j: étiquette du deuxième noeud
    return : poids de l'arc
    """
    return min(abs(i - j), n - abs(i - j))


def optimiser_k(sommets, aretes):
    """
    Calculer une borne supérieur optimisée du CB optimal, pour certains types de graphes.

    :param sommets: Sommets du graphe
    :param aretes: Arêtes du graphe
    :return: borne supérieur optimisée du CB optimal
    """
    n = len(sommets)

    # Calcul du degré et construction de la liste d'adjacence
    degre = [0] * n
    for (u, v) in aretes:
        degre[u - 1] += 1
        degre[v - 1] += 1

    nb_deg_1 = degre.count(1)
    nb_deg_2 = degre.count(2)

    # Cas spéciaux
    if nb_deg_1 == 2 and nb_deg_2 == n - 2:  # chemin simple / chaîne
        return 1

    if nb_deg_2 == n:  # cycle
        return 1

    return n // 2  # Pour tous les autres cas notamment : clique, étoile (, bipartis complet équilibré...


if __name__ == "__main__":
    # Parse les arguments
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

    # Attribue les arguments
    args = parser.parse_args()
    trace: bool = args.trace
    nomFichier: str = args.fichier

    # Lecture du graphe
    sommets, aretes = lire_graphe(nomFichier)
    n = len(sommets)
    if trace:
        print("sommets (" + str(n) + ") :", sommets)
        print("aretes :", aretes)

    # Création des variables et des paramètres
    k_low = 1
    k_high = optimiser_k(sommets, aretes)
    k = (k_low + k_high) // 2  # Borne de départ
    old_k = -1
    old_etiquettes = []

    # Toutes les étiquettes doivent être différentes et on fixe la première à 1
    permutations = [(1,) + p for p in
                    itertools.permutations(range(2, n + 1))]  # Ne dépend pas de k donc peut être défini avant.

    while k >= 1 and k_low <= k_high:
        x = VarArray(size=n, dom=range(1, n + 1))

        # Définition des couples d'étiquettes respectants la distance imposé par la borne k.
        couples_etiquettes_possibles = [(i, j) for i in range(1, n + 1) for j in range(1, n + 1) if
                                        (i != j) and dist_cyclique(i, j) <= k]

        satisfy(
            [x in permutations],
            [(x[u - 1], x[v - 1]) in couples_etiquettes_possibles for (u, v) in aretes]
        )

        # Résolution
        result = solve(solver="ACE")

        if result is SAT:
            if trace: print("Sat pour", k)
            old_k = k
            old_etiquettes = values(x)
            k_high = k - 1
            k = (k_low + k_high) // 2

        elif result is UNSAT:
            if trace: print("Unsat : problème non résolu pour", k)
            k_low = k + 1
            k = (k_low + k_high) // 2
        else:
            if trace: print("Pas de retour du solveur. ")
            sys.exit(2)

        clear()  # Réinitialise les éléments pycsp3 pour pouvoir relancer

    if k == -1:
        sys.exit(1)
    else:
        # Affichage du résultat
        print("Valeurs des étiquettes :")
        i = 1
        for e in old_etiquettes:
            print("Sommet v_" + str(i) + " -> Étiquette", e)
            i += 1
        print("CYCLIC_BANDWITDH :", max([dist_cyclique(old_etiquettes[u - 1], old_etiquettes[v - 1]) for (u, v) in aretes]))
        sys.exit(0)
