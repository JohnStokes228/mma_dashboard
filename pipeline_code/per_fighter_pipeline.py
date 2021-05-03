"""
The data as downloaded is on a mostly per fight basis, we'd like to convert it into a per fighter form of some sort.
Some wrangling will probs be required. Maybe a cheeky bit of slap and tickle as well, who knows...

I've scraped some additional data from wikipedia, but due to the websites rather chaotic nature some amount of post
processing is required to get it into a shape where it can be joined to the rest of the data. I wont save these to csv
alone, but rather as part of the merged master file, just to cut down on excess files and since I know if i need to
repeat the scrape that the data will need re transforming.

The camp data is both the hardest to make useful and the least useful once transformed so hurray for wasted efforts I
guess.

TODO: - identify what columns should be salvaged and how  <- more likely I'll be adding than taking away tbh
      - write pipeline for preforming the transformation  <- 1/2 done
      - build tests where necessary  <- built a few I guess...
      - set up sphinx docs <- looks like we need something to allow for numpy docs
      - complete_df has extra rows in it <- looks like at least one fighter has multiple nationalities <<- generic name?
      - clean where appropriate... <- 'derrick' needs a clean lads
      - logger to log things needs setting up

"""
import pandas as pd
import numpy as np
import hashlib
import json
import re
from typing import List, Tuple, Dict
from functools import reduce


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

    Returns
    -------
    Only data pertaining to the specified corner / the whole bout, with generic column names.
    """
    opponent = '{}fighter'.format(exc_substring)

    columns_to_keep = list(filter(lambda x: exc_substring not in x, df.columns))
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


def red_blue_converter(
    corner_col: str,
    comp_col: str,
) -> str:
    """Convert corner focused column into fighter focused column.

    Parameters
    ----------
    corner_col : Value of the corner.
    comp_col : Value of the column to be converted.

    Returns
    -------
    Corrected column value.
    """
    if comp_col == corner_col:
        fixed_col = 1
    elif comp_col not in [np.NaN, 'neither']:
        fixed_col = 0
    else:
        fixed_col = comp_col

    return fixed_col


def standardise_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Set date to datetime since where else are you going to do that, standardise the columns containing Red / Blue
    values into something more useful.

    Parameters
    ----------
    df : Input df.

    Returns
    -------
    Fixed column version of input df.
    """
    df['date'] = pd.to_datetime(df['date'])
    df['Winner'] = df.apply(lambda x: red_blue_converter(x.corner, x.Winner), axis=1)
    df['better_rank'] = df.apply(lambda x: red_blue_converter(x.corner, x.better_rank), axis=1)

    df.loc[df.finish_details.isin(['Red', 'Blue', 'neither']), 'finish_details'] = np.NaN  # scrub the filth!

    return df


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
    df = standardise_cols(df)

    return df


def json_to_dict(filepath: str) -> Dict[str, object]:
    """Read in json data as dictionary.

    Parameters
    ----------
    filepath : path to json data.

    Returns
    -------
    JSON data as a python dictionary, as i cant be arsed to rewrite the same two lines of code over and over.
    """
    with open(filepath) as json_file:
        data_dict = json.load(json_file)

    return data_dict


def get_proper_nouns(input_string: str) -> str:
    """Pull proper nouns (other than the word flag because nah mate to that) from an input string.

    Parameters
    ----------
    input_string : some string containing some proper nouns.

    Notes
    -----
    Function returns strictly the alphabetic characters of the input string so for instance 'John123' would return only
    'John'. This is also true for special characters i.e. 'Suflé' would yield 'Sufl'. This is fine for our purposes as
    my web scrapers already unidecode the strings they scrape to avoid issues such as this but for data not coming from
    my own scrapers, unidecode-ing the input string first would be strongly recommended.

    Returns
    -------
    Whitespace separated proper nouns from the input string.
    """
    input_string = input_string.replace('Flag of', '')
    proper_nouns = re.findall('([A-Z][a-z]*)', input_string)
    proper_nouns = ' '.join(proper_nouns)

    if proper_nouns[-1] == 'C':
        proper_nouns = proper_nouns[:-2]  # remove annoying capital C in fighter name for current champs

    return proper_nouns


def split_string_list(variables_string: str) -> List[str]:
    """Transform the input lists into something usable.

    Parameters
    ----------
    variables_string : A single string with a bunch of flag file names in.

    Returns
    -------
    An ordered list of variables.
    """
    variables_string = variables_string.split(',')
    variable_list = list(map(get_proper_nouns, variables_string))

    return variable_list


