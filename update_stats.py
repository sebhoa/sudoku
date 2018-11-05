

# Mise à jour des journaux de stats
#
s = set()
with open('stats_sans_backtrack', 'r') as f_in,\
	open('Stats/stats_sans_backtrack', 'a') as fout,\
	open('Filtres/sans_backtrack', 'a') as fout2:
	for ligne in f_in:
		id_fic, tps, nb = ligne.split()
		s.add(f'{id_fic}')
		fout.write(ligne)
		fout2.write(f'{id_fic}\n')



with open('Filtres/avec_backtrack', 'r') as f_in,\
	open('avec_backtrack', 'w') as fout:
		for id_fic in f_in:
			if id_fic[:-1] not in s:
				fout.write(id_fic)

with open('Stats/stats_avec_backtrack', 'r') as f_in,\
	open('stats_avec_backtrack', 'w') as fout:
		for ligne in f_in:
			id_fic, _, _ = ligne.split()
			if id_fic not in s:
				fout.write(ligne)



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


