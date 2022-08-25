"""
Copyright 2022 Balacoon

factory to create data iterator based on
data name.
"""

from enum import Enum
from typing import List

from learn_to_normalize.evaluation.data_iterator import DataIterator
from learn_to_normalize.evaluation.google_data.google_data_iterator import GoogleDataIterator


class Datasets(Enum):
    """
    Names of datasets supported for evalation
    """
    GOOGLE_EN = "google_en"


def get_supported_datasets() -> List[str]:
    """
    helper function that returns all supported dataset names

    Returns
    -------
    res: List[str]
        list of names that can be passed to :func:`.get_data_iterator`
    """
    return [x.value for x in Datasets]


def get_data_iterator(name: str, location: str, subset: str, n_utterances: int = -1) -> DataIterator:
    """
    Creates data iterator by dataset name.

    Parameters
    ----------
    name: str
        dataset name, check :func:`get_supported_datasets` for the
        list of possible values.
    location: str
        downloaded and unpacked directory with the dataset
    subset: str
        Subset of the data to iterate through. Passed to data iterator
    n_utterances: int
        if > 0, reads only first n_utterances from the subset
    """
    if name == Datasets.GOOGLE_EN.value:
        return GoogleDataIterator(location=location, subset=subset, n_utterances=n_utterances)
    else:
        raise RuntimeError("Unknown dataset: {}. Please pick one from the list {}".format(
            name, str(get_supported_datasets())))
