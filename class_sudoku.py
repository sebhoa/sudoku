"""
Implémentation de sudoku par deux classes
Essais d'implémentations de diverses techniques
de simplification tirées du site :
http://hodoku.sourceforge.net/en/show_example.php?file=h202&tech=Hidden+Pair
"""

import random
import time
import sys
import collections
# import numpy as np finalement je ne vois pas comment utiliser numpy

SIZE = 9
MODULO = 3
NUMBERS = list(range(1,SIZE+1))
VIDE = 0

# Pour dessiner les bordures de la grille
#
TLC = '\u250C'  # Top Left Corner
TIB = '\u252C'  # Top Inner Border
TRC = '\u2510'  # Top Right Corner
MLB = '\u251C'  # Middle Left Border
MIB = '\u253C'  # Middle Inner Border
MRB = '\u2524'  # Middle Right Border
BLC = '\u2514'  # Bottom Left Corner
BIB = '\u2534'  # Bottom Inner Border
BRC = '\u2518'  # Bottom Right Corner
SBO = '\u2500'  # Simple BOrder
VSEP = '|' # Vertical Line

TOP = f'{TLC}{SBO * 7}{TIB}{SBO * 7}{TIB}{SBO * 7}{TRC}'
MIDDLE = f'{MLB}{SBO * 7}{MIB}{SBO * 7}{MIB}{SBO * 7}{MRB}'
BOTTOM = f'{BLC}{SBO * 7}{BIB}{SBO * 7}{BIB}{SBO * 7}{BRC}'

FLAG = False

# Techniques de simplification

TECHNIQUES = ['naked_single', 'hidden_single', 'hidden_pair', 'hidden_triple']
HIDDEN = {2:'hidden_pair', 3:'hidden_triple'}

# -- Une petite fonction utilitaire --
# -- que je ne sais pas trop où mettre  --

def x_pareil(liste, j):
    return [i for i in range(j+1,len(liste)) if liste[i] == liste[j]]

def diff(ens, *args):
    return (x for x in ens if x not in args)

def modulo(x):
    deb = x//MODULO * MODULO
    fin = deb + MODULO
    return (y for y in range(deb, fin))

def block(id_row, id_col):
    return ((lig, col) for lig in modulo(id_row) for col in modulo(id_col) 
                        if lig != id_row or col != id_col)
 

class Case():
    """ Classe qui modélise une case de sudoku """

    # -- Petites fonctions de la classe --

    def by_number_of_candidats(case):
        return len(case.candidats)

    def __init__(self, row, col, val):
        self.val = val          # valeur stockée
        self.id_row = row  # les coordonnées de la case
        self.id_col = col
        self.same_row = {}     # dict des cases de la même ligne
        self.same_col = {}   # dict des cases de la même colonne
        self.same_block = {}     # dict des cases du même carré 3x3
        self.candidats = set(NUMBERS)  # l'ensemble des nombres possibles pour val
        self.impacted = set() # l'ensemble des cases impactées par un changement
        self.interdits = set()  # l'ensemble des nombres interdits


    def __repr__(self):
        if self.val == VIDE:
            return '.'
        else:
            return str(self.val)

    def infos(self):
        """ fonction pour debuggage à supprimer """
        print(f'{self.id_row, self.id_col}', end=' ')
        if self.empty():
            print(f'{self.candidats}')
        else:
            print(f'{self.val}')

    def empty(self):
        return self.val == VIDE

    def set_val(self, v):
        self.val = v
        self.propage()


    def propage(self):
        v = self.val
        for (id_row, id_col), case in self.same_row.items():
            try:
                case.candidats.remove(v)
                self.impacted.add(case)
            except:
                pass
        for (id_row, id_col), case in self.same_col.items():
            try:
                case.candidats.remove(v)
                self.impacted.add(case)
            except:
                pass
        for (id_row, id_col), case in self.same_block.items():
            try:
                case.candidats.remove(v)
                self.impacted.add(case)
            except:
                pass

    def erase_val(self):
        while self.impacted:
            case = self.impacted.pop()
            case.candidats.add(self.val)
        #self.candidats.add(self.val)
        self.val = VIDE

    def singleton(self):
        """ Retourne True ssi la case n'a qu'un seul candidat """
        return len(self.candidats) == 1


