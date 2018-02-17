#!/usr/bin/env python

import sys

from puns.phoneme_dictionary import PhonemeDictionary
from puns.pun_generator import PunGenerator

# Uses the format specified by http://www.speech.cs.cmu.edu/cgi-bin/cmudict
phoneme_file = "data/cmudict-0.7b"


if __name__ == "__main__":

	phoneme_dict = PhonemeDictionary(phoneme_file)
	pun_generator = PunGenerator(phoneme_dict)

	pun_target = sys.argv[1].upper()
	puns = pun_generator.generate_puns(pun_target)

	# TODO consider leveraging NLTK to determine pun probability
	for pun in sorted(puns):
		print(pun)
