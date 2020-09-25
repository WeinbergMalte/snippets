""" Module for preprocessing data. """

import pandas as pd
from sklearn.preprocessing import OrdinalEncoder
from category_encoders import TargetEncoder
from snippets.utils import listify


def ordinal_target_encoding(df_list, target_col, cols):
    """
    Applies ordinal target encoding of categorical feature columns
    from list of dataframes.
    Note that only the first dataframe (i.e. the training data)
    is used for target encoding to prevent leakage.

    Parameters:
    -----------

    df_list: list-type
        List of dataframes for encoding. Here, the first dataframe
        should be the training data as it is used for target-encoding.
    target_col: str
        Target column in dataframes that should be encoded.
    cols: list-type
        Categorical feature columns that are encoded.
    """

    df_list = listify(df_list)

    t_enc = TargetEncoder(cols=cols).fit(df_list[0], df_list[0][target_col])

    df_concat = pd.concat([t_enc.transform(df) for df in df_list])

    df_concat[cols] = OrdinalEncoder().fit_transform(df_concat[cols])

    return [df_concat.loc[df.index] for df in df_list]
