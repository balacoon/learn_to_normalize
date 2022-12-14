"""
Copyright 2022 Balacoon

Recipe to build an addon for balacoon_frontend.
"""

import os
import shutil
import argparse
import logging

import msgpack

from balacoon_frontend import TextNormalizer as tn

from learn_to_normalize.grammar_utils.grammar_loader import GrammarLoader


def parse_args():
    ap = argparse.ArgumentParser(
        description="Packs rules for text conversion into spoken form, used by balacoon_frontend package.",
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
    # TODO reuse fields from text_normalization package
    addon = {tn.AddonFields.ID_KEY: tn.AddonFields.ID_VALUE, tn.AddonFields.LOCALE: args.locale}
    tokenizer_config, verbalizer_config, verbalizer_specification = loader.get_configs()
    addon[tn.AddonFields.TOKENIZER_CONFIG] = tokenizer_config
    addon[tn.AddonFields.VERBALIZER_CONFIG] = verbalizer_config
    addon[tn.AddonFields.VERBALIZER_SPECIFICATION] = verbalizer_specification
    os.makedirs(args.work_dir, exist_ok=True)
    addon[tn.AddonFields.TOKENIZER] = loader.get_tokenizer(args.work_dir)
    addon[tn.AddonFields.VERBALIZER] = loader.get_verbalizer(args.work_dir)
    default_addon_path = os.path.join(args.work_dir, "normalization.addon")
    with open(default_addon_path, "wb") as fp:
        msgpack.dump([addon], fp)
    if args.out:
        shutil.copy(default_addon_path, args.out)
