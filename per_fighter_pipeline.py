"""
The data as downloaded is on a mostly per fight basis, we'd like to convert it into a per fighter form of some sort.
Some wrangling will probs be required. Maybe a cheeky bit of slap and tickle as well, who knows...

TODO: - identify what columns should be salvaged and how  <- more likely I'll be adding than taking away tbh
      - write pipeline for preforming the transformation  <- 1/2 done
      - build tests where necessary  <- so far nothing test worthy :(
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
    cols_to_hash: Tuple[pd.Series, ...],
) -> pd.DataFrame:
    """Create 16 character alphanumeric hash function using specified columns.

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
        .apply(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())
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


def split_df_by_col(
    df: pd.DataFrame,
    exc_substring: str = 'R_',
    inc_substring: str = 'B_',
    corner: str = 'Blue',
) -> pd.DataFrame:
    """Create per fighter df by taking only columns relevant to the bout on the whole and the specified corner.

    Parameters
    ----------
    df : Input dataframe pertaining to both fighters.
    exc_substring : Substring of column names to exclude from output df.
    inc_substring : Substring of column names that will be included, but without this substring.
    corner : Corner the specified fighter was fighting out of.

    Notes
    -----
    We need to maintain the knowledge of which corner the fighter came from as some columns such as 'winner' are given
    to the corner not the fighter. For now, this will be done by adding a 'corner' column.
    TODO: convert these columns to binary where appropriate? or at least make them not corner dependant...

    Returns
    -------
    Only data pertaining to the specified corner / the whole bout, with generic column names.
    """
    opponent = '{}fighter'.format(exc_substring)

    columns_to_keep = [col for col in df.columns if exc_substring not in col]
    columns_to_keep.append(opponent)

    column_names = {col: col.replace(inc_substring, '') for col in columns_to_keep}
    column_names[opponent] = 'opponent'

    per_fighter_df = df[columns_to_keep].copy()
    per_fighter_df.rename(
        columns=column_names,
        inplace=True
    )
    per_fighter_df['corner'] = corner

    return per_fighter_df


def create_per_fighter_df() -> pd.DataFrame:
    """Read in and split the master data into a per fighter dataframe.

    Returns
    -------
    Per fighter form of the master data.
    """
    df = get_master_df()

    red_corner_df = split_df_by_col(df, exc_substring='B_', inc_substring='R_', corner='Red')
    blue_corner_df = split_df_by_col(df, exc_substring='R_', inc_substring='B_', corner='Blue')

    df = pd.concat([red_corner_df, blue_corner_df])

    return df


if __name__ == '__main__':
    pass  # This will eventually run the bloody bastard pipeline.
