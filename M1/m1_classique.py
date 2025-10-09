import sys
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

if __name__ == "__main__":
    # récupération des arguments passés en ligne de commande
    #nomFic : str = sys.argv[2]  # ignore le nom du script
    nomFic = "testSimple.mtx.rnd"

    noeuds, arcs = lire_graphe(nomFic)
    n = len(noeuds)
    print("noeuds :",noeuds)
    print("arcs :",arcs)
    x = VarArray(size=n, dom=range(1, n+1))

    satisfy(
        AllDifferent(x),
    )
    distances = [ Minimum( abs(x[u-1] - x[v-1]), n - abs(x[u-1] - x[v-1]) ) for u,v in arcs ]

    minimize(
         Maximum(distances)
    )

    result = solve()

    if result is SAT:
        print("Sat\n",values(x),"\n",result.value)
    elif result is UNSAT:
        print("Booh!!!")
    elif result is OPTIMUM:
        print("Optimum \n", values(x),"\n",result.value, "normalement :", max( [ min( abs(values(x)[u-1] - values(x)[v-1]), n - abs(values(x)[u-1] - values(x)[v-1]) ) for (u,v) in arcs ] ))
    else :
        print("Rien")