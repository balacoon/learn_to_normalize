"""
Copyright 2022 Balacoon

Tool to run evaluation of the rules on large corpus.
Can be used to evaluate or enhance existing rules.
"""

import tqdm
import logging
import argparse

from text_normalization import TextNormalizer

from learn_to_normalize.evaluation.data_iterator_factory import get_supported_datasets, get_data_iterator


def setup_logger(log_path: str = None):
    """
    Helper function that set ups handlers in logger.
    """
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    if log_path:
        file_handler = logging.FileHandler(log_path, mode="w")
        file_handler.setLevel(logging.WARNING)
        logger.addHandler(file_handler)


def parse_args():
    ap = argparse.ArgumentParser(
        description="Runs evaluation of text normalization on a corpus",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap.add_argument(
        "--addon",
        required=True,
        help="Pack addon with text normalization rules obtained with `learn_to_normalize`",
    )
    ap.add_argument(
        "--dataset",
        required=True,
        choices=get_supported_datasets(),
        help="Dataset name, defines how to parse data from datadir",
    )
    ap.add_argument(
        "--datadir",
        required=True,
        help="Directory with the data",
    )
    ap.add_argument(
        "--subset",
        default="test",
        help="Subset of the data to run evaluation on. Check data iteration implementation for details",
    )
    ap.add_argument(
        "--num",
        default=-1,
        type=int,
        help="Number of sentences to read from a subset. By default - reads all"
    )
    ap.add_argument(
        "--ignore-case",
        action="store_true",
        help="In balacoon upper case indicate spelling. It may trigger a lot of false alarm in reporting."
    )
    ap.add_argument(
        "--log",
        help="If provided, additionally stores the log into specified path",
    )
    args = ap.parse_args()
    return args


def main():
    args = parse_args()
    setup_logger(log_path=args.log)
    data_iterator = get_data_iterator(name=args.dataset, location=args.datadir, subset=args.subset, n_utterances=args.num)
    tn = TextNormalizer(args.addon)
    total_num, incorrect_num = 0, 0
    for unnormalized, normalized in tqdm.tqdm(data_iterator):
        result = tn.normalize(unnormalized)
        total_num += 1
        if args.ignore_case:
            result = result.lower()
            normalized = normalized.lower()
        if result != normalized:
            logging.warning("\nExpected: " + normalized)
            logging.warning("Obtained: " + result)
            logging.warning("Original: " + unnormalized)
            incorrect_num += 1
    accuracy = (total_num - incorrect_num) / float(total_num)
    logging.warning("Accuracy: {}".format(accuracy))

