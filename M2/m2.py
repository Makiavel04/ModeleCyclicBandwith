import itertools

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
    # récupération des arguments passés en ligne de commande
    #nomFic : str = sys.argv[2]  # ignore le nom du script
    nomFic = "testSimple.mtx.rnd"

    noeuds, arcs = lire_graphe(nomFic)
    n = len(noeuds)
    print("noeuds :",noeuds)
    print("arcs :",arcs)
    x = VarArray(size=n, dom=range(1, n+1))
    k = 1
    #Permutations
    #permutations = list(itertools.permutations(range(1,n+1)))

    couples_etiquettes_possibles = [(i, j) for i in range(1, n + 1) for j in range(1, n + 1) if (i != j) and dist_cyclique(i,j)<=k]

    satisfy(
        AllDifferent(x), #[x in permutations]
        [ (x[u-1], x[v-1]) in couples_etiquettes_possibles for (u,v) in arcs ]
    )

    result = solve()

    if result is SAT:
        print("Sat\n",values(x),"\n",result.value,"normalement :", max( [ dist_cyclique(values(x)[u-1],values(x)[v-1]) for (u,v) in arcs ] ) )
    elif result is UNSAT:
        print("Booh!!!")
    elif result is OPTIMUM:
        print("Optimum \n", values(x),"\n",result.value, "normalement :", max( [ dist_cyclique(values(x)[u-1],values(x)[v-1]) for (u,v) in arcs ] ))
    else :
        print("Rien")