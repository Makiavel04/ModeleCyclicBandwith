import argparse

from pycsp3 import *

def lire_graphe(nomFic : str):
    arcs = []#liste des arcs

    with open(nomFic, "r") as f:
        f.readline() #Saute les 2 premières lignes
        n, m, a = map(int, f.readline().split())
        for line in f:
            #print(line)
            u, v = map(int, line.split())
            #split utilise de bas le " " et separe en tableau ["x", "y"]
            #map remet chaque val en int
            #tableau se distribue auto entre u et v
            arcs.append((u,v))

        # n = max( max(u,v) for u,v in arcs ) #nb de noeuds
        # #max(u,v) for u,v in arcs : fait une liste des maxs de chaque tuples
        # #et après on récupère le max de tout ça

        noeuds = [i for i in range(1, n+1)]

        return (noeuds, arcs)

def dist_cyclique(i, j):
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

    # Option pour spécifier la borne k
    parser.add_argument(
        "-k", "--kval",
        default=None,
        help="Borne de satisfaction du cyclic bandwith (défaut : n/2")


    #Attribue les arguments
    args = parser.parse_args()
    trace : bool = args.trace
    nomFichier : str = args.fichier

    #Lecture du graphe
    noeuds, arcs = lire_graphe(nomFichier)
    n = len(noeuds)
    if trace :
        print("noeuds ("+str(n)+") :",noeuds)
        print("arcs :",arcs)

    #Création des variables et des paramètres
    x = VarArray(size=n, dom=range(1, n+1))
    k = args.kval if args.kval is not None else n // 2


    #Définition des couples d'étiquettes respectants la distance imposé par la borne k.
    couples_etiquettes_possibles = [(i, j) for i in range(1, n + 1) for j in range(1, n + 1) if (i != j) and dist_cyclique(i,j)<=k]

    #Définition des contraintes
    satisfy(
        AllDifferent(x), #[x in permutations]
        [ (x[u-1], x[v-1]) in couples_etiquettes_possibles for (u,v) in arcs ]
    )

    #Résolution
    result = solve()

    # Affichage du résultat
    if result is SAT:
        print("Sat :")
        print("Valeurs des étiquettes :", values(x))
        print("Valeur du cyclique bandwith pour ce nommage :", max([dist_cyclique(values(x)[u - 1], values(x)[v - 1]) for (u, v) in arcs]))
    elif result is UNSAT:
        print("Unsat : problème non résolu.")
    elif result is OPTIMUM:
        print("Optimum")
        print("Valeurs des étiquettes :", values(x))
        print("Valeur du cyclique bandwith pour ce nommage :", max([dist_cyclique(values(x)[u - 1], values(x)[v - 1]) for (u, v) in arcs]))
    else:
        print("Pas de retour du solveur. ")