import logging
import re

from ast2vec import Repo2Base
#from ast2vec.model2.uast2bow import Uasts2BOW #?replace \w sourced.ml

from sourced.ml.models import BOW, Topics, DocumentFrequencies

import numpy
from scipy.sparse import csr_matrix

from tmsc.environment import initialize
from tmsc.uast2bow import Uasts2BOW

class Repo2BOW(Repo2Base):
    """
    Implements the step repository -> :class:`ast2vec.nbow.NBOW`.
    """
    MODEL_CLASS = BOW

    def __init__(self, vocabulary, docfreq, **kwargs):
        super().__init__(**kwargs)
        self.vocabulary = vocabulary
        self._uasts2bow = Uasts2BOW(vocabulary, docfreq, lambda x: x.response.uast)

    def convert_uasts(self, file_uast_generator):
        return self._uasts2bow(file_uast_generator)


class TopicDetector:
    GITHUB_URL_RE = re.compile(
        r"(https://|ssh://git@|git://)(github.com/[^/]+/[^/]+)(|.git|/)")

    def __init__(self, topics=None, docfreq=None, bow=None, verbosity=logging.DEBUG,
                 prune_df_threshold=1, repo2bow_kwargs=None):

        self._log = logging.getLogger("topic_detector")
        self._log.setLevel(verbosity)

        if not topics:
            raise ValueError("Please provide a Topic model")
        assert isinstance(topics, Topics)
        self._topics = topics
        self._log.info("Loaded topics model: %s", self._topics)

        if not docfreq:
            self._docfreq = None
            self._log.warning("Disabled document frequencies - you will "
                              "not be able to query arbitrary repositories.")
            self._repo2bow = None
        else:
            assert isinstance(docfreq, DocumentFrequencies)
            self._docfreq = docfreq
            self._docfreq = self._docfreq.prune(prune_df_threshold)
            self._log.info("Loaded docfreq model: %s", self._docfreq)
            self._repo2bow = Repo2BOW(
                {t: i for i, t in enumerate(self._topics.tokens)}, self._docfreq,
                **(repo2bow_kwargs or {}))
        
        if not bow:
            self._bow = None
            self._log.warning("No BOW cache was loaded.")
        else:
            assert isinstance(bow, BOW)
            self._bow = bow
            if self._topics.matrix.shape[1] != self._bow.matrix.shape[1]:
                raise ValueError("Models do not match: topics has %s tokens while bow has %s" %
                                 (self._topics.matrix.shape[1], self._bow.matrix.shape[1]))
            self._log.info("Attached BOW model: %s", self._bow)

    def query(self, url_or_path_or_name, size=5):
        if size > len(self._topics):
            raise ValueError("size may not be greater than the number of topics - %d" %
                             len(self._topics))
        token_vector = None
        if self._bow:
            try:
                repo_index = self._bow.documents_index(
                    url_or_path_or_name)
            except KeyError:
                match = self.GITHUB_URL_RE.match(url_or_path_or_name)
                if match:
                    name = match.group(2)
                    try:
                        repo_index = self._bow.documents_index(name)
                    except KeyError:
                        pass
            if repo_index:
                token_vector = self._bow.matrix[repo_index]

        if not token_vector:
            if not self._docfreq:
                raise ValueError("You need to specify document frequencies model to process "
                                 "custom repositories")
            bow_dict = self._repo2bow.convert_repository(url_or_path_or_name)
            token_vector = numpy.zeros(self._topics.matrix.shape[1], dtype=numpy.float32)
            for i, v in bow_dict.items():
                token_vector[i] = v
            token_vector = csr_matrix(token_vector)

        topic_vector = -numpy.squeeze(self._topics.matrix.dot(token_vector.T).toarray())
        order = numpy.argsort(topic_vector)
        result = []
        i = 0
        while len(result) < size and i < len(self._topics):
            topic = self._topics.topics[order[i]]
            if topic:
                result.append((topic, -topic_vector[order[i]]))
            i += 1
        return result
