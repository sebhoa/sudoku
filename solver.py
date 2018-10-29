#!/usr/bin/env python3

""" 
SOLVEUR DE SUDOKUS 

Principe : Les grilles de sudoku sont représentées par un fichier 
stockant pour chaque grille un identifiant et des données sur une 
ligne (une chaine de 81 caractères), identifiant et donnée sont 
séparés par un espace

Le solveur prend un tel fichier ainsi qu'un fichier contenant des 
identifiants et va résoudre toutes les grilles correspondantes puis
afficher un résumé avec notamment le nombre de grilles résolues sans
et avec backtrack ainsi que le temps moyen.

Le but ici est de faire tourner ce solveur sur un fichier contenant 
49151 grilles de 17 cases initiales (sudoku17) et d'essayer de toutes 
les résoudres *sans* backtrack.

Auteur : Sébastien Hoarau
Date   : 2018.10.29
"""

REP_GRID = 'Grilles'
REP_FILTER = 'Filtres'
DEFAULT_SUDOKUS = 'sudoku17'
DEFAULT_FILTER = 'avec_backtrack'
SUDOKU17_SIZE = 49151 

import pathlib
import argparse
import random
import sudoku

class Solver:

	def __init__(self):
		self.main_filename = '' 		# nom du fichier principal contenant toutes les grilles
		self.snd_filename = ''			# le fichier secondaire avec les identifiants des grilles à résoudre
		self.datas = {}					# dictionnaire stockant les données de toutes les grilles
		self.sudokus_to_solve = set()	# l'ensemble des identifiants à résoudre
		self.sudokus = []				# la liste des sudokus créés et résolus
		self.verbose = True				# pour afficher les détails
	


	def settings(self):
		"""
		Pour récupérer les fichiers nécessaires, régler le solveur
		"""
		parser = argparse.ArgumentParser()
		parser.add_argument('id_file', nargs='?')
		parser.add_argument('-a', '--all', help='The file name of all sudokus.')
		parser.add_argument('-f', '--filter', help='The file name of sudokus id we want to solve.')
		parser.add_argument('-v', '--verbose', help='Print details for each sudoku.',
								action='store_true')
		args = parser.parse_args()

		# le fichier contenant toutes les grilles
		#
		if args.all:
			main_filename = pathlib.Path.cwd() / REP_GRID / args.all
		else:
			main_filename = pathlib.Path.cwd() / REP_GRID / DEFAULT_SUDOKUS

		# si on a 1 seul  identifiant de fichier c'est lui qu'on va résoudre
		if args.id_file:
			filtername = pathlib.Path.cwd() / REP_FILTER / 'default_filter'
			with open(filtername, 'w') as output:
				output.write(f'{args.id_file}\n')
		# sinon on regarde dans le fichier filtre
		elif args.filter:
			filtername = pathlib.Path.cwd() / REP_FILTER / args.filter
		# sinon pas de filtre et on prendra tous les fichiers
		else:
			filtername = ''

		with open(main_filename, 'r') as all_sudokus:
			for one_sudoku in all_sudokus:
				id_sudoku, data_sudoku = one_sudoku.split()
				self.datas[id_sudoku] = data_sudoku

		if filtername:
			with open(filtername, 'r') as some_sudokus:
				for id_sudoku in some_sudokus:
					self.sudokus_to_solve.add(id_sudoku[:-1])
		else:
			self.sudokus_to_solve = set(self.datas.keys())

		self.verbose = args.verbose or len(self.sudokus_to_solve) <= 5



	def start(self):
		for index, id_sudoku in enumerate(self.sudokus_to_solve):
			if not self.verbose:
				print(f'{index:05} : {id_sudoku}', end='\b'*13, flush=True)
			current_sudoku = sudoku.Sudoku(id_sudoku, self.datas[id_sudoku])
			if self.verbose:
				print(current_sudoku)
			current_sudoku.solve()
			if self.verbose:
				current_sudoku.analyse()
			self.sudokus.append(current_sudoku)


	def end(self):
		"""
		Terminer le solveur c'est afficher un résumé des grilles résolues
		résumé du nombre de grilles résolues avec backtrack et sans.
		Ecriture des stats dans deux fichiers :
		stats_avec_backtrack
		stats_sans_backtrack
		"""
		counts = [0, 0]
		tps = [0, 0]
		with open('stats_avec_backtrack', 'w') as output_avec,\
			open('stats_sans_backtrack', 'w') as output_sans:
			outputs = [output_sans, output_avec]
			for current_sudoku in self.sudokus:
				nb_backtrack = current_sudoku.profil['backtracking']
				crt_tps = current_sudoku.temps
				name = current_sudoku.name
				avec_backtrack = nb_backtrack > 0 
				counts[avec_backtrack] += 1
				tps[avec_backtrack] += crt_tps
				outputs[avec_backtrack].write(f'{name} {crt_tps} {nb_backtrack}\n')
		for i in range(2):
			try:
				tps[i] = tps[i] / counts[i]
			except:
				pass
		s = f'Résumé des {len(self.sudokus)} grilles :\n'\
			f'\tAvec backtrack : {counts[1]} grilles, temps moyen {tps[1]:.3f}s\n'\
			f'\tSans backtrack : {counts[0]} grilles, temps moyen {tps[0]:.3f}s\n'
		print(s)




# -- MAIN -- 

my_solver = Solver()
my_solver.settings()
my_solver.start()
my_solver.end()



