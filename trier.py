import sys

type_grille = sys.argv[1]
filein = f'Stats/stats_{type_grille}_backtrack'
fileout = f'{type_grille}_backtrack'
with open(filein, 'r') as fin,\
	open(fileout, 'w') as fout:
	for ligne in fin:
		id_fic, _, _ = ligne.split()
		fout.write(f'big_{id_fic}\n')