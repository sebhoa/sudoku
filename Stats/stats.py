
import sys


listes = {0.01:[], 0.1:[]}
bornes = list(listes.keys())
bornes.sort()
last = []

if len(sys.argv) < 2:
	filename = 'diaboliques'
else:
	filename = 'stats_fast'

with open(filename, 'r') as fin:
	for ligne in fin:
		try:
			name, tps = ligne.split()
		except:
			break
		tps = float(tps)
		for borne in bornes:
			if tps <= borne:
				listes[borne].append(tps)
				break
		else:
			last.append(tps)

for borne in bornes:
	print(f'moins de {borne:>4}s : {len(listes[borne])}')
print(f'plus de {bornes[-1]:>4}s : {len(last)}')

l_values = listes.values()
values = sum([sum(l) for l in l_values]) + sum(last)
nb = sum([len(l) for l in l_values]) + len(last)
print(f'Temps moyen pour les {nb} fichiers : {values/nb:.2f}s')