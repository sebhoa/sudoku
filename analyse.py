from os import system

count = 0
with open('stats_fast', 'r') as fin:
	with open('diaboliques', 'a') as fout:
		for ligne in fin:
			id_fic, tps = ligne.split()
			tps = float(tps)
			if tps >= 1:
				count += 1
				# system(f'mv BigDossier/big_{id_fic} GrillesDiaboliques')
				fout.write(ligne)
print(f'{count} transferts')