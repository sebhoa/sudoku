

# Mise à jour des journaux de stats
#
# s = set()
# with open('stats_avec_backtrack', 'r') as f_in,\
# 	open('Stats/stats_sans_backtrack', 'a') as fout,\
# 	open('stats_avec_backtrack_bis', 'w') as fout2:
# 	for ligne in f_in:
# 		id_fic, tps, nb = ligne.split()
# 		if nb == '0':
# 			fout.write(ligne)
# 			s.add(f'{id_fic}')
# 		else:
# 			fout2.write(ligne)

with open('Stats/stats_avec_backtrack', 'r') as fin,\
	open('Filtres/avec_backtrack', 'w') as fout:
	for ligne in fin:
		id_fic, _, _ = ligne.split()
		fout.write(f'{id_fic}\n')

# Mise à jour des fichiers de noms de grilles
# avec et sans backtrack
#
# with open('Filtres/avec_backtrack', 'r') as f_in,\
# 	open('Filtres/sans_backtrack', 'a') as fout,\
# 	open('avec_backtrack_bis', 'w') as fout2:
# 	for ligne in f_in:
# 		if ligne[:-1] in s:
# 			fout.write(ligne)
# 		else:
# 			fout2.write(ligne)


