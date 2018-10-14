#! /usr/local/bin/python3

import random, time, sys

SIZE = 9
SMALL = 3

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


class Sudoku(object):
	"""Classe Sudoku"""
	
	def __init__(self, name="Unamed", fichier=""):
		# remplissage de la grille : à partir d'un fichier texte
		# s'il existe 
		self.grille = []
		if fichier != "":
			with open(fichier, 'r') as fp:
				lignes = fp.readlines()
			for i in range(SIZE):
				line = [int(e) for e in lignes[i].split()]
				self.grille.append(line)
		# en demandant à l'utilisateur sinon			
		else:
			print("Vous n'avez pas fourni de fichier texte.")
			print("Veuillez donner les lignes de chiffres :")
			for i in range(SIZE):
				line = [int(e) for e in input("Ligne {} : ".format(i+1)).split()]
				self.grille.append(line)
		self.temps = 0					# temps de résolution
		self.name = name 				# nom du fichier
		self.difficulty = "" 			# difficulté mais je ne sais pas si ça sert ;-)
		self.cases_vides = {} 			# le dictionnaire des cases vides et les valeurs possibles
		# valeurs interdites pour les cases vides :
		self.valeurs_interdites = {(i, j):[] for i in range(SIZE) for j in range(SIZE)}
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
			if i > 0 and i % SMALL == 0:
				chaine += f'{MIDDLE}\n'
			for j in range(SIZE):
				if j % SMALL == 0:
					chaine += f'{VSEP} '
				if not self.vide(i, j):
					chaine += f'{str(self.g(i, j))} '
				else:
					chaine += ". "
			chaine += f'{VSEP}\n'
		chaine += f'{BOTTOM}\n'
		return chaine



	def g(self, i, j):
		return self.grille[i][j]
	
	def set_g(self, i, j, v):
		self.grille[i][j] = v
	
	def vide(self, i, j):
		return self.grille[i][j] == 0
	
	def nb_cases_vides(self):
		return len(self.cases_vides.keys())
	
	
	def set_cases_vides_par_lignes(self):
		res = [[[] for _ in range(SIZE)] for _ in range(SIZE)]
		for x, y in self.cases_vides:
			res[x][y] = self.cases_vides[(x,y)]
		self.cases_vides_par_lignes = res 


	def update_cases_vides(self):
		""" Une des méthodes clé : calcule pour chaque case vide les valeurs possibles 
			Cette info est stockée de 2 façon différentes : par un dict et par une liste
			de lignes """
		def calculValMemeLigne(x,y):
			return [self.g(x,b) for b in range(SIZE) if b != y and not self.vide(x,b)]
		
		def calculValMemeColonne(x,y):
			return [self.g(a,y) for a in range(SIZE) if a != x and not self.vide(a,y)]
		
		def calculValMemeCarre(x,y):
			res = []
			for a in range(SIZE):
				for b in range(SIZE):
					if a//SMALL == x//SMALL and b//SMALL == y//SMALL and a != x and b != y and not self.vide(a,b):
						res.append(self.g(a,b))
			return res
			
		for x in range(SIZE):
			for y in range(SIZE):
				if self.vide(x,y):
					valSurMemeLigne = calculValMemeLigne(x,y)
					valSurMemeColonne = calculValMemeColonne(x,y)
					valSurMemeCarre = calculValMemeCarre(x,y) 
					candidats = []
					for e in range(1,SIZE+1):
						if e not in valSurMemeLigne and e not in valSurMemeColonne and e not in valSurMemeCarre and e not in self.valeurs_interdites[(x,y)]:
							candidats.append(e)
					self.cases_vides[(x,y)] = candidats
				elif (x,y) in self.cases_vides:
					del self.cases_vides[(x,y)]
		self.set_cases_vides_par_lignes()
					
		
	
	
	def set_valeurs_par_lignes(self):
		res = []
		for i in range(SIZE):
			res.append({})
			for j in range(SIZE):
				for number in range(1,SIZE+1):
					if number in self.cases_vides_par_lignes[i][j]:
						res[i][number] = res[i].get(number, []) + [j]
		self.valeurs_par_lignes = res
	
	def set_valeurs_par_colonnes(self):
		res = []
		for j in range(SIZE):
			res.append({})
			for i in range(SIZE):
				for number in range(1,SIZE+1):
					if number in self.cases_vides_par_lignes[i][j]:
						res[j][number] = res[j].get(number, []) + [i]
		self.valeurs_par_colonnes = res
	
	def set_valeurs_par_carres(self):
		res = []
		for i in range(SMALL):
			res.append([])
			for j in range(SMALL):
				res[i].append({})
		for i in range(SIZE):
			i_carre = i // SMALL
			for j in range(SIZE):
				j_carre = j // SMALL
				for number in range(1, SIZE+1):
					if number in self.cases_vides_par_lignes[i][j]:
						res[i_carre][j_carre][number] = res[i_carre][j_carre].get(number, []) + [(i,j)]
		self.valeurs_par_carres = res
	
	def singleton_nu(self):
		nb = 0
		liste = list(self.cases_vides.items())
		liste.sort(key=by_number_of_integers)
		while liste and len(liste[0][1]) == 1:
			x,y = liste[0][0]
			self.set_g(x, y, liste[0][1][0])
			self.update_cases_vides()
			nb += 1
			self.profil['singleton_nu'] += 1
			self.profil['total'] += 1
			liste = list(self.cases_vides.items())
			liste.sort(key=by_number_of_integers)
		return nb
	
	def singleton_cache_par_ligne(self):
		nb = 0
		singleton_trouve = True
		self.set_valeurs_par_lignes()
		while singleton_trouve:
			singleton_trouve = False
			for i in range(SIZE):
				for number in self.valeurs_par_lignes[i]:
					if len(self.valeurs_par_lignes[i][number]) == 1:
						nb += 1
						self.profil['singleton_cache_par_ligne'] += 1
						self.profil['total'] += 1
						self.set_g(i, self.valeurs_par_lignes[i][number][0], number)
						self.update_cases_vides()
						self.set_valeurs_par_lignes()
		return nb
	
	def singleton_cache_par_colonne(self):
		nb = 0
		singleton_trouve = True
		self.set_valeurs_par_colonnes()
		while singleton_trouve:
			singleton_trouve = False
			for i in range(SIZE):
				for number in self.valeurs_par_colonnes[i]:
					if len(self.valeurs_par_colonnes[i][number]) == 1:
						nb += 1
						self.profil['singleton_cache_par_colonne'] += 1
						self.profil['total'] += 1
						self.set_g(self.valeurs_par_colonnes[i][number][0], i, number)
						self.update_cases_vides()
						self.set_valeurs_par_colonnes()
		return nb
	
	def singleton_cache_par_carre(self):
		nb = 0
		modulo = SIZE // 3
		singleton_trouve = True
		self.set_valeurs_par_carres()
		while singleton_trouve:
			singleton_trouve = False
			for i in range(modulo):
				for j in range(modulo):
					for number in self.valeurs_par_carres[i][j]:
						if len(self.valeurs_par_carres[i][j][number]) == 1:
							nb += 1
							self.profil['singleton_cache_par_carre'] += 1
							self.profil['total'] += 1
							x, y = self.valeurs_par_carres[i][j][number][0]
							self.set_g(x, y, number)
							self.update_cases_vides()
							self.set_valeurs_par_carres()
		return nb
	
	def trouver_valeurs_interdites(self):

		def x_pareil(liste, j):
			return [i for i in range(j+1,len(liste)) if i != j and liste[i] == liste[j]]
	
		t1 = time.time()
		trouve = False
		# trouver des valeurs par lignes
		for ligne_id in range(SIZE):
			for col_id in range(SIZE):
				if self.vide(ligne_id, col_id):
					pareil_que_j = x_pareil(self.cases_vides_par_lignes[ligne_id], col_id)
					#print("Sur ligne {} les pareils que {} : {}".format(ligne_id,col_id,pareil_que_j))
					#print("trouve avant",trouve)
					if pareil_que_j != [] and len(pareil_que_j)+1 == len(self.cases_vides[(ligne_id, col_id)]):
						pareil_que_j.append(col_id)
						interdites = self.cases_vides[(ligne_id, col_id)]
						indices = [k for k in range(SIZE) if k not in pareil_que_j and self.vide(ligne_id, k)]
						nb = 0
						for k in indices:
							for e in interdites:
								if e not in self.valeurs_interdites[(ligne_id, k)]:
									self.valeurs_interdites[(ligne_id, k)].append(e)
									nb += 1
						if nb > 0:
							trouve = True
							self.profil['candidats_identiques'] += 1									
					#print("trouve apres",trouve)
		# trouver des valeurs par colonnes
		for col_id in range(SIZE):
			valeurs_par_colonnes = [self.cases_vides_par_lignes[i][col_id] for i in range(SIZE)]
			for ligne_id in range(SIZE):
				if valeurs_par_colonnes[ligne_id] != []:
					pareil_que_j = x_pareil(valeurs_par_colonnes, ligne_id)
					if pareil_que_j != [] and len(pareil_que_j)+1 == len(self.cases_vides[(ligne_id, col_id)]):
						pareil_que_j.append(ligne_id)
						interdites = self.cases_vides[(ligne_id, col_id)]
						indices = [k for k in range(SIZE) if k not in pareil_que_j and self.vide(k, col_id)]
						#print(self)
						#print("Colonne {} : ".format(col_id))
						#print("\tIndices de colonnes Valeurs pareil : {} -- valeurs = {}".format(pareil_que_j, interdites))
						#print("\tIndices à épurer : {}".format(indices))
						#h = input()
						nb = 0
						for k in indices:
							for e in interdites:
								if e not in self.valeurs_interdites[(k, col_id)]:
									self.valeurs_interdites[(k, col_id)].append(e)
									nb += 1
						if nb > 0:
							trouve = True
							self.profil['candidats_identiques'] += 1									
		return trouve
		
	
	def simplifier(self):
		t1 = time.time()
		changement = True
		while changement:
			changement = False
			nb_singleton_nu = self.singleton_nu()
			if nb_singleton_nu > 0:
				changement = True
			self.set_valeurs_par_lignes()
			nb_par_ligne = self.singleton_cache_par_ligne()
			#print("Nombres de singleton cachés par ligne : {}".format(nb_par_ligne))
			if nb_par_ligne > 0:
				#print(self)
				changement = True
			self.set_valeurs_par_colonnes()
			nb_par_colonne = self.singleton_cache_par_colonne()
			#print("Nombres de singleton cachés par colonne : {}".format(nb_par_colonne))
			if nb_par_colonne > 0:
				#print(self)
				changement = True
			self.set_valeurs_par_carres()
			nb_par_carre = self.singleton_cache_par_carre()
			#print("Nombres de singleton cachés par carré : {}".format(nb_par_carre))
			if nb_par_carre > 0:
				#print(self)
				changement = True
		t2 = time.time()
		self.temps += t2-t1			
	
	def simplifier_plus_interdits(self):
		changement = True
		while changement:
		#for i in range(1):
			changement = False
			self.simplifier()
			self.update_cases_vides()
			changement = self.trouver_valeurs_interdites()
			self.update_cases_vides()
			#print(self)
			#h = input()
			#print(self.valeurs_interdites)
			#for i in range(9):
			#	print(self.cases_vides_par_lignes[i])
			#print(self.profil['candidats_identiques'])
			
	
	def backtracking(self, optionTri=True):
		self.update_cases_vides()
		if self.nb_cases_vides() == 0:
			return True
		else:
			liste = list(self.cases_vides.items())
			if optionTri:
				liste.sort(key=by_number_of_integers)
			x, y = liste[0][0]
			candidats = liste[0][1]
			while candidats:
				e = random.choice(candidats)
				candidats.remove(e)
				self.set_g(x, y, e)
				self.profil['backtracking'] += 1
				if self.backtracking():
					return True
				else:
					self.set_g(x, y, 0)
					self.profil['backtracking'] -= 1
			return False
	
	def solve_by_backtracking(self, optionTri):
		t1 = time.time()
		if self.backtracking(optionTri):
			t2 = time.time()
			self.temps += t2-t1
		else:
			self.temps = -1
	
	def solve(self, optionTri=True, optionSingleton=True):
		self.update_cases_vides()
		if optionSingleton:
			self.simplifier_plus_interdits()
			#self.simplifier()
		self.solve_by_backtracking(optionTri)
	
	def analyse(self):
		print("\n")
		print("Statistiques pour {}".format(self.name))
		print('----')
		for technique in ['singleton_nu', 'singleton_cache_par_ligne', 'singleton_cache_par_colonne',  
		'singleton_cache_par_carre', 'candidats_identiques']:
			print("{:30} : {:2} résolutions".format(technique, self.profil[technique]))
		print("{:30} : {:2} résolutions".format("TOTAL",self.profil['total']))
		print("----")
		print("Par backtracking : {} cases.".format(self.profil['backtracking']))
		if self.temps > -1:
			print("Au final, grille résolue en {:5.3f}s".format(self.temps))
		else:
			print("Au final, grille non résolue.")
		print('----')
		print(self)
	
	


def by_number_of_integers(candidat):
	return len(candidat[1])



def main():
	grille = Sudoku("","GrillesMotCroises_ch/grille_004.txt")
	print(grille)
	grille.update_cases_vides()
	grille.simplifier_plus_interdits()
	#grille.update_cases_vides()
	#print(grille)
	#for i in range(grille.Taille):
	#	print(grille.cases_vides_par_lignes[i])
	#grille.trouver_valeurs_interdites()
	#print(grille.valeurs_interdites)
	#grille.update_cases_vides()
	#for i in range(grille.Taille):
	#	print(grille.cases_vides_par_lignes[i])
	#grille.simplifier()
	print(grille)
	#grille.update_cases_vides()
	

		
if __name__ == "__main__":
	main()