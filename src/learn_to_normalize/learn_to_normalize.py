"""
Copyright 2022 Balacoon

Recipe to build an addon for text_normalization.
"""

import argparse
import logging

from learn_to_normalize.grammar_utils.grammar_loader import GrammarLoader


def parse_args():
    ap = argparse.ArgumentParser(
        description="Packs rules for text conversion into spoken form, used by text_normalization package.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap.add_argument(
        "--grammars",
        required=True,
        help="Directory with normalization grammars. Those are stored in repos that are submodules to this repo. "
        "For ex. `grammars/en_us_normalization/production`",
    )
    ap.add_argument(
        "--locale",
        required=True,
        help="Locale corresponding to resources, that will be stored in addon. For ex. `en_us`",
    )
    ap.add_argument(
        "--work-dir",
        default="work_dir",
        help="Working directory to put intermediate artifacts to",
    )
    ap.add_argument(
        "--out",
        help="Path to put produced artifact to. It is also stored at work_dir/normalization.addon",
    )
    args = ap.parse_args()
    return args


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    loader = GrammarLoader(args.grammars)
