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

    df = ds.reset_index().rename(columns={"index": "columns", 0: value_col})

    if sort is None:
        return df

    if sort.lower().startswith("asc"):
        df = df.sort_values(by=value_col, ascending=True)

    if sort.lower().startswith("desc"):
        df = df.sort_values(by=value_col, ascending=False)

    return df.reset_index(drop=True)


def pd_null_ratio(df: pd.DataFrame, value_col: str = "null_ratio") -> pd.DataFrame:
    """Retrurns styled dataframe with null ratios of columns."""

    df_nulls = pd_column_analysis(df.isnull().mean(), value_col=value_col)
    return df_nulls.style.format("{:.2%}", subset=[value_col]).background_gradient(
        cmap="Reds", vmin=0.0, vmax=1.0
    )
