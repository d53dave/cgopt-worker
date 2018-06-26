import numpy as np

from typing import Tuple, NamedTuple, Type


class OptResult(NamedTuple):
    states: np.ndarray
    values: np.ndarray
    failure: Tuple[Type[Exception], Exception, str]
