with open(f'sudoku17.txt', 'r') as fin:
	for id_fic, ligne in enumerate(fin):
		with open(f'big_{id_fic:05}', 'w') as fout:
			for i in range(0,81,9):
				fout.write(' '.join([c for c in ligne[i:i+9]]) + '\n')
