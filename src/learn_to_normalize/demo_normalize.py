"""
Copyright 2022 Balacoon

Interactive text normalization demo with create addon
"""

import logging
import argparse

from text_normalization import TextNormalizer


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
    args = ap.parse_args()
    return args


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    normalizer = TextNormalizer(args.addon, args.locale)
    while True:
        utterance = input("Enter text: ")
        if not utterance:
            logging.info("No normalization for empty string")
            continue
        logging.info(normalizer.normalize(utterance))
