#! /usr/local/bin/python3

import random
import time
import sys
import collections
import numpy as np

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


# -- Deux petites fonctions utilitaires --
# -- que je ne sais pas trop où mettre  --

def by_number_of_integers(candidat):
    """ Pour le tri des cases vides suivant le nombre de candidats """
    return len(candidat[1])

def x_pareil(liste, j):
    return [i for i in range(j+1,len(liste)) if liste[i] == liste[j]]



class Case():
    """ Classe qui modélise une case de sudoku """

    # -- Petites fonctions de la classe --

    def by_number_of_candidats(case):
        return len(case.candidats)

    def __init__(self, id_ligne, id_col, val):
        self.val = val          # valeur stockée
        self.id_lig = id_ligne  # les coordonnées de la case
        self.id_col = id_col
        self.ligne = []     # liste des cases de la même ligne
        self.colonne = []   # liste des cases de la même colonne
        self.carre = []     # liste des cases du même carré 3x3
        self.candidats = set(NUMBERS)  # l'ensemble des nombres possibles pour val
        self.interdits = set()  # l'ensemble des nombres interdits
        self.cases_impactees = set() # l'ensemble des cases impactées par un changement


    def __repr__(self):
        if self.val == VIDE:
            return '.'
        else:
            return str(self.val)

    def infos(self):
        print(f'{self.id_lig, self.id_col}', end=' ')
        if self.vide():
            print(f'{self.candidats}')
        else:
            print(f'{self.val}')

    def vide(self):
        return self.val == VIDE

    def set_val(self, v):
        self.val = v
        self.propage()


    def propage(self):
        v = self.val
        for case in self.ligne:
            try:
                case.candidats.remove(v)
                self.cases_impactees.add(case)
            except:
                pass
        for case in self.colonne:
            try:
                case.candidats.remove(v)
                self.cases_impactees.add(case)
            except:
                pass
        for case in self.carre:
            try:
                case.candidats.remove(v)
                self.cases_impactees.add(case)
            except:
                pass

    def erase_val(self):
        while self.cases_impactees:
            case = self.cases_impactees.pop()
            case.candidats.add(self.val)
        #self.candidats.add(self.val)
        self.val = VIDE



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

        self.valeurs_par_lignes = []
        self.valeurs_par_colonnes = []
        self.valeurs_par_carres = []
        # Pour afficher combien de fois telle ou telle méthode a été utilisée :
        self.profil = {'total':0, 'singleton_nu':0, 'singleton_cache_par_ligne':0, 
                        'singleton_cache_par_colonne':0,  
                        'singleton_cache_par_carre':0, 
                        'backtracking':0, 
                        'candidats_identiques':0} 
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
                if not self.vide(i, j):
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
                for id_ligne, ligne in enumerate(fp):
                    for id_col, val in enumerate(ligne.split()):
                        val = int(val)
                        new_case = Case(id_ligne, id_col, val)
                        self.grille[(id_ligne, id_col)] = new_case
                        if val == VIDE:
                            self.cases_vides.append(new_case)


        # en demandant à l'utilisateur sinon            
        else:
            print("Vous n'avez pas fourni de fichier texte.")
            print("Veuillez donner les lignes de chiffres :")
            for id_ligne in range(SIZE):
                ligne = input(f'Ligne {i+1} : ')
                for id_col, val in enumerate(ligne.split()):
                    val = int(val)
                    new_case = Case(id_ligne, id_col, val)
                    self.grille[(id_ligne, id_col)] = new_case
                    if val == VIDE:
                        self.cases_vides.append(new_case)

        self.init_zones()


    def init_zones(self):
        """ 
        Pour chacune des cases initialise les listes ligne, colonne et carre
        et propage éventuellement sa valeur non vide ie l'enleve des candidats
        des zones concernées
        """
        for id_ligne, id_col in self.grille:
            deb_l = (id_ligne // MODULO) * MODULO
            fin_l = deb_l + MODULO
            deb_c = (id_col // MODULO) * MODULO
            fin_c = deb_c + MODULO
            case = self.case(id_ligne, id_col)
            case.ligne = [self.case(id_ligne, col) 
                    for col in range(SIZE) if col != id_col]
            case.colonne = [self.case(lig, id_col) 
                    for lig in range(SIZE) if lig != id_ligne]
            case.carre = [self.case(lig, col)
                    for lig in range(deb_l, fin_l) for col in range(deb_c, fin_c)
                    if col != id_col and lig != id_ligne]
            if not case.vide():
                case.propage()



    # -- Méthodes concernant une case --

    def case(self, i, j):
        """ Retourne une référence vers la Case de coordonnée (i, j) """
        return self.grille[(i,j)]

    def set_case(self, case, v):
        """ Demande à la Case case de mettre à jour sa valeur avec v """
        case.set_val(v)
    
    def erase_case(self, case):
        case.erase_val()

    def vide(self, i, j):
        """ Demande à la Case (i, j) si elle est vide """
        return self.case(i,j).vide()
    
    
    def nb_cases_vides(self):
        return len(self.cases_vides)

    def tri_cases_vides(self):
        self.cases_vides.sort(key=Case.by_number_of_candidats)
    
    

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
        # self.update_cases_vides()
        # if optionSingleton:
        #     self.simplifier_plus_interdits()
        self.solution = self.solve_by_backtracking(optionTri)
        self.temps = time.time() - self.temps
    

    # -- Pour afficher des stats de la résolution --

    def analyse(self):
        print('\n')
        print(f'Statistiques pour {self.name}')
        print('----')
        for technique in ['singleton_nu', 'singleton_cache_par_ligne', 'singleton_cache_par_colonne',  
        'singleton_cache_par_carre', 'candidats_identiques']:
            print(f'{technique:30} : {self.profil[technique]:2} résolutions')
        print(f'{"TOTAL":30} : {self.profil["total"]:2} résolutions')
        print('----')
        print(f'Par backtracking : {self.profil["backtracking"]} cases.')
        if self.solution:
            print(f'Au final, grille résolue en {self.temps:5.3f}s')
        else:
            print('Au final, grille non résolue.')
        print('----')
        print(self)






# -- Programme principal si on utilise ce module stand-alone --



def main():
    dossier = 'GrillesDiaboliques'
    id_fic = '36378'
    mon_sudoku = Sudoku("",f'{dossier}/big_{id_fic}')
    print(mon_sudoku)
    # for i, j in mon_sudoku.grille:
    #     print(mon_sudoku.case(i, j).candidats)
    # input()
    mon_sudoku.solve() 
    print(mon_sudoku)
    print(f'Résolu en {mon_sudoku.temps:3f}s')   

        
if __name__ == "__main__":
    main()