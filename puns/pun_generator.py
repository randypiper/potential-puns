import itertools

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
