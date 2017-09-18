from setuptools import setup, find_packages


setup(
    name="tmsc",
    description="Part of source{d}'s stack for machine learning on source "
                "code. Provides API and tools to detect topics in Git "
                "repositories.",
    version="0.1.1-alpha",
    license="Apache 2.0",
    author="source{d}",
    author_email="machine-learning@sourced.tech",
    url="https://github.com/src-d/tmsc",
    download_url="https://github.com/src-d/tmsc",
    packages=find_packages(exclude=("tmsc.tests",)),
    entry_points={
        "console_scripts": ["tmsc=tmsc.__main__:main"],
    },
    keywords=["machine learning on source code", "topic modeling",
              "github", "bblfsh", "babelfish", "ast2vec"],
    install_requires=["ast2vec>=0.3.0-alpha"],
    package_data={"": ["LICENSE", "README.md"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries"
    ]
)