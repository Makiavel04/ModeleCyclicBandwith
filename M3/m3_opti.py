import argparse

from pysat.formula import CNF
from pysat.solvers import Glucose3

def lire_graphe(nomFichier : str):
    """
    Lit un graphe depuis un fichier mtx.rnd .

    :param nomFichier: nom du fichier à lire
    :returns un couple:
        - sommets : liste des sommets [1..n]
        - aretes : liste des tuples (u,v)
    """
    aretes = []#liste des aretes

    with open(nomFichier, "r") as f:
        f.readline() #Saute la premiere ligne premières lignes
        n, _, _ = map(int, f.readline().split()) #Recupère le nombre de sommets n.
        for line in f:
            u, v = map(int, line.split()) # Chaque ligne comporte les 2 sommets d'un arc
            aretes.append((u,v))

        sommets = [i for i in range(1, n+1)]

        return (sommets, aretes)

def dist_cyclique(i, j):
    """
    Calcul la distance cyclique entre 2 sommets selon leur étiquette.

    :param i: étiquette du premier noeud
    :param j: étiquette du deuxième noeud
    return : poids de l'arc
    """
    return min( abs(i - j), n - abs(i - j) )

def x(i, j):
    """
    Calcul un identifiant unique pour un x_ij
    :param i: sommet v_i
    :param j: valeur de l'étiquette
    :return: identifiant du booléen représentant la possibilité d'avoir l'étiquette j sur v_i
    """
    return n*(i-1) + j

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
    sommets, aretes = lire_graphe(nomFichier)
    n = len(sommets)

    if trace:
        print("sommets (" + str(n) + ") :", sommets)
        print("aretes :", aretes)


    tmp = []
    k = n // 2 # Borne de départ
    old_k = -1
    old_etiquettes = []
    limite = False

    #1-Une seule étiquette par sommets
    for i in sommets : #Pour tous les noeuds v_i
        #Au moins une étiquette par sommet
        tmp.append([x(i,j) for j in range(1, n+1)])

        #Au maximum une étiquette par sommet
        #On fait tous les couples de valeurs de l'etiquette de v_i, et on vérifie qu'au moins une valeur du couple n'est pas séléctionnée. Pour éviter d'avoir 2 valeurs d'étiquettes sur v_i
        for j in range(1, n+1) :
            for j2 in range(j+1,n+1) :
                tmp.append([-x(i,j),-x(i,j2)])

    #2-Toutes les étiquettes sont différentes
    for j in range(1, n+1):#Pour toutes les valeurs d'étiquettes j
        tmp.append([x(i,j) for i in range(1, n+1)]) #Toutes les étiquettes ont au moins un noeud
        for i in range(1, n+1) :
            for i2 in range(i+1, n+1):
                tmp.append([-x(i,j), -x(i2,j)])

    # 4-Rompre les symétries
    tmp.append([x(1, 1)])

    while not limite :
        cnf = CNF()

        for clause in tmp :
            cnf.append(clause)

        #3-Valeur de cyclic bandwidth
        for j in range(1,n+1):
             for m in range(1,n+1):
                 if j!=m and dist_cyclique(j, m)>k : #Pour toutes les paires d'etiquettes ne respectant la distance cyclique, on empeche les sommets des arêtes d'avoir ces paires d'étiquettes.
                     for i, l in aretes:
                        cnf.append([-x(i,j), -x(l,m)])

        #4-Rompre les symétries
        cnf.append([x(1,1)])

        solver = Glucose3()

        # Ajouter toutes les clauses du CNF
        for clause in cnf.clauses:
            solver.add_clause(clause)


        sat = solver.solve()

        if sat:
            if trace:
                print("sat pour", k)
            old_k = k
            old_etiquettes = solver.get_model()  # retourne une liste d'entiers : positif = variable vraie, négatif = fausse
            if k<=1 :
                limite = True
            else :
                k = k-1

        else:
            if trace:print("insatisfiable pour", k)
            limite = True



    # Extraire les étiquettes assignées
    if trace :
        etiquettes = {}
        for v in old_etiquettes:
            if v > 0:  # variables vraies
                # Décoder i et j depuis x(i,j)
                i = (v-1)//n + 1
                j = (v-1) % n + 1
                etiquettes[i] = j
        print("Étiquetage trouvé :")
        for i in sorted(etiquettes.keys()):
            print("Sommet v_"+str(i)+" -> Étiquette", etiquettes[i])
        print("Valeur de k :",old_k)
