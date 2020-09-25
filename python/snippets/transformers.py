""" Module containing sklearn-type transformers. """
# pylint: disable=unused-argument,missing-docstring

import stumpy
import pandas as pd
from sklearn.base import TransformerMixin


class StumpyTransformer(TransformerMixin):
    """
    Calculates stumpy matrix profile data frame of lag-columns.
    Acceleration of row-wise computation with .swifter.apply()

    Parameters
    ----------

    m: int default=7
        Size of matrix profile window.
    col_prefix: str default='stumpy'
        Prefix of generated stumpy-columns.
    """

    def __init__(self, m=7, col_prefix="stumpy"):
        self.m = m
        self.col_prefix = col_prefix

    def fit(self, X, y=None):
        return self

    def _stumpy_row(self, row, s):
        if not row.sum():
            return pd.Series([0] * (s + 1 - self.m))
        return pd.Series(stumpy.stump(row, m=self.m)[:, 0])

    def transform(self, df, y=None):

        s = df.shape[1]
        df_stumpy = df.fillna(0).swifter.apply(self._stumpy_row, s=s, axis=1)
        df_stumpy.columns = [f"{self.col_prefix}_{i}" for i in range(s - self.m + 1)]

        return df_stumpy


class FullStumpyTransformer(TransformerMixin):
    """
    Selects lag columns from data frame and appends stumpy matrix profile.

    Parameters
    ----------

    m: int default=7
        Size of matrix profile window.
    cols: list-type
        List of lag columns in data frame.
    """

    def __init__(self, m, cols):
        self.m = m
        self.cols = cols

    def fit(self, X, y=None):
        return self

    def transform(self, df, y=None):

        df_stumpy = StumpyTransformer(self.m).fit_transform(df[self.cols])

        drop_cols = [c for c in df_stumpy.columns if c in df.columns]
        if len(drop_cols):
            df = df.drop(drop_cols, axis=1)

        return pd.concat([df, df_stumpy], axis=1)
