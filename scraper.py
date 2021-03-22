import os
import csv
import sys
import json
import time
import requests
import selenium
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium import webdriver
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from joblib import Parallel, delayed, parallel_backend

headers = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) ' +
                      'Gecko/20100101 Firefox/84.0',
        'referrer': 'https://yandex.ru',
    }


def delayer(func):
    """
    To not get banned from some sites - just waits for ~ a second
    """
    def wrapped(*args, **kwargs):
        delay = np.random.choice([0.5, 1, 2])
        time.sleep(delay)
        return func(*args, **kwargs)
    return wrapped


class Scraper:
    """
    Helps to parse news from chosen source
    """

    def __init__(self, sitename):
        """
        - takes <sitename> as input
        - then reads urls from *sitemaps* folder
          from the file *news_<sitename>.csv*
        - then reads css-selectors and cleaning
          techniques from *settings.json* looking
          for the <sitename> key
        """
        self.site = sitename
        self.sitemap = f'sitemaps/news_{self.site}.csv'
        self.newsfile = f'news/{self.site}.csv'
        self.fieldnames = ['url', 'time', 'title', 'text']
        with open('settings.json') as f:
            site = json.load(f)[self.site]
            self.css_selectors = site['css']
            self.cleaning_tools = site['clean']

    def _create_csv(self):
        """
        Creates .csv file for new news (lol) if it's not exists
        """
        if not os.path.exists(self.newsfile):
            with open(self.newsfile, 'w', newline='') as f:
                writer = csv.DictWriter(f, self.fieldnames)
                writer.writeheader()

    def _load_urls(self):
        """
        Checking already parsed urls
        Leaves only non-gathered ones
        """
        all_urls = list()
        with open(self.sitemap) as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                all_urls.append(row[0])
        with open(f'news/{self.site}.csv', 'r') as f:
            lines = f.readlines()
            parsed_urls = [line.split(',')[0] for line in lines]
        print('Check remaining URLs:')
        self.urls = [url for url in tqdm(all_urls) if url not in parsed_urls]

    def _clean_article(self, name, block):
        """
        Apply cleaning techniques per specific
        article block from settings.json
        """
        return eval(self.cleaning_tools[name])

    def _get_article(self, soup):
        """
        Get article blocks by their css-selectors
        Clean derived text with chosen techniques
        """
        article = {
            'title': self._clean_article(
                'title', soup.find_all(*self.css_selectors['title'])),
            'time': self._clean_article(
                'time', soup.find_all(*self.css_selectors['time'])),
            'text': self._clean_article(
                'text', soup.find_all(*self.css_selectors['text']))
        }
        return article

    def _save_article(self, article):
        """
        Write article to .csv file
        """
        with open(self.newsfile, 'a') as f:
            writer = csv.DictWriter(f, self.fieldnames)
            writer.writerow(article)

    @delayer
    def _get_html(self, url):
        """
        Get sitepage with requests package
        """
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)

        session.mount('http://', adapter)
        session.mount('https://', adapter)

        r = session.get(url, headers=headers)
        return r

    def _parse(self, url):
        """
        Inner parsing func:
        - get html
        - check status code
        - parse text
        - construct article
        - save article to .csv file
        """
        try:
            r = self._get_html(url)
            article = {'url': url}
            soup = BeautifulSoup(r.text, 'html.parser')
            content = self._get_article(soup)
            article.update(content)
            self._save_article(article)
        except (IndexError, requests.exceptions.ConnectionError):
            pass

    def parallel_parse(self):
        """
        Outer parallel parsing func to run inner parsing func
        For quicker parsing using all CPUs (*cores go brrrr*)
        """
        self._create_csv()
        self._load_urls()
        print('Parse URLs:')
        try:
            with parallel_backend("loky", n_jobs=-1):
                with Parallel(verbose=0) as parallel:
                    parallel(delayed(self._parse)(url)
                             for url in tqdm(self.urls))
        finally:
            # important to delete parallel workers to free ram
            del parallel

    def selenium_parse(self):
        """
        All-in-one selenium parsing func
        For those sources which can not be parsed by requests package
        """
        self._create_csv()
        self._load_urls()
        print('Parse URLs:')
        # Running 'headless' (silent) Firefox browser window to save RAM
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        for url in tqdm(self.urls):
            try:
                driver.get(url)
                article = {'url': url}
                title = driver.find_element_by_tag_name(
                    self.css_selectors['title']).text
                time = driver.find_element_by_tag_name(
                    self.css_selectors['time']).text
                text = driver.find_elements_by_tag_name(
                    self.css_selectors['text'])
                content = {
                    'title': self._clean_article('title', title),
                    'time': self._clean_article('time', time),
                    'text': self._clean_article('text', text)
                    }
                article.update(content)
                self._save_article(article)
            except selenium.common.exceptions.NoSuchElementException:
                pass

    def test_parse(self, url):
        """
        For testing purposes:
        - takes one url for parse with requests package
          and check chosen css-selectors and cleaning techniques
        """
        self.url = url
        print(self.url)
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Print before cleaning
        print(soup.find_all(*self.css_selectors['title']))
        print(soup.find_all(*self.css_selectors['time']))
        print(soup.find_all(*self.css_selectors['text']))
        article = self._get_article(soup)
        # Print after cleaning
        self.title = article['title']
        print('TITLE', self.title)
        self.time = article['time']
        print('TIME', self.time)
        self.text = article['text']
        print('TEXT', self.text)


if __name__ == '__main__':
    # reading options as '--test'
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    # reading arguments as 'sitename'
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    news = Scraper(args[0])
    if '--test' in opts:
        print('Testing url.')
        news.test_parse(args[1])
    elif '--selenium' in opts:
        print('Parsing with selenium.')
        news.selenium_parse()
    else:
        print('Usial parsing.')
        news.parallel_parse()


# https://www.crummy.com/software/BeautifulSoup/bs4/doc.ru/bs4ru
# https://www.pluralsight.com/guides/web-scraping-with-beautiful-soup
# https://selenium-python.readthedocs.io/
