import collections
import re

class PhonemeDictionary:

	def __init__(self, phoneme_dict_file):
		self.phonemes_to_words = collections.defaultdict(set)
		self.words_to_phonemes = collections.defaultdict(set)
		self._parse_phoneme_dict_file(phoneme_dict_file)

	def get_words(self, phoneme):
		return self.phonemes_to_words.get(phoneme)


	def get_phonemes(self, word):
		return self.words_to_phonemes.get(word)


	def _parse_phoneme_dict_file(self, phoneme_dict_file):
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
			self.phonemes_to_words[phoneme].add(word)
			self.words_to_phonemes[word].add(phoneme)


	def _normalize_word(self, word):
		if word.endswith(")"):
			word = word[:-3]
		return word.replace("'", "").replace("-", "").replace(".","")


	def _normalize_phoneme(self, phoneme):
		return re.sub("\d", "", phoneme)
