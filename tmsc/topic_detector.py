import logging
import re

from ast2vec import Topics, Repo2Base, DocumentFrequencies
from ast2vec.bow import BOWBase
from ast2vec.model2.source2bow import Uasts2BOW
from modelforge.backends import create_backend
import numpy
from scipy.sparse import csr_matrix

from tmsc.environment import initialize


class Repo2BOW(Repo2Base):
    """
    Implements the step repository -> :class:`ast2vec.nbow.NBOW`.
    """
    MODEL_CLASS = BOWBase

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
                 gcs_bucket=None, initialize_environment=True, repo2bow_kwargs=None):
        if initialize_environment:
            initialize()
        self._log = logging.getLogger("topic_detector")
        self._log.setLevel(verbosity)
        if gcs_bucket:
            backend = create_backend(args="bucket=" + gcs_bucket)
        else:
            backend = create_backend()
        if topics is None:
            self._topics = Topics(log_level=verbosity).load(backend=backend)
        else:
            assert isinstance(topics, Topics)
            self._topics = topics
        self._log.info("Loaded topics model: %s", self._topics)
        if docfreq is None:
            if docfreq is not False:
                self._docfreq = DocumentFrequencies(log_level=verbosity).load(
                    source=self._topics.get_dependency("docfreq")["uuid"], backend=backend)
            else:
                self._docfreq = None
                self._log.warning("Disabled document frequencies - you will "
                                  "not be able to query custom repositories.")
        else:
            assert isinstance(docfreq, DocumentFrequencies)
            self._docfreq = docfreq
        if bow is not None:
            assert isinstance(bow, BOWBase)
            self._bow = bow
            if self._topics.matrix.shape[1] != self._bow.matrix.shape[1]:
                raise ValueError("Models do not match: topics has %s tokens while bow has %s" %
                                 (self._topics.matrix.shape[1], self._bow.matrix.shape[1]))
            self._log.info("Attached BOW model: %s", self._bow)
        else:
            self._bow = None
            self._log.warning("No BOW cache was loaded.")
        if self._docfreq is not None:
            self._repo2bow = Repo2BOW(
                {t: i for i, t in enumerate(self._topics.tokens)}, self._docfreq,
                **(repo2bow_kwargs or {}))
        else:
            self._repo2bow = None

    def query(self, url_or_path_or_name, size=5):
        if size > len(self._topics):
            raise ValueError("size may not be greater than the number of topics - %d" %
                             len(self._topics))
        if self._bow is not None:
            try:
                repo_index = self._bow.repository_index_by_name(
                    url_or_path_or_name)
            except KeyError:
                repo_index = -1
            if repo_index == -1:
                match = self.GITHUB_URL_RE.match(url_or_path_or_name)
                if match is not None:
                    name = match.group(2)
                    try:
                        repo_index = self._bow.repository_index_by_name(name)
                    except KeyError:
                        pass
        else:
            repo_index = -1
        if repo_index >= 0:
            token_vector = self._bow.matrix[repo_index]
        else:
            if self._docfreq is None:
                raise ValueError("You need to specify document frequencies model to process "
                                 "custom repositories")
            bow_dict = self._repo2bow.convert_repository(url_or_path_or_name)
            token_vector = numpy.zeros(self._topics.matrix.shape[1], dtype=numpy.float32)
            for i,v in bow_dict.items():
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