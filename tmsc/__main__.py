import argparse
import json
import logging
import sys
import os

from sourced.ml.models import BOW, Topics, DocumentFrequencies
from modelforge.backends import create_backend
from modelforge.index import GitIndex

from tmsc.environment import initialize
from tmsc.topic_detector import TopicDetector

DEFAULT_BBLFSH_TIMEOUT = 20

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Repository URL or path or name.")
    parser.add_argument("--log-level", default="INFO",
                        choices=logging._nameToLevel,
                        help="Logging verbosity.")
    parser.add_argument("--topics", default=None, help="Topic model URL or path.")
    parser.add_argument("--df", default=None,
                        help="Document frequencies URL or path.")
    parser.add_argument("--bow", default=None, help="BOW model URL or path.")
    parser.add_argument("--bblfsh", default=None,
                        help="babelfish server address.")
    parser.add_argument(
        "--timeout", type=int, default=None,
        help="Babelfish timeout - longer requests are dropped. Default is %s." %
             DEFAULT_BBLFSH_TIMEOUT)
    parser.add_argument("--gcs", default=None, help="GCS bucket to use.")
    parser.add_argument("--linguist", default=None,
                        help="Path to src-d/enry or github/linguist.")
    parser.add_argument("--prune-df", default=20, type=int,
                        help="Minimum number of times an identifer must occur in different "
                             "documents to be taken into account.")
    parser.add_argument("--index_repo", default="https://github.com/src-d/models",
                        help="Models index repository.")
    parser.add_argument("--index_cache", default=os.path.join(BOW.cache_dir(), "models"),
                        help="Local cache of models index repository")
    parser.add_argument("-n", "--nnn", default=10, type=int,
                        help="Number of topics to print.")
    parser.add_argument("-f", "--format", default="human", choices=["json", "human"],
                        help="Output format.")

    args = parser.parse_args()
    if args.linguist is None:
        args.linguist = "./enry"
    initialize(args.log_level, enry=args.linguist)

    if args.gcs:
        backend = create_backend(args="bucket=" + args.gcs)
    else:
        git_index = GitIndex(index_repo=args.index_repo, cache=args.index_cache, log_level=args.log_level)
        backend = create_backend(git_index=git_index)

    args.topics = Topics(log_level=args.log_level).load(source=args.topics, backend=backend) #source=args.topics
    args.df = DocumentFrequencies(log_level=args.log_level).load(source=args.df, backend=backend)
    #args.bow = BOW(log_level=args.log_level).load(source=args.bow, backend=backend)

    sr = TopicDetector(
        topics=args.topics, docfreq=args.df, bow=args.bow, verbosity=args.log_level,
        prune_df_threshold=args.prune_df, repo2bow_kwargs={
            "linguist": args.linguist,
            "bblfsh_endpoint": args.bblfsh,
            "timeout": args.timeout})

    topics = sr.query(args.input, size=args.nnn)
    
    if args.format == "json":
        json.dump({"repository": args.input, "topics": topics}, sys.stdout)
    elif args.format == "human":
        for t, r in topics:
            print("%64s" % t, "%.2f" % r, sep="\t")


if __name__ == "__main__":
    sys.exit(main())
