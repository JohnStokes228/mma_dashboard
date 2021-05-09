"""
acquire required datasets for dashboard construction.

TODO: - move existing web scraping code into this file to scrape wikipedia with for peripheral datasets, but only the
      mvp. don't want to port the whole scraping project over that's too complicated really...
      - write code to automate construction of disciplines dataset?
"""
from kaggle.api.kaggle_api_extended import KaggleApi
import scrapy
from typing import Generator, List, Tuple, Dict, Any
import time
import random
from bs4 import BeautifulSoup
from unidecode import unidecode
import json
from scrapy.crawler import CrawlerProcess


class WikipediaSpider(scrapy.Spider):

    name = 'wikipedia_scraper'
    start_urls = ['https://en.wikipedia.org/wiki/List_of_professional_MMA_training_camps',
                  'https://en.wikipedia.org/wiki/List_of_current_UFC_fighters']

    def start_requests(self) -> Generator[str, None, None]:
        """Send request to each start url and pass the response to the parse method of the spider.
        """
        meta = {'dont_redirect': True,
                'handle_httpstatus_list': [301, 302]}

        for url in self.start_urls:
            yield scrapy.Request(url=url, meta=meta, callback=self.parse)

    def get_xpath_lists(
        self,
        response: scrapy.http.Response,
    ) -> List[Tuple[str, str, str]]:
        """Figure out which xpaths to scrape based on input url.

        Parameters
        ----------
        response : Response to scrapys request for html.

        Returns
        -------
        List of tuples of desired variable names, xpaths and attributes.
        """
        if 'camps' in response.url:
            self.name = 'wikipedia-camps'
            return [('camp', '//table[@class="wikitable"]/tbody/tr/td[1]', 'text'),
                    ('coaches', '//table[@class="wikitable"]/tbody/tr/td[2]', 'text'),
                    ('current_fighters', '//table[@class="wikitable"]/tbody/tr/td[3]', 'text'),
                    ('previous_fighters', '//table[@class="wikitable"]/tbody/tr/td[4]', 'text'),
                    ('camp_location', '//table[@class="wikitable"]/tbody/tr/td[5]', 'text')]
        else:
            self.name = 'wikipedia-nationalities'
            return [('country_of_origin', '//table[position() > 7]/tbody/tr/td/img', 'alt'),
                    ('fighter', '(//table[position() > 7]/tbody/tr)/td[2]', 'text')]

    def element_to_attribute(
        self,
        element_list: List[str],
        attribute: str,
    ) -> List[str]:
        """Use BeautifulSoup to parse html requested from site.

        Parameters
        ----------
        element_list : Input list of str's, in form of html.
        attribute : Desired attribute to pull from each element.

        Returns
        -------
        List of desired attributes pulled from html.
        """
        attribute_list = []

        for element in element_list:
            soup = BeautifulSoup(element, 'html.parser')
            if attribute == 'text':
                attribute_list.append(soup.get_text())
            else:
                attr = soup.find()[attribute]
                attribute_list.append(attr)

        return attribute_list

    def scrape_multiple_to_attribute(
        self,
        response: scrapy.http.Response,
        list_of_tuples: List[Tuple[str, str, str]],
    ) -> Dict[str, List[str]]:
        """Scrape a list of target xpaths / attributes into a dictionary.

        Parameters
        ----------
        response : Response to scrapys' request for the web url.
        list_of_tuples: List of tuples of form (var_name, target_path, attribute).

        Returns
        -------
        Dictionary of chosen attributes, whose keys are the var_names from the tuples.
        """
        output_dict = {}

        for input_tuple in list_of_tuples:
            time.sleep(random.uniform(2, 5))
            element_list = response.xpath(input_tuple[1]).extract()
            attribute_list = self.element_to_attribute(element_list, input_tuple[2])
            output_dict[input_tuple[0]] = attribute_list

        return output_dict

    def clean_scraped_data(
        self,
        data_dict: Dict[str, List[str]],
    ) -> Dict[str, str]:
        """Cleans the values in input dict by:
            - removing £ sign to avoid it getting decoded
            - replace special characters with closest latin characters
            - l and r stripping
            - removing multiple whitespaces
            - removing line breaks and tabs

        Parameters
        ----------
        data_dict : Dictionary containing list of string data.

        Returns
        -------
        Input dictionary whose values were cleaned via the above described method.
        """
        for key in data_dict.keys():
            data_dict[key] = [val.replace('£', '') for val in data_dict[key]]
            data_dict[key] = [unidecode(val) for val in data_dict[key]]
            data_dict[key] = [val.lstrip().rstrip() for val in data_dict[key]]
            data_dict[key] = [' '.join(val.split()) for val in data_dict[key]]

        return data_dict

    def parse(
        self,
        response: scrapy.http.Response,
        **kwargs: Any,
    ) -> None:
        """Parse the target url.

        Parameters
        ----------
        response : Response to scrapys request for the input url.
        """
        target_xpaths = self.get_xpath_lists(response)
        scraped_data = self.scrape_multiple_to_attribute(response, target_xpaths)
        scraped_data = self.clean_scraped_data(scraped_data)

        with open('data/{}.json'.format(self.name), 'w', encoding='utf8') as fp:
            json.dump(scraped_data, fp, sort_keys=True, indent=4, ensure_ascii=False)


def scrape_wikipedia_data() -> None:
    """Run scrapes for wikipedia fight data, and saves the output as jsons in the data folder.

    Notes
    -----
    Instantiates twisted reactor, and closes the reactor down at the end of the process. As such no further use of
    twisted will be allowed in the process after this point.
    """
    process = CrawlerProcess()
    process.crawl(WikipediaSpider)
    process.start()


def get_most_recent_kaggle() -> None:
    """Uses kaggles' api to download the most recent data to the data folder.
    """
    api = KaggleApi()
    api.authenticate()

    api.dataset_download_files('mdabbert/ultimate-ufc-dataset', path='data/', unzip=True)


def acquire_data_main() -> None:
    """Run data acquisition functions.
    """
    get_most_recent_kaggle()
    scrape_wikipedia_data()


if __name__ == '__main__':
    print('write some code before you test run Johnno jeez...')
