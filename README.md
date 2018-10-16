# TMSC [![Build Status](https://travis-ci.org/src-d/tmsc.svg)](https://travis-ci.org/src-d/tmsc) [![codecov](https://codecov.io/github/src-d/tmsc/coverage.svg?branch=develop)](https://codecov.io/gh/src-d/tmsc) [![Docker Build Status](https://img.shields.io/docker/build/srcd/tmsc.svg)](https://hub.docker.com/r/srcd/tmsc) [![PyPI](https://img.shields.io/pypi/v/tmsc.svg)](https://pypi.python.org/pypi/tmsc)

TMSC (Topics Modeling on Source Code) is a command line application to discover the topics of
a repository the user provides. A "topic" is a set of keywords, in this case source code
identifiers, which typically occur together. This project has **nothing** to do with
[GitHub topics](https://github.com/blog/2309-introducing-topics).

```
$ tmsc https://github.com/apache/spark
...
                Parallel and distributed processing - General IT	4.43
                Machine Learning, sklearn-like APIs - General IT	3.87
               Java/JS + async + JSON serialization - General IT	3.58
                Java string input/output - Programming languages	3.29
                            Cryptography: libraries - General IT	3.23
                        SQL, working with databases - General IT	3.11
                          Java: Spring, Hibernate - Technologies	3.09
                              Operations on numbers - General IT	2.98
                               Distributed clusters - General IT	2.62
           Functional programming, Scala - Programming languages	2.60
```

Automatic topic inference can be useful for cataloging repositories or mining concepts from them.
The current model was trained on GitHub repositories cloned in October 2016 after
[de-fuzzy-forking](https://blog.sourced.tech/post/minhashcuda/). There is a
[paper](https://arxiv.org/abs/1704.00135) on it.

### Installation

```
pip3 install tmsc
```

### Usage

Command line:

```
$ tmsc https://github.com/apache/spark
```

Python API:

```python
import tmsc

engine = tmsc.Topics()
print(engine.query("https://github.com/apache/spark"))
```

### Docker image

```
docker build -t srcd/tmsc
docker run -d --privileged -p 9432:9432 --name bblfshd bblfsh/bblfshd
docker exec -it bblfshd bblfshctl driver install --recommended
docker run -it --rm srcd/tmsc https://github.com/apache/spark
```

In order to cache the downloaded models:

```
docker run -it --rm -v /path/to/cache/on/host:/root srcd/tmsc https://github.com/apache/spark
```

### Contributions

...are welcome! See [CONTRIBUTING](CONTRIBUTING.md) and [code of conduct](CODE_OF_CONDUCT.md).

### License

[Apache 2.0](LICENSE.md)
