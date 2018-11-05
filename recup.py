

d_grilles = {}
with open('Grilles/sudoku17') as f_in:
    for ligne in f_in:
        id_fic, data = ligne.split()
        d_grilles[id_fic] = data

keys = []
type_grille = 'sans'
with open(f'Filtres/{type_grille}_backtrack') as f_in:
	for id_fic in f_in:
		keys.append(id_fic[:-1])

with open('outfab2.txt') as f_in2,\
	open('Filtres/fab_fail', 'w') as fout,\
	open('datas_fab_fail', 'w') as fout2:
	for id_ligne, ligne in enumerate(f_in2):
		if 'Echec' in ligne:
			id_fic = f'{id_ligne:05}'
			fout.write(f'{keys[id_ligne]}\n')
			fout2.write(f'{d_grilles[id_fic]}\n')

