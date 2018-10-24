from os import system

nb = 0
with open('stats_all', 'r') as fin:
	for ligne in fin:
		id_fic, tps = ligne.split()
		if float(tps) < 0.5:
			system(f'mv GrillesDiaboliques/big_{id_fic} BigDossier')
			nb += 1
print(f'{nb} transferts')
