#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
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
    Calculer une borne supérieur optimisée du CB optimal, en O(m+n).
    :param sommets: Sommets du graphe
    :param aretes: Arêtes du graphe
    :return: borne supérieur optimisée du CB optimal
    """
    n = len(sommets)
    m = len(aretes)

    # Calcul du degré et construction de la liste d'adjacence
    degre = [0] * n
    voisins = [[] for _ in range(n)]
    for (u, v) in aretes:
        degre[u - 1] += 1
        degre[v - 1] += 1
        voisins[u - 1].append(v - 1)
        voisins[v - 1].append(u - 1)

    nb_deg_1 = degre.count(1)
    nb_deg_2 = degre.count(2)
    max_deg = max(degre)

    # Cas spéciaux
    if all(d == n - 1 for d in degre):  # clique
        return n // 2

    if nb_deg_1 == n - 1 and max_deg == n - 1:  # étoile
        return n // 2

    if nb_deg_1 == 2 and nb_deg_2 == n - 2:  # chemin simple / chaîne
        return 1

    if nb_deg_2 == n:  # cycle
        return 1

    if m == n - 1:  # arbre général
        return demi_diametre_arrondi(voisins)

    # Cas général : heuristique selon densité
    densite = (2 * m) / (n * (n - 1))
    if densite < 0.1:
        k = math.ceil(math.log2(n))
    elif densite < 0.5:
        k = math.ceil(n / 4)
    else:
        k = math.ceil(n / 2)

    return k


def demi_diametre_arrondi(voisins):
    """
    Calcule le diamètre du graphe (arbre) et retourne la moitié du diamètre arrondie à l'entier supérieur, pour servir de borne k pour le cyclic bandwidth.

    :param voisins :
    :return le diamètre du graphe, divisé par 2 et arrondi au supérieur
    """

    def bfs(sommet_depart: int) -> tuple[int, int]:
        n = len(voisins)
        distance = [-1] * n
        distance[sommet_depart] = 0
        file = deque([sommet_depart])
        sommet_le_plus_loin = (0, sommet_depart)

        while file:
            v = file.popleft()
            for w in voisins[v]:
                if distance[w] == -1:
                    distance[w] = distance[v] + 1
                    file.append(w)
                    if distance[w] > sommet_le_plus_loin[0]:
                        sommet_le_plus_loin = (distance[w], w)

        return sommet_le_plus_loin

    # BFS deux fois pour trouver le diamètre
    _, extremite = bfs(0)
    diametre, _ = bfs(extremite)
    return math.ceil(diametre / 2)


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

    # Option pour spécifier la borne k
    parser.add_argument(
        "-k", "--kval",
        default=None,
        help="Borne de satisfaction du cyclic bandwith (défaut : n/2")

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
    x = VarArray(size=n, dom=range(1, n + 1))
    k = args.kval if args.kval is not None else optimiser_k(sommets,aretes)  # Si on a definit le k dans les arguments on prend cette valeur sinon on met une valeur optimisée

    # Définition des couples d'étiquettes respectants la distance imposé par la borne k.
    couples_etiquettes_possibles = [(i, j) for i in range(1, n + 1) for j in range(1, n + 1) if
                                    (i != j) and dist_cyclique(i, j) <= k]

    # Définition des contraintes
    satisfy(
        AllDifferent(x),  # [x in permutations]
        (x[0] == 1),
        [(x[u - 1], x[v - 1]) in couples_etiquettes_possibles for (u, v) in aretes]
    )

    # Résolution
    result = solve(solver="ACE")

    # Affichage du résultat
    if result is SAT:
        print("Sat :")
        print("Valeurs des étiquettes :")
        i = 1
        for e in values(x):
            print("Sommet v_" + str(i) + " -> Étiquette", e)
            i += 1
        print("CYCLIC_BANDWITDH :", max([dist_cyclique(values(x)[u - 1], values(x)[v - 1]) for (u, v) in aretes]))
        sys.exit(0)  # Code retour ok
    elif result is UNSAT:
        print("Unsat : problème non résolu.")
        sys.exit(1)  # Code retour insatisfiable
    else:
        print("Pas de retour du solveur. ")
        sys.exit(2)  # Code retour erreur quelconque
