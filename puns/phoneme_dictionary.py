import collections
import re

class PhonemeDictionary:

    def __init__(self, phoneme_dict_file):
        self.phonemes_to_words = collections.defaultdict(set)
        self.words_to_phonemes = collections.defaultdict(set)
        self._phonemes = set()
        self._parse_phoneme_dict_file(phoneme_dict_file)

    @property
    def phonemes(self):
        return self._phonemes

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
                phonemes = self._normalize_phoneme(match.group("phoneme"))
                self._add(phonemes, word)


    def _add(self, phonemes, word):
        self.phonemes_to_words[phonemes].add(word)
        self.words_to_phonemes[word].add(phonemes)
        self._phonemes = self._phonemes.union(phonemes.split())



    def _normalize_word(self, word):
        if word.endswith(")"):
            word = word[:-3]
        return word.replace("'", "").replace("-", "").replace(".","")


    def _normalize_phoneme(self, phoneme):
        return re.sub("\d", "", phoneme)
