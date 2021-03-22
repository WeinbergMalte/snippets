"""Contains tests for transformers module."""
# pylint: disable=missing-docstring

import pytest
import pandas as pd
import numpy as np
from itertools import product, permutations
from pandas.testing import assert_frame_equal



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

        df_in = get_test_frame()
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



def get_test_frame(which=0):

    if which == 0:
        data = [
            [4, "A", 1, "Emmanuel"],
            [0, "C", 2, "Emmanuel"],
            [5, "A", 3, "Angie"],
            [9, "B", 4, "Angie"],
            [8, "B", 5, "Boris"],
            [1, "C", 6, "Boris"],
        ]
    elif which == 1:
        data = [
            [1, "B", 1, "Angie"],
            [2, "B", 2, "Angie"],
            [0, "B", 3, "Angie"],
            [300, "C", 4, "Emmanuel"],
            [400, "A", 5, "Emmanuel"],
            [500, "C", 6, "Emmanuel"],
            [200, "A", 7, "Emmanuel"],
            [21, "A", 8, "Boris"],
            [20, "B", 9, "Boris"],
        ]
    elif which == 2:
        data = [
            [0, "A", 1, "Angie"],
            [0, "A", 3, "Angie"],
            [0, "B", 5, "Boris"],
            [0, "B", 2, "Boris"],
            [0, "C", 4, "Emmanuel"],
            [0, "C", 6, "Emmanuel"],
        ]

    cols = ["target", "cat1", "cat2", "cat3"]
    return pd.DataFrame(data, columns=cols)


def get_expected_mapping(which=0):

    if which == 0:
        mapping = {
            "cat1": {"A": 1.0, "B": 2.0, "C": 0.0},
            "cat3": {"Emmanuel": 0.0, "Angie": 2.0, "Boris": 1.0},
        }
    elif which == 1:
        mapping = {
            "cat1": {"A": 1.0, "B": 0.0, "C": 2.0},
            "cat3": {"Emmanuel": 2.0, "Angie": 0.0, "Boris": 1.0},
        }
    elif which == 2:
        mapping = {
            "cat1": {"A": 0.0, "B": 0.0, "C": 0.0},
            "cat3": {"Emmanuel": 0.0, "Angie": 0.0, "Boris": 0.0},
        }

    # If only a single instance of a category is present in the fitted
    # dataframe, TargetEncoder will use the global average of the target.
    # Hence, only zeros will result from the combination of TargetEncoder
    # and OrdinalEncoder for 'cat2' column.
    mapping["cat2"] = {i: 0.0 for i in range(1, 10)}

    return mapping


class TestOrdinalTargetEncoding:
    @pytest.fixture
    def encoder(self):
        from utils.encoder import ordinal_target_encoding

        return ordinal_target_encoding

    # Iterate over permutations of indices for dataframe list
    # as well as different column selections:
    p_indexes = [[0], [1], [2], [0, 1], [0, 2], [1, 2], [0, 1, 2]]
    p_idxlist = [list(permutations(l)) for l in p_indexes]
    permutation_idx = [p for sublist in p_idxlist for p in sublist]
    permutation_col = [["cat1"], ["cat3"], ["cat1", "cat2"], ["cat1", "cat2", "cat3"]]
    permutation_list = list(product(permutation_idx, permutation_col))

    @pytest.mark.parametrize("indices, columns", permutation_list)
    def test_func(self, encoder, indices, columns):

        df_list_in = [get_test_frame(i) for i in indices]
        df_list_expected = df_list_in.copy()

        mapping = get_expected_mapping(indices[0])

        df_list_expected = list()
        for df in df_list_in:
            df_exp = df.copy()
            for c, m in mapping.items():
                if c not in columns:
                    continue
                df_exp[c] = df_exp[c].map(m)
            df_list_expected.append(df_exp)

        df_list_result = encoder(df_list_in, target_col="target", cols=columns)

        for df_expected, df_result in zip(df_list_expected, df_list_result):
            assert_frame_equal(df_expected, df_result)
