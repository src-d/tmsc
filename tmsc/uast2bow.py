from collections import defaultdict
import marshal
import math
import types

from sourced.ml.models import BOW, DocumentFrequencies
from sourced.ml.algorithms.uast_ids_to_bag import UastIds2Bag

class Uasts2BOW:
    def __init__(self, vocabulary: dict, docfreq: DocumentFrequencies,
                 getter: callable):
        self._docfreq = docfreq
        self._uast2bag = UastIds2Bag(vocabulary) #TODO replace with sourced.ml.
        self._reverse_vocabulary = [None] * len(vocabulary)
        for key, val in vocabulary.items():
            self._reverse_vocabulary[val] = key
        self._getter = getter

    @property
    def vocabulary(self):
        return self._uast2bag.token2index #.vocabulary

    @property
    def docfreq(self):
        return self._docfreq

    def __call__(self, file_uast_generator):
        freqs = defaultdict(int)
        for file_uast in file_uast_generator:
            bag = self._uast2bag(self._getter(file_uast)) #.uast_to_bag
            for key, freq in bag.items():
                freqs[key] += freq
        missing = []
        for key, val in freqs.items():
            try:
                freqs[key] = math.log(1 + val) * math.log(
                    self._docfreq.docs / self._docfreq[self._reverse_vocabulary[key]])
            except KeyError:
                missing.append(key)
        for key in missing:
            del freqs[key]
        return dict(freqs)

    def __getstate__(self):
        state = self.__dict__.copy()
        if isinstance(self._getter, types.FunctionType) \
                and self._getter.__name__ == (lambda: None).__name__:
            assert self._getter.__closure__ is None
            state["_getter"] = marshal.dumps(self._getter.__code__)
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        if isinstance(self._getter, bytes):
            self._getter = types.FunctionType(marshal.loads(self._getter), globals())
