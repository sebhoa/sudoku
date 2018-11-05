import sys

type_s = sys.argv[1]
filename = f'stats_{type_s}_backtrack'
d_stats = {}
with open(filename) as f_in:
	for ligne in f_in:
		id_fic, tps, nb = ligne.split()
		tps = float(tps)
		if id_fic in d_stats:
			old_tps = d_stats[id_fic][0]
			d_stats[id_fic] = (min(tps, old_tps), d_stats[id_fic][1])
		else:
			d_stats[id_fic] = (tps, nb)

file_out = f'stats_{type_s}_backtrack_bis'
with open(file_out, 'w') as f_out:
	for id_fic in d_stats:
		f_out.write(f'{id_fic} {d_stats[id_fic][0]} {d_stats[id_fic][1]}\n')