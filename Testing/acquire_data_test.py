"""
Testing the functions of acquire data file. Alot of this is python built ins so might be a bit sparse.
"""
from pipeline_code.acquire_data import WikipediaSpider


def test_clean_scraped_data():
    test_spider = WikipediaSpider()
    input_value = {'test_a': ['thi £    acute (é), grave (è), circumflex (â, î or ô), tilde (ñ) '],
                   'test_b': ['youll do nuttin']}
    expected_output = {'test_a': ['thi acute (e), grave (e), circumflex (a, i or o), tilde (n)'],
                       'test_b': ['youll do nuttin']}

    assert expected_output == test_spider.clean_scraped_data(input_value)
