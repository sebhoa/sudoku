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


# -- Settings ----
# ----------------
def recupAllFiles(rep):
	return os.listdir(rep)

def settings(argv):
	try:
		opts, args = getopt.getopt(argv,Options)
	except getopt.error:
		msg = sys.exc_info()[1]
		print(f'Error: {msg}')
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
		print('-------------------------')
		print(f'Temps moyen : {sum(tps)/len(tps):.3f}s')

# Traiter 1 ou plusieurs grilles ?
def solveOneOrMore(l, rep, optTri, optChoix, optSingleton):
	# ferr = open('big.log','w')
	# fstats = open('stats_all','a')
	tps = []
	toutes_les_grilles = {}
	taille = len(l)
	for id_fic, fic in enumerate(l):
		# print(f'{id_fic:05}', end='\b'*5, flush=True)
		grille = class_sudoku.Sudoku(fic,os.path.join(Home,rep,fic))
		toutes_les_grilles[fic] = grille
		# print(f'\nGrille : {fic}')
		if taille == 1:
			print()
			print(grille)
		grille.solve(optTri, optSingleton)
		if optChoix != 'all':
			if grille.solution:				# si tps != -1 alors c'est que la grille a été résolue et tps vaut le temps mis pour résoudre
				if taille == 1:					# taille == 1 signifie qu'on résoud une seule grille et non tout un répertoire
					print('\nSolution :')
					print(grille)		
				print(f'Résolue en : {grille.temps:.3f}s')
				# fstats.write(f'{fic[4:]} {grille.temps:2.2f}\n')
				tps.append(grille.temps)		# on mémorise le temps dans une liste pour calculer la moyenne ensuite 
			else:
				print('Non résolue !')
				# ferr.write(f'{grille.name}\n')
		else:
			print(f'{len(tps)} solution(s)')
			print(tps)
	afficheResume(tps)					# calcule et affiche le temps moyen
	# ferr.close()
	# fstats.close()
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
		