"""
acquire required datasets for dashboard construction. need to test if this logging implementation works hahaha. it might
not. it probably wont. but there is always a chance that it will...

TODO: - write code to automate construction of disciplines dataset?
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
from pipeline_code.logger_module import get_pipeline_logger


logger = get_pipeline_logger(__name__, filename=time.strftime('%d%m%y_%H%M%S'))


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
            logger.info('requesting URL {}'.format(url))
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
                    ('fighter', '(//table[position() > 7]/tbody/tr)/td[2]', 'text')]  # this should be simplified lad

    @staticmethod
    def element_to_attribute(
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

        logger.debug('checking elements for attribute {}'.format(attribute))

        for element in element_list:
            try:
                soup = BeautifulSoup(element, 'html.parser')
                if attribute == 'text':
                    attribute_list.append(soup.get_text())
                else:
                    attr = soup.find()[attribute]
                    attribute_list.append(attr)
            except Exception as e:
                logger.warning('FAILURE - {}'.format(e))
                attribute_list.append('')

        logger.debug('found {} of the desired attribute in the supplied elements'.format(len(attribute_list)))

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

    @staticmethod
    def clean_scraped_data(
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

        logger.info('Cleaning scraped data...')

        for key in data_dict.keys():
            try:
                data_dict[key] = [val.replace('£', '') for val in data_dict[key]]
                data_dict[key] = [unidecode(val) for val in data_dict[key]]
                data_dict[key] = [val.lstrip().rstrip() for val in data_dict[key]]
                data_dict[key] = [' '.join(val.split()) for val in data_dict[key]]
            except TypeError:
                logger.warning('FAILURE - cannot clean non obj data types!')

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
        logger.info('beginning scrape of URL {}'.format(response.url))
        target_xpaths = self.get_xpath_lists(response)
        scraped_data = self.scrape_multiple_to_attribute(response, target_xpaths)
        scraped_data = self.clean_scraped_data(scraped_data)

        with open('data/{}.json'.format(self.name), 'w', encoding='utf8') as fp:
            json.dump(scraped_data, fp, sort_keys=True, indent=4, ensure_ascii=False)
        logger.debug('saved scrape output to local json file')


def scrape_wikipedia_data() -> None:
    """Run scrapes for wikipedia fight data, and saves the output as jsons in the data folder.

    Notes
    -----
    Instantiates twisted reactor, and closes the reactor down at the end of the process. As such no further use of
    twisted will be allowed in the process after this point.
    """
    logger.info('beginning scrapy process')
    process = CrawlerProcess()
    process.crawl(WikipediaSpider)
    process.start()
    logger.info('scrape complete, disabling twisted reactor...')


def get_most_recent_kaggle() -> None:
    """Uses kaggles' api to download the most recent data to the data folder.
    """
    api = KaggleApi()
    api.authenticate()

    logger.info('requesting most recent data from kaggle API...')
    api.dataset_download_files('mdabbert/ultimate-ufc-dataset', path='data/', unzip=True)


def acquire_data_main() -> None:
    """Run data acquisition functions.
    """
    get_most_recent_kaggle()
    scrape_wikipedia_data()


if __name__ == '__main__':
    acquire_data_main()
