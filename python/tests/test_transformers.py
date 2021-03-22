"""Contains tests for transformers module."""
# pylint: disable=missing-docstring

import pytest
import pandas as pd
import numpy as np
from itertools import product, permutations
from pandas.testing import assert_frame_equal


def get_testframe():

    data = [
        ["c1", "A", "2020-10-22", "2020-10-23", 1, 100, 1.3, 1.0],
        ["c2", "C", "2020-10-23", "2020-10-23", 2, 200, 1.5, 1.0],
        ["c2", "A", "2020-10-24", "2020-10-23", 4, 400, 3.8, 1.0],
        ["c3", "B", "2020-10-21", "2020-10-23", 3, -300, 1.7, -1.0],
        ["c3", np.nan, "2020-10-21", "2020-10-23", 6, -300, np.nan, -1.0],
    ]
    cols = ["cat1", "cat2", "date1", "date2", "int1", "int2", "float1", "float2"]

    df = pd.DataFrame(data, columns=cols)
    df["date1"] = pd.to_datetime(df["date1"])
    df["date2"] = pd.to_datetime(df["date2"])

    return df


class TestLog1pTransformer:
    @pytest.fixture
    def trf(self):
        from mw_utils.transformers import Log1pTransformer

        return Log1pTransformer

    bools = [False, True]
    cols = ["int1", "int2", "float1"]
    variants = [i for i in product(cols, bools, bools)]

    @pytest.mark.parametrize("column, retain, fill", variants)
    def test_func(self, trf, column, retain, fill):

        df_in = get_testframe()
        df_expected = df_in.copy()

        val = df_in[column]
        if fill:
            val = val.fillna(0)

        if retain:
            df_expected[column] = np.log1p(val.abs()) * np.sign(val)
        else:
            df_expected[column] = np.log1p(val.abs())

        df_result = trf(column, retain_sign=retain, fillna=fill).fit_transform(df_in)
        assert_frame_equal(df_expected, df_result)
