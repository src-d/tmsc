## Topic Modeling on Source Code

[![Build Status](https://travis-ci.org/src-d/tmsc.svg)](https://travis-ci.org/src-d/tmsc) [![codecov](https://codecov.io/github/src-d/tmsc/coverage.svg?branch=develop)](https://codecov.io/gh/src-d/tmsc) [![PyPI](https://img.shields.io/pypi/v/tmsc.svg)](https://pypi.python.org/pypi/tmsc)

Finding out topics related to Git repositories.

```python
import tmsc

engine = tmsc.Topics()
print(engine.query("https://github.com/tensorflow/tensorflow"))
```