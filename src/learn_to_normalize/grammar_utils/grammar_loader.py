"""
Copyright 2022 Balacoon

class that loads grammars from directory with
normalization rules.
directory should have specific structure.
"""

import importlib
import os
import sys
from typing import Tuple

import pynini

from learn_to_normalize.grammar_utils.base_fst import BaseFst


class GrammarLoader:
    """
    Loads normalization grammars from directory of specific structure
    """

    NORMALIZATION_MODES = ["classify", "verbalize"]
    CONFIGURATION_NAMES = [
        "tokenizer.ascii_proto",
        "verbalizer.ascii_proto",
        "verbalizer_serialization_spec.ascii_proto",
    ]

    def __init__(self, grammars_dir: str):
        # all imports within grammars repo are done relative to parent dir of grammar repo.
        # so <grammar_repo>/../ should be added to PYTHONPATH and suffix stored to be used
        # during grammar loading. First <grammar_repo> directory should be identified
        grammars_dir = os.path.abspath(grammars_dir)
        # find the repo location
        repo_dir = (
            os.popen("cd {} && git rev-parse --show-toplevel".format(grammars_dir))
            .read()
            .strip()
        )
        # add to PYTHONPATH directory one level higher than repo
        above_repo_dir = os.path.join(repo_dir, "..")
        sys.path.append(above_repo_dir)
        # find out location of rules inside of grammars repo
        self._module_prefix = os.path.relpath(grammars_dir, above_repo_dir).replace(
            "/", "."
        )
        self._grammars_dir = grammars_dir

        # test that there is minimal entry points for export
        for mode in self.NORMALIZATION_MODES:
            if not os.path.isfile(os.path.join(grammars_dir, mode, mode + ".py")):
                raise RuntimeError(
                    "Grammars directory is missing entry point: {}/{}.py".format(
                        mode, mode
                    )
                )
        for config_name in self.CONFIGURATION_NAMES:
            config_path = os.path.join(grammars_dir, "configs", config_name)
            if not os.path.isfile(config_path):
                raise RuntimeError(
                    "Grammars directory is missing text_normalization proto config: {}".format(
                        config_path
                    )
                )

    def get_grammar(self, module_str: str, class_name: str) -> BaseFst:
        """
        Loads grammar from grammar dir based on module name and class name of the grammar

        Paramaters
        ----------
        module_str: str
            module to load, for ex. classify.cardinal
        class_name: str
            fst class to load from the module, for ex. CardinalFst

        Returns
        -------
        grammar: BaseFST
            grammar loaded by the name and initialized
        """
        grammar_path = os.path.join(
            self._grammars_dir, module_str.replace(".", "/") + ".py"
        )
        if not os.path.isfile(grammar_path):
            raise RuntimeError(
                "Cant get grammar from {}, {} doesn't exist".format(
                    module_str, grammar_path
                )
            )
        module = importlib.import_module(self._module_prefix + "." + module_str)
        if not hasattr(module, class_name):
            raise RuntimeError("{} doesn't have {}".format(grammar_path, class_name))
        grammar_class = getattr(module, class_name)
        grammar = grammar_class()
        assert isinstance(
            grammar, BaseFst
        ), "loaded grammar does not inherit base grammar"
        return grammar

    @staticmethod
    def _serialize_fst(fst: pynini.FstLike, rule_name: str, out_path: str) -> bytes:
        """
        Exports FAR, reads exported far as bytes.
        TODO: check if possible to serialize without saving to disk

        Parameters
        ----------
        fst: pynini.FstLike
            fst of a grammar to serialize
        rule_name: str
            name under which to store fst in FAR
        out_path: str
            path to export FAR to during serialization

        Returns
        -------
        res: bytes
            serialized fst as bytes
        """
        exporter = pynini.export.grm.Exporter(out_path)
        exporter[rule_name] = fst
        exporter.close()
        with open(out_path, "rb") as fp:
            res = fp.read()
        return res

    def get_verbalizer(self, work_dir: str) -> bytes:
        """
        Exports verbalizer, stores FAR on disk, returns serialized FAR

        Parameters
        ----------
        work_dir: str
            directory to store verbalizer FAR to

        Returns
        -------
        res: bytes
            serialized verbalizer
        """
        verb_path = os.path.join(work_dir, "verbalizer.far")
        verb = self.get_grammar("verbalize.verbalize", "VerbalizeFst")
        # should match rule name in configs/verbalizer.ascii_proto
        return self._serialize_fst(verb.fst, "ALL", verb_path)

    def get_tokenizer(self, work_dir: str) -> bytes:
        """
        Exports tokenizer/classifier, stores FAR on disk, returns serialized FAR

        Parameters
        ----------
        work_dir: str
            directory to store tokenizer FAR to

        Returns
        -------
        res: bytes
            serialized tokenizer
        """
        classify_path = os.path.join(work_dir, "tokenizer.far")
        classify = self.get_grammar("classify.classify", "ClassifyFst")
        # should match rule name in configs/tokenizer.ascii_proto
        return self._serialize_fst(classify.fst, "TOKENIZE_AND_CLASSIFY", classify_path)

    @staticmethod
    def _read_text_file(path: str) -> str:
        """
        Reads file from given path. Helper function to read config files

        Parameters
        ----------
        path: str
            path to read from

        Returns
        -------
        content: str
            read content of the file
        """
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        return content

    def get_configs(self) -> Tuple[str, str, str]:
        """
        Loads configurations required by text_normalization

        Returns
        -------
        configs: Tuple[str, str, str]
            Loaded proto configurations as strings.
            There are 3 configurations required by text_normalization package:
            tokenizer - defines name of the grammar and main rule
            verbalizer - defines name of grammar and main rule
            verbalizer serialization specification - fields of tokenized semiotic classes
        """
        configs = [
            self._read_text_file(os.path.join(self._grammars_dir, "configs", x))
            for x in self.CONFIGURATION_NAMES
        ]
        return configs
