

# Mise à jour des journaux de stats
#
s = set()
with open('stats_avec_backtrack', 'r') as f_in,\
	open('Stats/stats_sans_backtrack', 'a') as fout,\
	open('stats_avec_backtrack_bis', 'w') as fout2:
	for ligne in f_in:
		id_fic, tps, nb = ligne.split()
		if nb == '0':
			fout.write(ligne)
			s.add(f'big_{id_fic}')
		else:
			fout2.write(ligne)

# Mise à jour des fichiers de noms de grilles
# avec et sans backtrack
#
with open('avec_backtrack', 'r') as f_in,\
	open('sans_backtrack', 'a') as fout,\
	open('avec_backtrack_bis', 'w') as fout2:
	for ligne in f_in:
		if ligne[:-1] in s:
			fout.write(ligne)
		else:
			fout2.write(ligne)


