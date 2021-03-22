"""Module containing custom encoding functions."""

import pandas as pd
from uuid import uuid4
from sklearn.preprocessing import OrdinalEncoder
from category_encoders import TargetEncoder
from mw_utils.utils import listify


def ordinal_target_encoding(df_list, target_col, cols):
    """
    Applies ordinal target encoding of categorical feature columns
    from list of dataframes.
    Note that only the first dataframe (i.e. the training data)
    is used for target encoding to prevent leakage.

    Parameter
    ---------
    df_list: list
        List of dataframes for encoding. Here, the first dataframe
        should be the training data as it is used for target-encoding.
    target_col: str
        Target column in dataframes
        that is used for encoding the categorical feature columns below.
    cols: list
        Categorical feature columns that are encoded.

    Return
    ------
    list
        List of dataframes (same as input but with encoded columns)
    """

    cols = listify(cols)
    df_list = listify(df_list)

    # Fit TargetEncoder only on first dataframe in list
    t_enc = TargetEncoder(cols=cols).fit(df_list[0], df_list[0][target_col])

    # Generate temporary column in order to divide concatenated dataframes.
    # This is neccessary to avoid conflicts of dataframes with equal indices.
    tmp_col = str(uuid4())
    df_list_out = list()
    for idx, df in enumerate(df_list):
        # Apply target encoding to each dataframe in list.
        df = t_enc.transform(df)
        df[tmp_col] = idx
        df_list_out.append(df)
    # Concatenate dataframe and apply ordinal encoding globally.
    df_concat = pd.concat(df_list_out)
    df_concat[cols] = OrdinalEncoder().fit_transform(df_concat[cols])

    # Split dataframe again into list and drop temporary column.
    df_list_out = list()
    for idx in range(len(df_list)):
        df = df_concat[df_concat[tmp_col] == idx]
        df = df.drop(tmp_col, axis=1)
        df_list_out.append(df)

    return df_list_out
