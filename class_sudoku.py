#! /usr/local/bin/python3

import random
import time
import sys
import collections
import numpy as np

SIZE = 9
MODULO = 3
NUMBERS = list(range(1,SIZE+1))

# Pour dessiner les bordures de la grille
#
TLC = '\u250C'	# Top Left Corner
TIB = '\u252C'	# Top Inner Border
TRC = '\u2510'	# Top Right Corner
MLB = '\u251C'	# Middle Left Border
MIB = '\u253C'	# Middle Inner Border
MRB = '\u2524'	# Middle Right Border
BLC = '\u2514'	# Bottom Left Corner
BIB = '\u2534'	# Bottom Inner Border
BRC = '\u2518'	# Bottom Right Corner
SBO = '\u2500'	# Simple BOrder
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


class Sudoku(object):
	"""Classe Sudoku"""
	

	def __init__(self, name="Unamed", fichier=""):
		# remplissage de la grille : à partir d'un fichier texte
		# s'il existe 
		self.grille = np.full((SIZE, SIZE), 0)
		if fichier != "":
			with open(fichier, 'r') as fp:
				for id_ligne, ligne in enumerate(fp):
					self.grille[id_ligne] = [int(e) for e in ligne.split()]
		# en demandant à l'utilisateur sinon			
		else:
			print("Vous n'avez pas fourni de fichier texte.")
			print("Veuillez donner les lignes de chiffres :")
			for id_ligne in range(SIZE):
				self.grille[id_ligne] = [int(e) for e in input(f'Ligne {i+1} : ').split()]
		self.temps = 0					# temps de résolution
		self.solution = False			# on a trouvé une solution
		self.stop = False				# Pour arrêter la résolution
		self.name = name 				# nom du fichier
		self.difficulty = "" 			# difficulté mais je ne sais pas si ça sert ;-)
		self.cases_vides = {} 			# le dictionnaire des cases vides et les valeurs possibles
		# valeurs interdites pour les cases vides :
		self.valeurs_interdites = {(i, j):set() for i in range(SIZE) for j in range(SIZE)}
		self.cases_vides_par_lignes = []
		self.valeurs_par_lignes = []
		self.valeurs_par_colonnes = []
		self.valeurs_par_carres = []
		# Pour afficher combien de fois telle ou telle méthode a été utilisée :
		self.profil = {'total':0, 'singleton_nu':0, 'singleton_cache_par_ligne':0, 
						'singleton_cache_par_colonne':0,  
						'singleton_cache_par_carre':0, 
						'backtracking':0, 
						'candidats_identiques':0} 
	

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
					chaine += f'{str(self.g(i, j))} '
				else:
					chaine += ". "
			chaine += f'{VSEP}\n'
		chaine += f'{BOTTOM}\n'
		return chaine



	def g(self, i, j):
		return self.grille[i,j]
	
	def set_g(self, i, j, v):
		self.grille[i,j] = v
	
	def vide(self, i, j):
		return self.grille[i,j] == 0
	
	def nb_cases_vides(self):
		return len(self.cases_vides.keys())
	
	
	def set_cases_vides_par_lignes_colonnes(self):
		self.cases_vides_par_lignes = [[set() for _ in range(SIZE)] for _ in range(SIZE)]
		self.cases_vides_par_colonnes = [[set() for _ in range(SIZE)] for _ in range(SIZE)]
		for x, y in self.cases_vides:
			self.cases_vides_par_lignes[x][y] = self.cases_vides[(x,y)]
			self.cases_vides_par_colonnes[y][x] = self.cases_vides[(x,y)]


	def val_sur_meme_ligne(self, x, y):
		"""
		Les valeurs qui se trouvent sur la même ligne x, ailleurs qu'en y
		"""
		return [self.g(x,b) for b in range(SIZE) if b != y and not self.vide(x,b)]
	
	def val_sur_meme_col(self, x, y):
		"""
		Les valeurs qui se trouvent sur la même colonne y, ailleurs qu'en x
		"""
		return [self.g(a,y) for a in range(SIZE) if a != x and not self.vide(a,y)]
	
	def val_sur_meme_carre(self, x, y):
		"""
		Les valeurs qui se trouvent sur le même carré 3x3, ailleurs qu'en x,y
		"""
		deb_a = (x // MODULO) * MODULO
		fin_a = deb_a + MODULO
		deb_b = (y // MODULO) * MODULO
		fin_b = deb_b + MODULO
		return [self.g(a,b) for a in range(deb_a, fin_a) for b in range(deb_b, fin_b)
				if (a != x or b != y) and not self.vide(a,b)]

	def update_cases_vides(self):
		""" Une des méthodes clé : calcule pour chaque case vide les valeurs possibles 
			Cette info est stockée de 2 façon différentes : par un dict et par une liste
			de lignes """		
		for x in range(SIZE):
			for y in range(SIZE):
				if self.vide(x,y):
					valSurMemeLigne = self.val_sur_meme_ligne(x,y)
					valSurMemeColonne = self.val_sur_meme_col(x,y)
					valSurMemeCarre = self.val_sur_meme_carre(x,y) 
					# if FLAG:
					# 	print(f'Pour {x, y}')
					# 	print(valSurMemeLigne)
					# 	print(valSurMemeColonne)
					# 	print(valSurMemeCarre)
					candidats = set()
					for e in NUMBERS:
						if e not in valSurMemeLigne and e not in valSurMemeColonne and e not in valSurMemeCarre and e not in self.valeurs_interdites[(x,y)]:
							candidats.add(e)
					self.cases_vides[(x,y)] = candidats
				elif (x,y) in self.cases_vides:
					del self.cases_vides[(x,y)]
		self.set_cases_vides_par_lignes_colonnes()
		

	def set_valeurs_par_lignes(self):
		"""
		Pour chaque ligne calcule pour chaque entier n de 1 à 9
		le set des positions (colonnes) où on peut placer n
		""" 
		self.valeurs_par_lignes = {(i, n):set() for i in range(SIZE) for n in NUMBERS}
		for i, j in self.cases_vides:
			for n in self.cases_vides[(i,j)]:
				self.valeurs_par_lignes[(i, n)].add(j)

	
	def set_valeurs_par_colonnes(self):
		"""
		Pour chaque colonne j et pour chaque entier number de 1 à 9
		le set des positions (lignes) où on peut placer number
		""" 
		self.valeurs_par_colonnes = {(j, n):set() for j in range(SIZE) for n in NUMBERS}
		for i, j in self.cases_vides:
			for n in self.cases_vides[(i,j)]:
				self.valeurs_par_colonnes[(j, n)].add(i)

	
	def set_valeurs_par_carres(self):
		"""
		Pour chacun des carres 3x3 et pour chacun des nombres 1 à 9
		calcule les coordonnées i, j possible pour number
		"""
		self.valeurs_par_carres = {(ic, jc, n):set() for ic in range(MODULO) for jc in range(MODULO) for n in NUMBERS}
		for i, j in self.cases_vides:
			i_carre = i // MODULO
			j_carre = j // MODULO
			for n in self.cases_vides[(i,j)]:
				self.valeurs_par_carres[(i_carre, j_carre, n)].add((i,j))
	
	
	def set_valeurs(self):
		self.update_cases_vides()
		self.set_valeurs_par_lignes()
		self.set_valeurs_par_colonnes()
		self.set_valeurs_par_carres()	




	# -- Recherche de singletons --

	def singleton_nu(self):
		"""
		Si pour une case vide (x,y) il n'y a qu'une
		seule possibilité alors on joue cette valeur
		"""
		nb = 0
		liste = list(self.cases_vides.items())
		liste.sort(key=by_number_of_integers)
		while liste and len(liste[0][1]) == 1:
			x,y = liste[0][0]
			self.set_g(x, y, liste[0][1].pop())
			self.update_cases_vides()
			nb += 1
			self.profil['singleton_nu'] += 1
			self.profil['total'] += 1
			liste = list(self.cases_vides.items())
			liste.sort(key=by_number_of_integers)
		return nb
	
	def singleton_cache_par_ligne(self):
		for id_ligne, number in self.valeurs_par_lignes:
			if len(self.valeurs_par_lignes[(id_ligne, number)]) == 1:
				self.profil['singleton_cache_par_ligne'] += 1
				self.profil['total'] += 1
				id_col = self.valeurs_par_lignes[(id_ligne, number)].pop()
				self.set_g(id_ligne, id_col, number)
				return True
		return False
	
	def singleton_cache_par_colonne(self):
		for id_col, number in self.valeurs_par_colonnes:
			if len(self.valeurs_par_colonnes[(id_col, number)]) == 1:
				self.profil['singleton_cache_par_colonne'] += 1
				self.profil['total'] += 1
				id_ligne = self.valeurs_par_colonnes[(id_col, number)].pop()
				self.set_g(id_ligne, id_col, number)
				return True
		return False
	
	def singleton_cache_par_carre(self):
		for id_ligne, id_col, number in self.valeurs_par_carres:
			if len(self.valeurs_par_carres[(id_ligne, id_col, number)]) == 1:
				self.profil['singleton_cache_par_carre'] += 1
				self.profil['total'] += 1
				x, y = self.valeurs_par_carres[(id_ligne, id_col, number)].pop()
				self.set_g(x, y, number)
				return True
		return False
	


	# -- Recherche de valeurs interdites pour les cases vides --

	def interdites_par_ligne(self):
		"""
		Par ligne calcule pour une case donnée si d'autres cases ont exactement
		les mêmes candidats. Si c'est le cas et que le nombre de cases qui partagent
		ces candidats est égal au nombre de cases alors ces candidats doivent être
		interdits dans toutes les autres cases
		"""
		trouve = False
		for ligne_id, col_id in self.cases_vides:
			pareil_que_j = x_pareil(self.cases_vides_par_lignes[ligne_id], col_id)
			if pareil_que_j != [] and len(pareil_que_j)+1 == len(self.cases_vides[(ligne_id, col_id)]):
				pareil_que_j.append(col_id)
				indices = [k for k in range(SIZE) if k not in pareil_que_j and self.vide(ligne_id, k)]
				nb = 0
				for k in indices:
					interdites = self.cases_vides[(ligne_id, col_id)] & self.cases_vides[(ligne_id, k)]
					for e in interdites:
						self.valeurs_interdites[(ligne_id, k)].add(e)
						nb += 1
				if nb > 0:
					trouve = True
					self.profil['candidats_identiques'] += 1									
		return trouve

	def interdites_par_colonne(self):
		"""
		Idem que la fonction interdites_par_ligne mais pour les colonnes
		"""
		trouve = False
		for ligne_id, col_id in self.cases_vides:
			pareil_que_j = x_pareil(self.cases_vides_par_colonnes[col_id], ligne_id)
			if pareil_que_j != [] and len(pareil_que_j)+1 == len(self.cases_vides[(ligne_id, col_id)]):
				pareil_que_j.append(ligne_id)
				indices = [k for k in range(SIZE) if k not in pareil_que_j and self.vide(k, col_id)]
				nb = 0
				for k in indices:
					interdites = self.cases_vides[(ligne_id, col_id)] & self.cases_vides[(k, col_id)]
					for e in interdites:
						self.valeurs_interdites[(k, col_id)].add(e)
						nb += 1
				if nb > 0:
					trouve = True
					self.profil['candidats_identiques'] += 1
		return trouve									


	def trouver_valeurs_interdites(self):	
		trouve_par_ligne = self.interdites_par_ligne()
		trouve_par_colonne = self.interdites_par_colonne()
		return trouve_par_ligne or trouve_par_colonne
		
	

	# -- Techniques pour simplifier, réduire --

	def simplifier(self):
		changement = True
		while changement:
			changement = False
			if self.singleton_nu():
				changement = True
				self.update_cases_vides()
				self.set_valeurs()
			if self.singleton_cache_par_ligne():
				changement = True
				self.update_cases_vides()
				self.set_valeurs()
			if self.singleton_cache_par_colonne():
				changement = True
				self.update_cases_vides()
				self.set_valeurs()
			if self.singleton_cache_par_carre():
				changement = True
				self.update_cases_vides()
				self.set_valeurs()
	
	
	def simplifier_plus_interdits(self):
		changement = True
		self.set_valeurs()
		while changement:
			changement = False
			self.simplifier()
			self.update_cases_vides()
			self.set_valeurs()
			changement = self.trouver_valeurs_interdites()
			if changement:
				self.update_cases_vides()
				self.set_valeurs()
			# for k, s in self.valeurs_interdites.items():
			# 	if s:
			# 		print(f'{k} : {s}')
			# print(self)
			


	# -- Résolution brute : le backtrack --
	
	def solve_by_backtracking(self, optionTri=True):
		self.update_cases_vides()
		if self.nb_cases_vides() == 0:
			return True
		else:
			# self.simplifier_plus_interdits()
			liste = list(self.cases_vides.items())
			# if optionTri:
			liste.sort(key=by_number_of_integers)
			x, y = liste[0][0]
			candidats = liste[0][1]
			while candidats:
				e = candidats.pop()
				self.set_g(x, y, e)
				self.profil['backtracking'] += 1
				if self.solve_by_backtracking():
					return True
				else:
					self.set_g(x, y, 0)
					self.profil['backtracking'] -= 1
			return False
		
	def solve(self, optionTri=True, optionSingleton=True):
		self.temps = time.time()
		self.update_cases_vides()
		if optionSingleton:
			self.simplifier_plus_interdits()
		self.solution = self.solve_by_backtracking(optionTri)
		self.temps = time.time() - self.temps
	
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
	grille = Sudoku("","GrillesMotCroises_ch/grille_004.txt")
	print(grille)
	grille.update_cases_vides()
	grille.simplifier_plus_interdits()
	print(grille)
	

		
if __name__ == "__main__":
	main()