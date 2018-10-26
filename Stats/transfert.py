from os import system

nb = 0
with open('stats_all', 'r') as fin:
	for ligne in fin:
		id_fic, tps = ligne.split()
		if float(tps) >= 0.5:
			system(f'mv BigDossier/big_{id_fic} GrillesDiaboliques')
			nb += 1
print(f'{nb} transferts')
