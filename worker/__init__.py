import numpy as np

from typing import Tuple, NamedTuple, Type

class Runner(**kwargs):
    def __init__(self):
        pass


class OptResult(NamedTuple):
    values: np.ndarray
    states: np.ndarray
    failure: Tuple[Type[Exception], Exception, str]