class Sudoku(object):
    """Classe Sudoku"""
    
    def __init__(self, name="Unamed", fichier=""):
        # remplissage de la grille : à partir d'un fichier texte
        # s'il existe 
        self.grille = {}        # dictionnaire des cases        
        self.temps = 0          # temps de résolution
        self.solution = False   # on a trouvé une solution
        self.stop = False       # Pour arrêter la résolution
        self.name = name        # nom du fichier
        self.difficulty = ""    # difficulté mais je ne sais pas si ça sert ;-)
        self.cases_vides = []   # la liste des cases vides

        self.candidats_by_row = []
        self.candidats_by_col = []
        self.candidats_by_block = []
        # Pour afficher combien de fois telle ou telle méthode a été utilisée :
        self.profil = {tech:0 for tech in TECHNIQUES}
        self.profil['backtracking'] = 0
        self.init_grille(name, fichier) # pour remplir la grille
        self.init_zones()               # on lance l'initialisation des zones
    

    def __repr__(self):
        """ Affichage d'un beau sudoku avec bordure sympa 
            TODO : trouver une barre verticale plus haute que | """
        chaine = f'{TOP}\n'
        for i in range(SIZE):
            if i > 0 and i % MODULO == 0:
                chaine += f'{MIDDLE}\n'
            for j in range(SIZE):
                if j % MODULO == 0:
                    chaine += f'{VSEP} '
                if not self.empty(i, j):
                    chaine += f'{str(self.case(i, j))} '
                else:
                    chaine += ". "
            chaine += f'{VSEP}\n'
        chaine += f'{BOTTOM}\n'
        return chaine



    # -- Initialisation des diverses infos --

    def init_grille(self, name, fichier):
        if fichier != "":
            with open(fichier, 'r') as fp:
                for id_row, row in enumerate(fp):
                    for id_col, val in enumerate(row.split()):
                        val = int(val)
                        new_case = Case(id_row, id_col, val)
                        self.grille[(id_row, id_col)] = new_case
                        if val == VIDE:
                            self.cases_vides.append(new_case)
                        else:
                            new_case.candidats.clear()


        # en demandant à l'utilisateur sinon            
        else:
            print("Vous n'avez pas fourni de fichier texte.")
            print("Veuillez donner les lignes de chiffres :")
            for id_row in range(SIZE):
                row = input(f'Ligne {i+1} : ')
                for id_col, val in enumerate(row.split()):
                    val = int(val)
                    new_case = Case(id_row, id_col, val)
                    self.grille[(id_row, id_col)] = new_case
                    if val == VIDE:
                        self.cases_vides.append(new_case)
                    else:
                        new_case.candidats.clear()

        self.init_zones()


    def init_zones(self):
        """ 
        Pour chacune des cases initialise les listes ligne, colonne et carre
        et propage éventuellement sa valeur non vide ie l'enleve des candidats
        des zones concernées
        """
        for id_row, id_col in self.grille:
            case = self.case(id_row, id_col)
            case.same_row = {(id_row, a):self.case(id_row, a) for a in diff(range(SIZE), id_col)}
            case.same_col = {(a, id_col):self.case(a, id_col) for a in diff(range(SIZE), id_row)}
            case.same_block = {(a, b):self.case(a, b) for a, b in block(id_row, id_col)}
            if not case.empty():
                case.propage()



    # -- Méthodes concernant une case --

    def case(self, i, j):
        """ Retourne une référence vers la Case de coordonnée (i, j) """
        return self.grille[(i,j)]

    def set_by_coord(self, i, j, v):
        self.case(i,j).set_val(v)

    def set_case(self, case, v):
        """ Demande à la Case case de mettre à jour sa valeur avec v """
        case.set_val(v)
    
    def erase_case(self, case):
        case.erase_val()

    def empty(self, i, j):
        """ Demande à la Case (i, j) si elle est vide """
        return self.case(i,j).empty()
    
    
    def nb_cases_vides(self):
        return len(self.cases_vides)

    def tri_cases_vides(self):
        self.cases_vides.sort(key=Case.by_number_of_candidats)
    
    




    # -- Calcul de positions possibles pour les entiers candidats --

    def set_valeurs(self):
        """
        Pour chaque ligne calcule pour chaque entier n de 1 à 9
        le set des positions (colonnes) où on peut placer n
        Et pour chaque colonne j et pour chaque entier number de 1 à 9
        le set des positions (lignes) où on peut placer number
        """ 
        self.candidats_by_row = {(i, n):set() for i in range(SIZE) for n in NUMBERS}
        self.candidats_by_col = {(j, n):set() for j in range(SIZE) for n in NUMBERS}
        self.candidats_by_block = {(ic, jc, n):set() for ic in range(MODULO) for jc in range(MODULO) for n in NUMBERS}
        for case in self.cases_vides:
            i_carre = case.id_row // MODULO
            j_carre = case.id_col // MODULO
            for n in case.candidats:
                self.candidats_by_row[(case.id_row, n)].add(case.id_col)
                self.candidats_by_col[(case.id_col, n)].add(case.id_row)
                self.candidats_by_block[(i_carre, j_carre, n)].add((case.id_row,case.id_col))


                    



    # -- HIDDEN SINGLE --

    def naked_single(self):
        """
        Si pour une case vide (x,y) il n'y a qu'une
        seule possibilité alors on joue cette valeur
        """
        found = False
        while self.nb_cases_vides() and self.cases_vides[0].singleton():
            case_vide = self.cases_vides.pop(0)
            val = case_vide.candidats.pop()
            self.set_case(case_vide, val)
            found = True
            self.profil['naked_single'] += 1
        if found:
            self.set_valeurs()
        return found

    def hidden_single_by_row(self):
        found = False
        for id_row, number in self.candidats_by_row:
            if len(self.candidats_by_row[(id_row, number)]) == 1:
                self.profil['hidden_single'] += 1
                id_col = self.candidats_by_row[(id_row, number)].pop()
                self.cases_vides.remove(self.case(id_row, id_col))
                self.set_by_coord(id_row, id_col, number)
                found = True
        if found:
            self.set_valeurs()
        return False

    def hidden_single_by_col(self):
        found = False
        for id_col, number in self.candidats_by_col:
            if len(self.candidats_by_col[(id_col, number)]) == 1:
                self.profil['hidden_single'] += 1
                id_row = self.candidats_by_col[(id_col, number)].pop()
                self.set_by_coord(id_row, id_col, number)
                self.cases_vides.remove(self.case(id_row, id_col))
                found = True
        if found:
            self.set_valeurs()
        return found

    def hidden_single_by_block(self):
        found = False
        for id_row, id_col, number in self.candidats_by_block:
            if len(self.candidats_by_block[(id_row, id_col, number)]) == 1:
                self.profil['hidden_single'] += 1
                x, y = self.candidats_by_block[(id_row, id_col, number)].pop()
                self.set_by_coord(x, y, number)
                self.cases_vides.remove(self.case(x, y))
                found = True
        if found:
            self.set_valeurs()
        return found
 
    
    def hidden_single(self):
        """
        Recherche de single 
        """
        found = False
        found = self.hidden_single_by_row() or found
        found = self.hidden_single_by_col() or found 
        found = self.hidden_single_by_block() or found
        return found


    # -- INTERSECTIONS -- 




    # -- HIDDEN SUBSETS --

    def hidden_subset_by_row(self, id_row, k):
        found = False
        subset = {n for n in NUMBERS if 0 < len(self.candidats_by_row[(id_row, n)]) <= k}
        if len(subset) == k:
            cols = {col for n in subset for col in self.candidats_by_row[(id_row, n)]}
            if len(cols) == k:
                for id_col in cols:
                    candidats = self.case(id_row, id_col).candidats
                    inter = candidats & subset
                    if len(candidats) > len(inter):
                        self.case(id_row, id_col).candidats = inter
                        found = True
                if found:
                    self.profil[HIDDEN[k]] += 1
        return found


    def hidden_subset_by_col(self, id_col, k):
        found = False
        subset = {n for n in NUMBERS if 0 < len(self.candidats_by_col[(id_col, n)]) <= k}
        if len(subset) == k:
            row_ids = {a for n in subset for a in self.candidats_by_col[(id_col, n)]}
            if len(row_ids) == k:
                for id_row in row_ids:
                    candidats = self.case(id_row, id_col).candidats
                    inter = candidats & subset
                    if len(candidats) > len(inter):
                        self.case(id_row, id_col).candidats = inter
                        found = True
                if found:
                    self.profil[HIDDEN[k]] += 1
        return found


    def hidden_subset_by_block(self, i_block, j_block, k):
        found = False
        subset = {n for n in NUMBERS if 0 < len(self.candidats_by_block[(i_block, j_block, n)]) <= k}
        if len(subset) == k:
            cases = {(lig, col) for n in subset for lig, col in self.candidats_by_block[(i_block, j_block, n)]}
            if len(cases) == k:
                for id_row, id_col in cases:
                    candidats = self.case(id_row, id_col).candidats
                    inter = candidats & subset
                    if len(candidats) > len(inter):
                        self.case(id_row, id_col).candidats = inter
                        found = True
                if found:
                    self.profil[HIDDEN[k]] += 1
        return found



    def hidden_pair(self):
        """
        Recherche de pair cachés 
        """
        found = False
        for id_row in range(SIZE):
            found = self.hidden_subset_by_row(id_row, 2) or found
        for id_col in range(SIZE):
            found = self.hidden_subset_by_col(id_col, 2) or found 
        for i_carre, j_carre in {(i,j) for i in range(MODULO) for j in range(MODULO)}:
            found = self.hidden_subset_by_block(i_carre, j_carre, 2) or found
        return found


    def hidden_triple(self):
        """
        Recherche de triplets cachés 
        """
        found = False
        for id_row in range(SIZE):
            found = self.hidden_subset_by_row(id_row, 3) or found
        for id_col in range(SIZE):
            found = self.hidden_subset_by_col(id_col, 3) or found 
        for i_carre, j_carre in {(i,j) for i in range(MODULO) for j in range(MODULO)}:
            found = self.hidden_subset_by_block(i_carre, j_carre, 3) or found
        return found


    # -- XY-WINGS --
    # Plus tard



    # -- APPEL AUX TECH DE SIMPLIFICATION --


    def simplifier(self):
        self.set_valeurs()
        changement = True
        while self.nb_cases_vides() > 0 and changement:
            while changement:
                changement = False
                changement = self.naked_single() or changement
                    # changement = True
                    # self.tri_cases_vides()
                    # self.set_valeurs()
                changement = self.hidden_single() or changement
                    # changement = True
                    # self.tri_cases_vides()
                    # self.set_valeurs()
            if not changement and self.nb_cases_vides() > 0:
                if self.hidden_pair():
                    changement = True
                    # self.tri_cases_vides()
                    self.set_valeurs()
                if self.hidden_triple():
                    changement = True
                    # self.tri_cases_vides()
                    self.set_valeurs()



    # -- Recherche de valeurs interdites pour les cases vides --

    def interdites_par_ligne(self):
        """
        Par ligne calcule pour une case donnée si d'autres cases ont exactement
        les mêmes candidats. Si c'est le cas et que le nombre de cases qui partagent
        ces candidats est égal au nombre de cases alors ces candidats doivent être
        interdits dans toutes les autres cases
        """
        trouve = False
        for case in self.cases_vides:
            ligne_id, col_id = case.id_row, case.id_col
            cases_vides_par_lignes = [self.case(ligne_id, x) for x in range(SIZE) if self.empty(ligne_id, x)]
            pareil_que_j = x_pareil(cases_vides_par_lignes, col_id)
            if pareil_que_j != [] and len(pareil_que_j)+1 == len(case.candidats):
                pareil_que_j.append(col_id)
                indices = [k for k in range(SIZE) if k not in pareil_que_j and self.empty(ligne_id, k)]
                nb = 0
                for k in indices:
                    case_k = self.case(ligne_id, k)
                    interdites = case.candidats & case_k.candidats
                    nb = len(interdites)
                    case_k.candidats = case_k.candidats - case.candidats
                if nb > 0:
                    trouve = True
                    self.profil['candidats_identiques'] += 1                                    
        return trouve

    def interdites_par_colonne(self):
        """
        Idem que la fonction interdites_par_ligne mais pour les colonnes
        """
        trouve = False
        for case in self.cases_vides:
            ligne_id, col_id = case.id_row, case.id_col
            cases_vides_par_colonnes = [self.case(x, col_id) for x in range(SIZE) if self.empty(x, col_id)]
            pareil_que_j = x_pareil(cases_vides_par_colonnes, ligne_id)
            if pareil_que_j != [] and len(pareil_que_j)+1 == len(case.candidats):
                pareil_que_j.append(ligne_id)
                indices = [k for k in range(SIZE) if k not in pareil_que_j and self.empty(k, col_id)]
                nb = 0
                for k in indices:
                    case_k = self.case(k, col_id)
                    interdites = case.candidats & case_k.candidats
                    nb = len(interdits)
                    case_k.candidats = case_k.candidats - case.candidats
                if nb > 0:
                    trouve = True
                    self.profil['candidats_identiques'] += 1
        return trouve                                   


    def trouver_valeurs_interdites(self):   
        trouve_par_ligne = self.interdites_par_ligne()
        trouve_par_colonne = self.interdites_par_colonne()
        return trouve_par_ligne or trouve_par_colonne

        
    def simplifier_plus_interdits(self):
        changement = True
        self.set_valeurs()
        while changement:
            changement = False
            self.simplifier()
            # self.set_valeurs()
            changement = self.trouver_valeurs_interdites()
            if changement:
                self.set_valeurs()

    # -- Résolution brute : le backtrack --
    
    def solve_by_backtracking(self, optionTri=True):
        self.tri_cases_vides()
        if self.nb_cases_vides() == 0:
            return True
        else:
            case_vide = self.cases_vides.pop(0)
            memoire = [] # pour mémoriser les candidats (pour les remettre)
            while case_vide.candidats:
                e = case_vide.candidats.pop()
                memoire.append(e)
                self.set_case(case_vide, e)
                self.profil['backtracking'] += 1
                if self.solve_by_backtracking():
                    return True
                else:
                    self.erase_case(case_vide)
                    self.profil['backtracking'] -= 1
            # On est dans une impasse : on remet cette case vide en case vide
            # avec ses candidats avant de retourner False pour dire au-dessus 
            # qu'on est bloqué
            case_vide.candidats.update(memoire)
            self.cases_vides.insert(0, case_vide)
            return False
        
    def solve(self, optionTri=True, optionSingleton=True):
        self.temps = time.time()
        if optionSingleton:
            # self.simplifier_plus_interdits()
            self.simplifier()
        self.solution = self.solve_by_backtracking(optionTri)
        self.temps = time.time() - self.temps
    

    # -- Pour afficher des stats de la résolution --

    def analyse(self):
        nbcar = max(len(s) for s in TECHNIQUES) + 2
        print(f'Statistiques pour {self.name}')
        print('----')
        total = 0
        for technique in TECHNIQUES:
            total += self.profil[technique]
            print(f'{technique:{nbcar}} : {self.profil[technique]:2} résolutions')
        print(f'{"TOTAL":{nbcar}} : {total:2} résolutions')
        print('----')
        print(f'Par backtracking : {self.profil["backtracking"]} cases.')
        if self.solution:
            print(f'Au final, grille résolue en {self.temps:.3f}s')
        else:
            print('Au final, grille non résolue.')
        print('----')
        print(self)






# -- Programme principal si on utilise ce module stand-alone --



def main():
    dossier = 'GrillesDiaboliques'
    id_fic = '36749'
    mon_sudoku = Sudoku(f'big_{id_fic}',f'{dossier}/big_{id_fic}')
    print(mon_sudoku)
    mon_sudoku.solve() 
    mon_sudoku.analyse()
        
if __name__ == "__main__":
    main()