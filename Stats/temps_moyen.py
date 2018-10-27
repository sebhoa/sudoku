
import sys

type_grille = sys.argv[1]
filename = f'stats_{type_grille}_backtrack'
total = 0
nb = 0
with open(filename, 'r') as f_in:
	for ligne in f_in:
		fic_id, tps, *others = ligne.split()
		total += float(tps)
		nb += 1
print(f'{nb} grilles, temps moyen : {total/nb:.3f}s')