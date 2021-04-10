"""
Testing the per_fighter_pipeline functions, which tbh will likely have the biggest risk factors. especially I live in
fear of the regex for grabbing proper nouns but looks like its passing so... yeah and what.
"""
from pipeline_code.per_fighter_pipeline import (
    get_proper_nouns,
    split_string_list,
)


def test_get_proper_nouns_words():
    input_string = 'testing that John can figure out why he Is even spending his time doing such un Cool things'
    expected_output = 'John Is Cool'  # :o

    assert get_proper_nouns(input_string) == expected_output


def test_get_proper_nouns_special_chars():
    input_string = '   Andrei * is a Weird123 one'
    expected_output = 'Andrei Weird'

    assert get_proper_nouns(input_string) == expected_output


def test_get_proper_nouns_champ_shit_only():
    input_string = 'Fat Boy Slim C'
    expected_output = 'Fat Boy Slim'

    assert get_proper_nouns(input_string) == expected_output


def test_split_string_list():
    input_string = '  Test this Mother, you goddamn **23Son_Of&A*Bitch'
    expected_output = ['Test Mother', 'Son Of A Bitch']

    assert split_string_list(input_string) == expected_output
