import itertools
import re
import sys

# Uses the format specified by http://www.speech.cs.cmu.edu/cgi-bin/cmudict
phoneme_file = "data/cmudict-0.7b"

class PhonemeDictionary:

	def __init__(self, phoneme_dict_file):
		self.phonemes_to_words = {}
		self.words_to_phonemes = {}
		self._parse_phonemem_dict_file(phoneme_dict_file)

	def get_words(self, phoneme):
		return self.phonemes_to_words.get(phoneme)


	def get_phonemes(self, word):
		return self.words_to_phonemes.get(word)


	def _parse_phonemem_dict_file(self, phoneme_dict_file):
		pattern = re.compile(r"(?P<word>.*?)\s\s(?P<phoneme>.*?)\n")

		with open(phoneme_dict_file) as f:
			for line in f:
				if line.startswith(";;;"):
					continue

				match = pattern.match(line)
				word = self._normalize_word(match.group("word"))
				phoneme = self._normalize_phoneme(match.group("phoneme"))
				self._add(phoneme, word)


	def _add(self, phoneme, word):
		if phoneme in self.phonemes_to_words:
			self.phonemes_to_words[phoneme].add(word)
		else:
			self.phonemes_to_words[phoneme] = { word }

		if word in self.words_to_phonemes:
			self.words_to_phonemes[word].add(phoneme)
		else:
			self.words_to_phonemes[word] = { phoneme }


	def _normalize_word(self, word):
		if word.endswith(")"):
			word = word[:-3]
		return word.replace("'", "").replace("-", "").replace(".","")


	def _normalize_phoneme(self, phoneme):
		return phoneme.strip()


class PunGenerator:

	def __init__(self, phoneme_dict):
		self.phoneme_dict = phoneme_dict
		self.computed_puns = {}


	def generate_puns(self, pun_target):
		target_phonemes = self._convert_phrase_to_possible_phonemes(pun_target)
		for target_phoneme in target_phonemes:
			self._iterate_puns(target_phoneme)

		return self._get_all_puns(target_phonemes)


	def _iterate_puns(self, target_phoneme):
		if target_phoneme in self.computed_puns:
			return self.computed_puns[target_phoneme]

		phonemes = target_phoneme.split(" ")
		if len(phonemes) == 0:
			return

		if self.phoneme_dict.get_words(target_phoneme) is not None:
			self._add_pun(target_phoneme, self.phoneme_dict.get_words(target_phoneme))
		else:
			self._add_pun(target_phoneme, set())

		for i in range(1, len(phonemes)):
			left = " ".join(phonemes[:i])
			right = " ".join(phonemes[i:])
			self._iterate_puns(left)
			self._iterate_puns(right)

			left_puns = self.computed_puns[left]
			right_puns = self.computed_puns[right]
			self._add_pun(target_phoneme, { " ".join(tup) for tup in itertools.product(left_puns, right_puns) })


	def _add_pun(self, phoneme, words):
		if phoneme in self.computed_puns:
			self.computed_puns[phoneme].update(words)
		else:
			self.computed_puns[phoneme] = words


	def _convert_phrase_to_possible_phonemes(self, phrase):
		phrase_phonemes = [self.phoneme_dict.get_phonemes(word) for word in phrase.split(" ")]
		return [" ".join(tup) for tup in itertools.product(*phrase_phonemes)]


	def _get_all_puns(self, target_phonemes):
		return set().union(*[ self.computed_puns[phoneme] for phoneme in target_phonemes ])


if __name__ == "__main__":

	phoneme_dict = PhonemeDictionary(phoneme_file)
	pun_generator = PunGenerator(phoneme_dict)

	pun_target = sys.argv[1].upper()
	puns = pun_generator.generate_puns(pun_target)

	# TODO consider leveraging NLTK to determine pun probability
	for pun in sorted(puns):
		print(pun)
