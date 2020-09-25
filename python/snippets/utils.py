""" Module containing utility functions. """

import numpy as np


def _listify(x):
    """Returns single-element list of x if x is not of array-type."""
    if not isinstance(x, (list, tuple, np.ndarray)):
        return [x]
    return x
