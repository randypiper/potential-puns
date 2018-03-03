"""
Includes functions for computing phonetic similarity.
Methods are based on those described by Hixon, Schneider, and Epstein in
https://homes.cs.washington.edu/~bhixon/papers/phonemic_similarity_metrics_Interspeech_2011.pdf
"""
from math import log
from itertools import combinations, product
from collections import Counter, defaultdict

class SimilarityMatrix(object):
    """
    For calculating phonetic similarity
    """

    def __init__(self, phoneme_dictionary):
        self._pdict = phoneme_dictionary
        self._matrix = self._calculate_matrix()

    def _calculate_matrix(self):
        alt_pronunciations = (phones for phones in
                              self._pdict.words_to_phonemes.values()
                              if len(phones) > 1)

        pairs = [pair for wordset in alt_pronunciations
                 for pair in combinations(wordset, 2)]

        frequency_counter = defaultdict(int)
        swap_counter = defaultdict(int)
        total = 0.0

        for pro1, pro2 in pairs:
            seq1, seq2 = get_alignments(pro1.split(), pro2.split())
            for phoneme in seq1 + seq2:
                if phoneme is not None:
                    frequency_counter[phoneme] += 1
                    total += 1
            for swap in self._get_swaps(seq1, seq2):
                swap_counter[swap] += 1

        similarities = defaultdict(dict)
        for phone1, phone2 in product(self._pdict.phonemes, self._pdict.phonemes):
            key = tuple(sorted((phone1, phone2)))
            prob_phone1 = (frequency_counter[phone1]) / total
            prob_phone2 = (frequency_counter[phone2]) / total

            # Just some mathematically incorrect smoothing, nothing
            # to see here
            swap_prob = (swap_counter[key] + 1) / total

            # This is symmetrical so it's kind of a waste
            # of space, but it's nice to be able to
            # get all of the similarities for a given phoneme
            # easily
            similarities[phone1][phone2] = log(swap_prob/ (prob_phone1 * prob_phone2))
        return similarities

    @staticmethod
    def _get_swaps(seq1, seq2):
        """Gets swapped elements for aligned sequences seq1 and seq2"""
        swaps = []
        for val1, val2 in zip(seq1, seq2):
            if val1 is not None and val2 is not None:
                swaps.append(tuple(sorted((val1, val2))))
        return swaps

    @property
    def matrix(self):
        """Similarity matrix"""
        return self._matrix

    def similarity(self, phone1, phone2):
        """
        Similarity score between phonemes, phone1 and phone2
        """
        return self._matrix[phone1][phone2]

    def phoneme_seq_similarity(self, seq1, seq2):
        """
        Similarity between two phoneme sequences
        """
        return get_alignment_score(seq1, seq2, similarity_func=self.similarity)

    def phrase_phonetic_similarity(self, phrase1, phrase2):
        """
        Returns phonetic similarity of two English phrases
        """
        # Words to phonemes
        phrase1_phonemes = self._phrase_to_phonemes(phrase1)
        phrase2_phonemes = self._phrase_to_phonemes(phrase2)
        return max(
            self.phoneme_seq_similarity(seq1, seq2)
            for seq1 in phrase1_phonemes for seq2 in phrase2_phonemes
        )

    def _phrase_to_phonemes(self, phrase):
        """
        Returns all possible phoneme sequences for given phrase
        """
        phones = [self._pdict.words_to_phonemes[w.upper()]
                  for w in phrase.split()]
        return [" ".join(phone_seq).split() for phone_seq in product(*phones)]


def levenshtein(left, right):
    """1 if values are equal else -1"""
    return 1 if left == right else -1


def get_alignments(seq1, seq2, gap_penalty=-1, similarity_func=levenshtein):
    """
    Returns a pair of sequences after seq1 and seq2 have
    been aligned, using the the Needleman Wunsch algorithm. `None` is
    used as the empty placeholder resulting from "indelete" operations.
    """
    return _get_best_alignment(
        seq1, seq2,
        _get_alignment_matrix(seq1, seq2, gap_penalty, similarity_func),
        gap_penalty,
        similarity_func
    )

def get_alignment_score(seq1, seq2, gap_penalty=-1, similarity_func=levenshtein):
    """
    Gets the similarity score, according to the given gap_penalty and
    similarity_func, for the given sequences after optimal alignment
    """
    return _get_alignment_matrix(seq1, seq2, gap_penalty, similarity_func)[-1][-1]

def _get_alignment_matrix(seq1, seq2, gap_penalty=-1, similarity_func=levenshtein):
    """
    Calculates matrix of aligment scores based
    on Needleman Wunsch Algorithm.
    """
    align_mat = [[0 for _ in range(len(seq2) + 1)] for _ in range(len(seq1) + 1)]
    for i in range(len(seq1) + 1):
        align_mat[i][0] = i * gap_penalty
    for j in range(len(seq2) + 1):
        align_mat[0][j] = j * gap_penalty
    for i, char1 in enumerate(seq1, 1):
        for j, char2 in enumerate(seq2, 1):
            match = align_mat[i-1][j-1] + similarity_func(char1, char2)
            delete = align_mat[i-1][j] + gap_penalty
            insert = align_mat[i][j-1] + gap_penalty
            align_mat[i][j] = max(match, delete, insert)
    return align_mat

def _get_best_alignment(seq1, seq2, mat, gap_penalty, similarity_func):
    """
    Returns pair of sequences after modifying for best alignment.
    Nones represent inserted gaps.
    """
    seq1_aligned = []
    seq2_aligned = []
    i = len(seq1)
    j = len(seq2)
    while i > 0 or j > 0:
        is_match = mat[i][j] == mat[i - 1][j - 1] + similarity_func(seq1[i - 1], seq2[j -1])
        if i > 0 and j > 0 and is_match:
            seq1_aligned.append(seq1[i-1])
            seq2_aligned.append(seq2[j-1])
            j -= 1
            i -= 1
        elif i > 0 and mat[i][j] == mat[i - 1][j] - 1: # Gap penalty
            seq1_aligned.append(seq1[i-1])
            seq2_aligned.append(None)
            i -= 1
        else:
            seq1_aligned.append(None)
            seq2_aligned.append(seq2[j-1])
            j -= 1
    return [list(reversed(x)) for x in (seq1_aligned, seq2_aligned)]