def create_nationality_df() -> pd.DataFrame:
    """Transform raw scraped wikipedia fighter nationality json data into a usable pandas df.

    Returns
    -------
    Pandas dataframe of per fighter nationality.
    """
    nationalities_dict = json_to_dict('data/wikipedia-nationalities.json')

    nationalities_dict['country_of_origin'] = split_string_list(nationalities_dict['country_of_origin'][0])
    nationalities_dict['fighter'] = split_string_list(nationalities_dict['fighter'][0])

    nationalities_df = pd.DataFrame.from_dict(nationalities_dict)
    nationalities_df = nationalities_df.groupby(['fighter']).first().reset_index()

    return nationalities_df


def create_gym_dict() -> Dict[str, List[str]]:
    """Transform raw scraped wikipedia gym json data into a usable pandas df.

    Notes
    -----
    I delete the 'coaches' data since it required cleaning, would still eb a list per fighter, would only be filled for
    some fighters and, prehaps most importantly, the coaches are per gym meaning they don't really add any extra info
    compared to just the camp itself. I delete 'previous_fighters' for now as it gets in the way but may come back and
    reinstate it at some point as there's really not reason to other than convenience.

    Returns
    -------
    Pandas dataframe of per fighter gyms.
    """
    gyms_dict = json_to_dict('data/wikipedia-camps.json')
    del gyms_dict['coaches']
    del gyms_dict['previous_fighters']

    gyms_dict['camp_location'] = gyms_dict['camp_location'][0].split(' , ')
    gyms_dict['camp_country'] = [re.sub(r'[^a-zA-Z ]+', '', loc.split(', ')[-1]) for loc in gyms_dict['camp_location']]
    gyms_dict['camp_city'] = [loc.split(',')[0] for loc in gyms_dict['camp_location']]
    del gyms_dict['camp_location']

    gyms_dict['camp'] = gyms_dict['camp'][0].split(', ')
    gyms_dict['camp'] = [re.sub(r'[^a-zA-Z ]+', '', camp) for camp in gyms_dict['camp']]

    gyms_dict['current_fighters'] = gyms_dict['current_fighters'][0].split(', ')

    return gyms_dict


def fighters_in_list(
        fighters_list: List[str],
        input_fighters: str,
) -> List[str]:
    """Replace an input string with a list of every fighters name contained in that string.

    Parameters
    ----------
    fighters_list : List of all fighters from nationality_df, which is hopefully all the fighters?
    input_fighters : String of fighters names which are sometimes not separated by whitespace but sometimes are.

    Returns
    -------
    List of all fighters from nationality_df that were mentioned in input_fighters
    """
    return [fighter for fighter in fighters_list if fighter in input_fighters]


def create_gyms_df(fighters_list: List[str]) -> pd.DataFrame:
    """Read in gym data as dict then transform into exploded pandas df, using a list of known fighters to extract the
    relevant values.

    Notes
    -----
    We take the first gym a fighter appears in to be truth to avoid duplication of rows. This may not strictly
    speaking be the most useful way to construct the data, but short term it allows us to build the data into a testable
    state. This might be something to revise in future...

    Parameters
    ----------
    fighters_list : A comprehensive list of all known fighters to compare against.

    Returns
    -------
    A dataframe containing a list of all current fighters at each major MMA gym according to wikipedia.
    """
    gyms_dict = create_gym_dict()

    gyms_dict['fighter'] = [
        fighters_in_list(fighters_list, gym_fighters) for gym_fighters in gyms_dict['current_fighters']
    ]
    del gyms_dict['current_fighters']
    gyms_df = pd.DataFrame.from_dict(gyms_dict)
    gyms_df = gyms_df.explode('fighter')
    gyms_df = gyms_df.groupby(['fighter']).first().reset_index()

    return gyms_df


def create_disciplines_df() -> pd.DataFrame:
    """Read it in and clean it up mucky pup.

    Returns
    -------
    One clean discipline df goddamnit.
    """
    disciplines_df = pd.read_csv('data/disciplines_breakdown.csv')

    disciplines_df['primary_discipline'] = disciplines_df['primary_discipline'].fillna('mixed')
    disciplines_df.fillna(0, inplace=True)

    return disciplines_df


def complete_fighter_df() -> pd.DataFrame:
    """Bring together the wikipedia bonus data and the master data into a single dataframe.

    Returns
    -------
    Dataframe containing gym and nationality data per fighter.
    """
    nationality_df = create_nationality_df()
    per_fighter_df = create_per_fighter_df()
    fighters_list = list(per_fighter_df['fighter'].unique())
    gyms_df = create_gyms_df(fighters_list)
    disciplines_df = create_disciplines_df()

    df_list = [per_fighter_df, nationality_df, gyms_df, disciplines_df]
    complete_df = reduce(lambda left, right: pd.merge(left, right, on='fighter', how='left'), df_list)

    return complete_df


if __name__ == '__main__':
    fighter_df = complete_fighter_df()
    fighter_df.to_csv('data/complete_per_fighter.csv', index=False)
    print('Created per fighter df successfully!')
