import math
import itertools
import random

NEGATIVE_PENALTY = 10

def compute_color_map(part_sizes):
	color_parts = map(lambda (i, s): [i] * s, enumerate(part_sizes))
	color_map = reduce(lambda x, y: x + y, color_parts)
	return color_map

def generate_random_graph(color_map, probi, proba, nprobi, nproba):
	n = len(color_map)
	adj = [[-1] * n for i in xrange(n)]

	def generate_edge(i, j):
		v = random.random()
		internal = color_map[i] == color_map[j]
		if color_map[i] == color_map[j]:
			nprob = nprobi
			prob = probi
		else:
			nprob = nproba
			prob = proba

		if v <= nprob:
			return -1
		count = 0
		while v <= prob and count < NEGATIVE_PENALTY - 1:
			count += 1
			v = random.random()
		return count

	for i in xrange(n):
		for j in xrange(i + 1, n):
			adj[i][j] = generate_edge(i, j)
			adj[j][i] = adj[i][j]

	return adj

def count_edges(adj):
	n = len(adj)

	count = 0
	edge_sum = 0
	for i in xrange(n):
		for j in xrange(i + 1, n):
			if adj[i][j] >= 0:
				count += 1
				edge_sum += adj[i][j]
	return count, edge_sum

def generate_vertex_map(n, shuffle = True):
	vtx_map = range(n)
	if shuffle:
		random.shuffle(vtx_map)
	return vtx_map

def print_graph(output_filename, names, part_sizes, vtx_map, adj):
	n = len(vtx_map)
	random.shuffle(names)

	total = n * (n - 1) / 2
	edges, edge_sum = count_edges(adj)
	with open(output_filename + ".txt", "w") as f:
		f.write("%d %d 0 %d\n" % (n, total - edges, edge_sum))
		for part in part_sizes:
			f.write("%d " % part)
		f.write("\n")
		f.write("# Names\n")
		for i in xrange(n):
			f.write("%s\n" % names[i])

		f.write("# Forbidden pairs\n")
		for i in xrange(n):
			for j in xrange(i + 1, n):
				val = adj[vtx_map[i]][vtx_map[j]]
				if val < 0:
					f.write("%s, %s\n" % (names[i], names[j]))
		f.write("# Must be together\n")
		f.write("# Already paired\n")
		for i in xrange(n):
			for j in xrange(i + 1, n):
				val = adj[vtx_map[i]][vtx_map[j]]
				while val > 0:
					f.write("%s, %s\n" % (names[i], names[j]))
					val -= 1

def print_metis_graph(output_filename, part_sizes, color_map, vtx_map, adj):
	n = len(vtx_map)

	edges = count_edges(adj)[0]
	with open(output_filename + ".graph", "w") as f:
		f.write("%d %d 001\n" % (n, edges))
		for i in xrange(n):
			for j in xrange(n):
				val = adj[vtx_map[i]][vtx_map[j]]
				if val >= 0:
					val = NEGATIVE_PENALTY - val
					f.write("%d %d " % (j + 1, val))
			f.write("\n")

	with open(output_filename + ".expected", "w") as f:
		for i in xrange(n):
			f.write("%d\n" % color_map[vtx_map[i]])

	with open(output_filename + ".targetweights", "w") as f:
		for i, p in enumerate(part_sizes):
			f.write("%d = %f\n" % (i, float(p) / n))

def load_names(filename):
	names = []
	with open(filename, "r") as f:
		for line in f:
			name = line.strip()
			names.append(name)
	return names

if __name__ == "__main__":
	names = load_names("names.txt")

	part_sizes = [3, 3, 3]
	probi = 0.1
	nprobi = 0.05
	proba = 0.3
	nproba = 0.1

	color_map = compute_color_map(part_sizes)
	vtx_map = generate_vertex_map(len(color_map), True)
	adj = generate_random_graph(color_map, probi, proba, nprobi, nproba)
	print_metis_graph("test2", part_sizes, color_map, vtx_map, adj)
	print_graph("test2", names, part_sizes, vtx_map, adj)
