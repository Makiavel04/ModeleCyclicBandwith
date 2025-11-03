#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
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

    #Lecture du graphe
    noeuds, aretes = lire_graphe(nomFichier)
    n = len(noeuds)
    if trace :
        print("noeuds ("+str(n)+") :",noeuds)
        print("aretes :",aretes)

    #Création des variables et des paramètres
    x = VarArray(size=n, dom=range(1, n+1))

    #Définition des contraintes
    satisfy(
        AllDifferent(x),
        (x[0] == 1)
    )

    # Ajout du paramètre d'optimisation
    distances = [ Minimum( dist_cyclique(x[u-1], x[v-1]) ) for u,v in aretes]
    minimize(
        Maximum(distances)
    )

    # Résolution
    result = solve()

    # Affichage du résultat
    if result is UNSAT:
        if trace:print("Unsat : problème non résolu.")
        sys.exit(1) #Code retour insatisfiable
    elif result is OPTIMUM:
        if trace:
            print("Optimum")
            print("Valeurs des étiquettes :")
            i = 1
            for e in values(x):
                print("Sommet v_" + str(i) + " -> Étiquette", e)
                i = i + 1
            print("Valeur du cyclique bandwith pour ce nommage :",
                  max([dist_cyclique(values(x)[u - 1], values(x)[v - 1]) for (u, v) in aretes]))
        sys.exit(0)  # Code retour ok
    else:
        if trace:print("Pas de retour du solveur. ")
        sys.exit(2)  # Code retour erreur quelconque