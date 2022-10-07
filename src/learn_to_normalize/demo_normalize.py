"""
Copyright 2022 Balacoon

Interactive text normalization demo with create addon
"""

import time
import logging
import argparse

from balacoon_frontend import TextNormalizer


def parse_args():
    ap = argparse.ArgumentParser("Returns normalized text given addon.")
    ap.add_argument(
        "--addon",
        required=True,
        help="Path to pronunciation addon (work_dir/normalization.addon",
    )
    ap.add_argument(
        "--locale",
        default="",
        help="If addon has multiple normalization fields sections, disambiguate one to use, by providing locale",
    )
    ap.add_argument(
        "--file",
        help="If provided, reads utterances to normalize from a file"
    )
    args = ap.parse_args()
    return args


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    normalizer = TextNormalizer(args.addon, args.locale)
    if args.file:
        num = 0
        elapsed = 0
        with open(args.file, "r") as fp:
            for line in fp:
                line = line.strip()
                if line:
                    start = time.time()
                    logging.info(normalizer.normalize(line))
                    elapsed += time.time() - start
                    num += 1
        logging.info("Normalizing at {} seconds / utterance".format(elapsed / float(num)))
    else:
        while True:
            utterance = input("Enter text: ")
            if not utterance:
                logging.info("No normalization for empty string")
                continue
            logging.info(normalizer.normalize(utterance))
