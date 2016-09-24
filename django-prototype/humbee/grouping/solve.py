#!/usr/bin/env python
import os
import sys
import StringIO
import subprocess
import shlex

NEGATIVE_PENALTY = 10

def read_line(f):
	while True:
		line = f.readline()
		if not line.startswith("#"):
			return line

def split_line(line, valid_names):
	tokens = line.split(",")
	tokens = map(lambda s: s.strip(), tokens)
	for name in tokens:
		if not name in valid_names:
			raise Exception("Invalid name: " + name)
	return tokens

def process_text(text):
	names = []
	forbidden = []
	same = []
	other_pairs = []
	f = StringIO.StringIO(text)

	line = read_line(f)
	line = line.strip()
	tokens = line.split()
	n = int(tokens[0])
	num_forbidden = int(tokens[1])
	num_same = int(tokens[2])
	num_other_pairs = int(tokens[3])

	line = read_line(f)
	line = line.strip()
	tokens = line.split()
	part_sizes = map(lambda x: int(x), tokens)

	for i in xrange(n):
		line = read_line(f)
		name = line.strip()
		names.append(name)
	valid_names = set(names)

	for i in xrange(num_forbidden):
		line = read_line(f)
		tokens = split_line(line, valid_names)
		forbidden.append(tokens)

	for i in xrange(num_same):
		line = read_line(f)
		tokens = split_line(line, valid_names)
		same.append(tokens)

	for i in xrange(num_other_pairs):
		line = read_line(f)
		tokens = split_line(line, valid_names)
		other_pairs.append(tokens)

	f.close()
	return (names, part_sizes, forbidden, same, other_pairs)

def construct_name_map(info):
	names = info[0]
	same = info[3]
	name_map = dict()

	for i, name in enumerate(names):
		name_map[name] = i

	for tokens in same:
		min_idx = len(names)
		for name in tokens:
			if name_map[name] < min_idx:
				min_idx = name_map[name]

		for name in tokens:
			name_map[name] = min_idx

	used = set()
	for name in names:
		used.add(name_map[name])
	used = sorted(list(used))

	tmp_map = dict()
	for i, v in enumerate(used):
		tmp_map[v] = i

	nn = len(used)
	rev_name_map = [[] for i in xrange(nn)]

	for name in names:
		val = tmp_map[name_map[name]]
		rev_name_map[val].append(name)
		name_map[name] = val

	return name_map, rev_name_map

def generate_graph(info, name_map, rev_name_map):
	names = info[0]
	forbidden = info[2]
	other_pairs = info[4]

	nn = len(rev_name_map)
	adj = [[0] * nn for i in xrange(nn)]

	for tokens in other_pairs:
		vals = [name_map[x] for x in tokens]
		for i in xrange(len(vals)):
			for j in xrange(i + 1, len(vals)):
				if vals[i] == vals[j]:
					continue
				adj[vals[i]][vals[j]] += 1
				adj[vals[j]][vals[i]] += 1

	for tokens in forbidden:
		vals = [name_map[x] for x in tokens]
		for i in xrange(len(vals)):
			for j in xrange(i + 1, len(vals)):
				if vals[i] == vals[j]:
					raise Exception("Invalid graph")
				adj[vals[i]][vals[j]] = -1
				adj[vals[j]][vals[i]] = -1
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

def print_metis_graph(output_filename, part_sizes, rev_name_map, adj):
	n = len(adj)
	nn = 0
	edges = count_edges(adj)[0]
	with open(output_filename + ".graph", "w") as f:
		f.write("%d %d 101\n" % (n, edges))
		for i in xrange(n):
			nn += len(rev_name_map[i])
			f.write("%d " % len(rev_name_map[i]))
			for j in xrange(n):
				if i == j:
					continue

				val = adj[i][j]
				if val >= 0:
					val = NEGATIVE_PENALTY - val
					f.write("%d %d " % (j + 1, val))
			f.write("\n")

	with open(output_filename + ".targetweights", "w") as f:
		for i, p in enumerate(part_sizes):
			f.write("%d = %f\n" % (i, float(p) / nn))

def solve_metis(filename, num_parts):
	cmdline = "gpmetis -tpwgts=%s.targetweights %s.graph %d" % \
	          (filename, filename, num_parts)
	proc = subprocess.Popen(shlex.split(cmdline),
	                        stdout = subprocess.PIPE,
	                        shell = False)
	(out, err) = proc.communicate()
	return out + str(shlex.split(cmdline))

def read_solution(filename, num_parts):
	filename = "%s.graph.part.%d" % (filename, num_parts)
	partition = [[] for i in xrange(num_parts)]
	with open(filename, "r") as f:
		for i, line in enumerate(f):
			val = int(line.strip())
			partition[val].append(i)

	return partition

def reconstruct_groups(partition, rev_name_map):
	groups = []
	for parts in partition:
		group = []
		for idx in parts:
			group.extend(rev_name_map[idx])
		groups.append(group)
	return groups

def solve(text, tmp_filename):
	# TODO change this tmp_filename thing
	info = process_text(text)
	part_sizes = info[1]
	name_map, rev_name_map = construct_name_map(info)
	adj = generate_graph(info, name_map, rev_name_map)
	print_metis_graph(tmp_filename, part_sizes, rev_name_map, adj)
	num_parts = len(part_sizes)
	out = solve_metis(tmp_filename, num_parts)
	partition = read_solution(tmp_filename, num_parts)
	groups = reconstruct_groups(partition, rev_name_map)
	return groups, out

