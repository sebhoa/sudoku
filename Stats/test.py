from os import system
# with open('sans_backtracking', 'w') as fout:
# 	with open('stats_all', 'r') as f: 
# 		for l in f: 
# 			fic, tps, n = l.split() 
# 			n = int(n)
# 			if n <= 0:
# 				# print(f'{fic} {tps} {n}')
# 				fout.write(l)

total = 0
nb = 0
with open('sans_backtracking', 'r') as fin:
	for ligne in fin:
		fic, tps, _ = ligne.split()
		total += float(tps)
		nb += 1
print(f'Temps moyen : {total/nb:.3f}')
