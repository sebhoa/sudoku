#! /usr/local/bin/python3

import random, time, sys, getopt, os
import class_sudoku

# CONSTANTES
# ----------
HelpMessage = '''
sudoku -- Resoud une grille de sudoku

SYNOPSIS
	sudoku [-u] [grille]
	sudoku -d rep [-u] [grille]
	sudoku -h
	
DESCRIPTION
	sudoku résoud une grille passée en paramètre et stockée dans un fichier texte.
	Si aucune grille n'est fournie, une grille par défaut sera résolue. Le script
	affiche la grille vide puis la grille résolue.
	
	Les options suivantes sont disponibles :
	
	-h	
		Affiche cet écran.
	
	-d rep [grille]
		Résoud la grille du répertoire rep. Si aucune grille n'est fournie
		le script résoud toutes les grilles du répertoire et affiche
		uniquement le temps mis pour chacune puis, à la fin, le temps moyen.
	
	-u
		Si cette option est présente, les cases du sudoku ne sont pas remplies
		dans l'ordre de celle qui présente le moins de candidats.
		
	-a
		Choisi les candidats aléatoirement. Sinon ils sont pris dans l'ordre croissant.
		
	-s
		Si cette option est présente, le système ne recherche pas de singletons avant de 
		lancer le backtracking.
'''

Options = "suhd:c:"

GrilleParDefaut = "rr_07_10_4_expert"
RepParDefaut = "AutresGrilles"
Home = "."

def afficher_lignes_candidats(tab):
	for i in range(9):
		print("Ligne {} : ".format(i+1),end="")
		for j in range(9):
			print(tab[i][j],end=" ")
		print()


def afficher_valeurs_par_ligne(tab):
	for i in range(9):
		print("Ligne {} : ".format(i+1))
		for number in tab[i]:
			print("\t{} -> {}".format(number, tab[i][number]))

def afficher_valeurs_par_colonne(tab):
	for i in range(9):
		print("Colonne {} : ".format(i+1))
		for number in tab[i]:
			print("\t{} -> {}".format(number, tab[i][number]))

def afficher_valeurs_par_carre(tab):
	for i in range(3):
		for j in range(3):
			print("Carré {},{} : ".format(i, j))
			for number in tab[i][j]:
				print("\t{} -> {}".format(number, tab[i][j][number]))



# -- Settings ----
# ----------------
def recupAllFiles(rep):
	return os.listdir(rep)

def settings(argv):
	try:
		opts, args = getopt.getopt(argv,Options)
	except getopt.error:
		msg = sys.exc_info()[1]
		print("Error: {}".format(msg))
		sys.exit(HelpMessage)
	
	# option processing
	rep = RepParDefaut
	optTri = True
	optChoix = "nonAlea"
	optionD = False
	optionS = True
	if opts:
		for option, value in opts:
			if option == "-h":
				sys.exit(HelpMessage)
			if option == "-c":
				optChoix = value
			if option == "-u":
				optTri = False
			if option == "-d":
				optionD = True
				rep = value
				if len(args) < 1:
					fichier = recupAllFiles(os.path.join(Home,rep))
				elif len(args) < 2:
					fichier = [args[0]]
				else:
					print("Trop d'arguments")
					sys.exit(HelpMessage)
			if option == '-s':
				optionS = False
				
	if not optionD:
		if len(args) < 1:
			fichier = [GrilleParDefaut]
		elif len(args) < 2:
			fichier = [args[0]]
		else:
			print("Trop d'arguments")
			sys.exit(HelpMessage)
	return fichier, rep, optTri, optChoix, optionS

def afficheResume(tps):
	if len(tps) > 1:
		print("-------------------------")
		print("Temps moyen : {:2.2f}s".format(sum(tps)/len(tps)))

# Traiter 1 ou plusieurs grilles ?
def solveOneOrMore(l, rep, optTri, optChoix, optSingleton):
	tps = []
	toutes_les_grilles = {}
	for fic in l:
		taille = len(l)
		grille = class_sudoku.Sudoku(fic,os.path.join(Home,rep,fic))
		toutes_les_grilles[fic] = grille
		print("{} : {}".format("\nGrille", fic))
		if taille == 1:
			print(grille)
		grille.solve(optTri, optSingleton)
		if optChoix != "all":
			if grille.temps != -1:				# si tps != -1 alors c'est que la grille a été résolue et tps vaut le temps mis pour résoudre
				if taille == 1:					# taille == 1 signifie qu'on résoud une seule grille et non tout un répertoire
					print("\nSolution :")
					print(grille)		
				print("Résolue en : {:2.2f}s\n".format(grille.temps))
				tps.append(grille.temps)		# on mémorise le temps dans une liste pour calculer la moyenne ensuite 
			else:
				print("Grille non résolue !")
		else:
			print('{} solution(s)'.format(len(tps)))
			afficher(tps[0])
	afficheResume(tps)					# calcule et affiche le temps moyen
	return toutes_les_grilles

# -- Main --------
# ----------------

def main():
	fic, rep, optTri, optChoix, optSingleton = settings(sys.argv[1:])
	# ceci est spécifique à Mac : lorsqu'on manipule les répertoires via l'interface graphique ce fichier .DS_Store apparaît
	# il faut bien sûr ne pas le traiter comme étant un fichier de sudoku
	if '.DS_Store' in fic:
		fic.remove('.DS_Store')
	all_grilles = solveOneOrMore(fic, rep, optTri, optChoix, optSingleton)
	for g in all_grilles:
		all_grilles[g].analyse()




if __name__ == "__main__":
	main()	
		