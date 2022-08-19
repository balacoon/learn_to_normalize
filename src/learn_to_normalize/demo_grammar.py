"""
Copyright 2022 Balacoon

Interactive demo for specific grammar
"""

import argparse
import logging
import sys

import pynini

from learn_to_normalize.grammar_utils.grammar_loader import GrammarLoader


def parse_args():
    ap = argparse.ArgumentParser(description="Interactive demo for individual grammar")
    ap.add_argument("--grammars", required=True, help="Directory with grammars")
    ap.add_argument(
        "--module",
        required=True,
        help="Module with a grammar, for ex. classify.abbreviation",
    )
    ap.add_argument(
        "--name",
        required=True,
        help="Grammar class to use test, for ex. AbbreviationFst",
    )
    args = ap.parse_args()
    return args


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    loader = GrammarLoader(args.grammars)
    grammar = loader.get_grammar(args.module, args.name)
    logging.info("Provide input for {} grammar and press ENTER:".format(args.name))

    for line in sys.stdin:
        line = line.strip()
        text = pynini.escape(line)
        result = grammar.apply(text)
        logging.info(result)
