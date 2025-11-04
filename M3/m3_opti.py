import argparse
import math
import sys
from collections import deque

from pysat.formula import CNF
from pysat.solvers import Glucose3


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


def x(i, j):
    """
    Calcul un identifiant unique pour un x_ij
    :param i: sommet v_i
    :param j: valeur de l'étiquette
    :return: identifiant du booléen représentant la possibilité d'avoir l'étiquette j sur v_i
    """
    return n * (i - 1) + j

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

    tmp = []
    k = optimiser_k(sommets, aretes)  # Borne de départ
    old_k = -1
    old_etiquettes = []
    limite = False

    # 1-Une seule étiquette par sommets
    for i in sommets:  # Pour tous les sommets v_i
        # Au moins une étiquette par sommet
        tmp.append([x(i, j) for j in range(1, n + 1)])

        # Au maximum une étiquette par sommet
        # On fait tous les couples de valeurs de l'etiquette de v_i, et on vérifie qu'au moins une valeur du couple n'est pas séléctionnée. Pour éviter d'avoir 2 valeurs d'étiquettes sur v_i
        for j in range(1, n + 1):
            for j2 in range(j + 1, n + 1):
                tmp.append([-x(i, j), -x(i, j2)])

    # 2-Toutes les étiquettes sont différentes
    for j in range(1, n + 1):  # Pour toutes les valeurs d'étiquettes j
        tmp.append([x(i, j) for i in range(1, n + 1)])  # Toutes les étiquettes ont au moins un noeud
        for i in range(1, n + 1):
            for i2 in range(i + 1, n + 1):
                tmp.append([-x(i, j), -x(i2, j)])

    # 4-Rompre les symétries
    tmp.append([x(1, 1)])

    while not limite:
        cnf = CNF()

        for clause in tmp:
            cnf.append(clause)

        # 3-Valeur de cyclic bandwidth
        for j in range(1, n + 1):
            for m in range(1, n + 1):
                if j != m and dist_cyclique(j,
                                            m) > k:  # Pour toutes les paires d'etiquettes ne respectant la distance cyclique, on empeche les sommets des arêtes d'avoir ces paires d'étiquettes.
                    for i, l in aretes:
                        cnf.append([-x(i, j), -x(l, m)])

        # 4-Rompre les symétries
        cnf.append([x(1, 1)])

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
            if k <= 1:
                limite = True
            else:
                k = k - 1

        else:
            if trace: print("insatisfiable pour", k)
            limite = True

    if old_k == -1:
        sys.exit(1)
    else:
        # Extraire les étiquettes assignées
        etiquettes = {}
        for v in old_etiquettes:
            if v > 0:  # variables vraies
                # Décoder i et j depuis x(i,j)
                i = (v - 1) // n + 1
                j = (v - 1) % n + 1
                etiquettes[i] = j
        print("Étiquetage trouvé :")
        for i in sorted(etiquettes.keys()):
            print("Sommet v_" + str(i) + " -> Étiquette", etiquettes[i])
        print("CYCLIC_BANDWIDTH :", max([dist_cyclique(etiquettes[u], etiquettes[v]) for u,v in aretes]))
        sys.exit(0)
