with open('95') as fin,\
	open('95bis', 'w') as fout:
	 lignes = fin.readlines()
	 nbcar = len(f'{len(lignes)}')
	 for index, ligne in enumerate(lignes):
	 	fout.write(f'{index:0{nbcar}} {ligne[:-1]}\n')