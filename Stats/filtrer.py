"""
Permet de détecter des anomalies de temps
sur les grilles... et de relancer la résolution

Appel : filter.py temps_de_reference sans|avec
"""


import sys


tps_ref = float(sys.argv[1])
type_grille = sys.argv[2]
filename = f'stats_{type_grille}_backtrack'
nb = 0
with open(filename, 'r') as fin:
	for ligne in fin:
		id_fic, tps, _ = ligne.split()
		if float(tps) >= tps_ref:
			print(id_fic, tps)
			nb += 1

print(f'{nb} grilles à plus de {tps_ref}s')