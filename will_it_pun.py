#!/usr/bin/env python

import argparse
import sys

from graphviz import Digraph

from puns.phoneme_dictionary import PhonemeDictionary
from puns.pun_generator import PunGenerator

# Uses the format specified by http://www.speech.cs.cmu.edu/cgi-bin/cmudict
phoneme_file = "data/cmudict-0.7b"


def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-g", "--graph", help="If set, output a graph file (in DOT format) of possible puns to GRAPH")
	parser.add_argument("phrase", help="The phrase to generate puns for")
	return parser.parse_args()

def graph_results(puns, output_path):
	dot = Digraph()
	nodes = set()
	edges = set()

	for pun in puns:
		words = pun.split(" ")
		for i in range(len(words)):
			# TODO the index of the node id should be the index of the associated
			# phoneme, not the index of the word
			node_id = words[i] + str(i)
			label = words[i]

			if node_id not in nodes:
				nodes.add(node_id)
				dot.node(node_id, label)

			if i != 0:
				previous_node_id = words[i-1] + str(i-1)
				edge_id = previous_node_id + " " + node_id
				if edge_id not in edges:
					edges.add(edge_id)
					dot.edge(previous_node_id, node_id)

	dot.save(output_path)


if __name__ == "__main__":

	args = parse_args()
	
	phoneme_dict = PhonemeDictionary(phoneme_file)
	pun_generator = PunGenerator(phoneme_dict)

	puns = pun_generator.generate_puns(args.phrase.upper())

	# TODO consider leveraging NLTK to determine pun probability
	for pun in sorted(puns):
		print(pun)

	if args.graph is not None:
		graph_results(puns, args.graph)
