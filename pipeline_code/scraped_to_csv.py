"""
I've scraped some additional data from wikipedia, but due to the websites rather chaotic nature some amount of post
processing is required to get it into a shape where it can be joined to the rest of the data. I wont save these to csv
alone, but rather as part of the merged master file, just to cut down on excess files and since I know if i need to
repeat the scrape that the data will need re transforming.

The camp data is both the hardest to make useful and the least useful once transformed so hurray for wasted efforts I
guess.

TODO: - write functions to transform camp data <- this one will be much harder :(
"""
import pandas as pd
import json
import re
from typing import List, Dict


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
    variable_list = [get_proper_nouns(variable) for variable in variables_string]

    return variable_list


def create_nationality_df() -> pd.DataFrame:
    """Transform raw scraped json data into a usable pandas df.

    Returns
    -------
    Pandas dataframe of per fighter nationality.
    """
    nationalities_dict = json_to_dict('data/wikipedia-nationalities.json')

    nationalities_dict['country_of_origin'] = split_string_list(nationalities_dict['country_of_origin'][0])
    nationalities_dict['fighter'] = split_string_list(nationalities_dict['fighter'][0])

    nationalities_df = pd.DataFrame.from_dict(nationalities_dict)

    return nationalities_df
