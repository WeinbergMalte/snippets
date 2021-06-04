""" Module containing utility functions. """

import numpy as np
import pandas as pd
from typing import Union


def listify(x) -> Union[list, tuple, np.ndarray]:
    """Returns single-element list of x if x is not of array-type."""
    if not isinstance(x, (list, tuple, np.ndarray)):
        return [x]
    return x


def pd_column_analysis(
    ds: pd.Series, value_col: str = "values", sort: str = None
) -> pd.DataFrame:
    """Returns formatted dataframe from standard column analysis"""

    df = ds.reset_index().rename(columns={"index": "cols", 0: value_col})

    if sort is None:
        return df

    if sort.lower().startswith("asc"):
        df = df.sort_values(by=value_col, ascending=True)

    if sort.lower().startswith("desc"):
        df = df.sort_values(by=value_col, ascending=False)

    return df.reset_index(drop=True)


def pd_block_break_df(
    df: pd.DataFrame, column_breaks: int = 4, min_break_len: int = 20
) -> pd.DataFrame:
    """Breaks dataframe with few columns into blocks for readability."""

    if df.shape[0] <= min_break_len:
        return df

    list_df = list()
    for idx, d in enumerate(np.array_split(df, column_breaks)):
        df_i = pd.DataFrame(d).reset_index(drop=True)
        df_i.columns = [f"{c}_{idx}" for c in df.columns]
        list_df.append(df_i)

    return pd.concat(list_df, axis=1)


def pd_null_ratio(
    df: pd.DataFrame,
    value_col: str = "null_ratio",
    column_breaks: int = 4,
    min_break_len: int = 20,
    cmap: str = "Reds",
) -> pd.DataFrame:
    """Retrurns styled dataframe with null ratios of columns."""

    df_n = pd_column_analysis(df.isnull().mean(), value_col=value_col)
    df_n = pd_block_break_df(
        df_n, column_breaks=column_breaks, min_break_len=min_break_len
    )
    return df_n.style.format(
        "{:.2%}", subset=df_n.select_dtypes(float).columns
    ).background_gradient(cmap=cmap, vmin=0.0, vmax=1.0)
