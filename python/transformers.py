from sklearn.base import TransformerMixin
from sklearn.preprocessing import OrdinalEncoder
from category_encoders import TargetEncoder


def listify(x):
    """Returns single-element list of x if x is neither list or tuple already."""
    if not isinstance(x, list) and not isinstance(x, tuple):
        return [x]
    return x


class CategoryTargetEncoder(TransformerMixin):
    """
    Encodes categorical features according to their mean target value.

    Parameters
    ----------
    cols: str, list, tuple
        Column name or list of column names that should be encoded.
    target_col: str
        Name of target column.
    ordinal_transform: bool
        Specifies if transformed columns should be returned as ordinals.
    """

    def __init__(self, cols, target_col, ordinal_transform=False):
        self.cols = listify(cols)
        self.target_col = target_col
        self.ordinal_transform = ordinal_transform

    def fit(self, X, y=None):
        return self

    def transform(self, X):

        t_enc = TargetEncoder(cols=self.cols)

        X = t_enc.fit_transform(X, X[self.target_col])

        if not self.ordinal_transform:
            return X

        o_enc = OrdinalEncoder()
        X[self.cols] = o_enc.fit_transform(X[self.cols])
        return X
