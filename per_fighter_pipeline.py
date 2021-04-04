"""
The data as downloaded is on a mostly per fight basis, we'd like to convert it into a per fighter form of some sort.
some wrangling will probs be required.

TODO: - identify what columns should be salvaged and how
      - write pipeline for preforming the transformation
      - build tests where neccessary
      - set up sphinx docs <- looks like we need something to allow for numpy docs
"""
import pandas as pd
import hashlib
from typing import List, Tuple


def set_mixed_dtype_to_int(
    df: pd.DataFrame,
    columns: List[str],
) -> pd.DataFrame:
    """Set columns to integer type, turn everything that's non numeric in these columns to NaN.

    Parameters
    ----------
    df : Input dataframe.
    columns : Columns to be set to integer.

    Returns
    -------
    Dataframe including type cast columns.
    """
    df[columns] = df[columns].apply(pd.to_numeric, errors='coerce', downcast='integer')

    return df


def create_col_hash(
        df: pd.DataFrame,
        cols_to_hash: Tuple[pd.Series],
) -> pd.DataFrame:
    """Create 16 digit hash function using specified columns.

    Parameters
    ----------
    df : Input dataframe.
    cols_to_hash : Tuple of the columns you wish to hash.

    Returns
    -------
    Dataframe with extra 'bout_id' column.
    """
    df['bout_id'] = (
        cols_to_hash
        .apply(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())  # alphanumeric hash per fight
    )

    return df


def get_master_df() -> pd.DataFrame:
    """Read in master UFC data to pandas, adding a unique fight ID.

    Notes
    -----
    Data in '..._match_weightclass_rank' columns is corrupted for fights from UFC 257, showing fighter names rather
    than numeric rank, this is circumvented using trickery and deception within this function.

    Returns
    -------
    Dataframe of UFC master data.
    """
    mixed_type_cols = ['B_match_weightclass_rank', 'R_match_weightclass_rank']

    df = pd.read_csv(
        'data/ufc-master.csv',
        encoding='utf-8',
        dtype={col: str for col in mixed_type_cols}  # for columns of mixed type, force string then convert to int.
    )

    df = set_mixed_dtype_to_int(df, mixed_type_cols)
    df = create_col_hash(df, (df.R_fighter + df.B_fighter + df.date))

    return df


if __name__ == '__main__':
    pass
