## Topic Modeling on Source Code

[![Build Status](https://travis-ci.org/src-d/tmsc.svg)](https://travis-ci.org/src-d/tmsc) [![codecov](https://codecov.io/github/src-d/tmsc/coverage.svg?branch=develop)](https://codecov.io/gh/src-d/tmsc) [![PyPI](https://img.shields.io/pypi/v/tmsc.svg)](https://pypi.python.org/pypi/tmsc)

Finding out topics related to Git repositories.

```python
import tmsc

engine = tmsc.Topics()
print(engine.query("https://github.com/tensorflow/tensorflow"))
```

### Docker image

```
docker build -t srcd/tmsc .
docker run -d --privileged -p 9432:9432 --name bblfsh --rm bblfsh/server
docker run -it --rm srcd/tmsc https://github.com/apache/spark
```

In order to cache the downloaded models:

```
docker run -it --rm -v /path/to/cache/on/host:/root srcd/tmsc https://github.com/apache/spark
```