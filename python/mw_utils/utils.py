""" Module containing utility functions. """

import numpy as np
from typing import Union


def listify(x) -> Union[list, tuple, np.ndarray]:
    """Returns single-element list of x if x is not of array-type."""
    if not isinstance(x, (list, tuple, np.ndarray)):
        return [x]
    return x
