import os
import csv
import sys
import json
import time
import requests
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
    def wrapped(*args, **kwargs):
        delay = np.random.choice([3, 5, 7, 9])
        time.sleep(delay)
        return func(*args, **kwargs)
    return wrapped


class Scraper:
    """
    Helps to parse news from chosen source
    """

    def __init__(self, site, options):
        """
        Just pass a site name
        """
        self.options = opts
        self.site = site
        self.sitemap = f'sitemaps/news_{site}.json'
        self.fieldnames = ['url', 'time', 'title', 'text']
        with open('settings.json') as f:
            site = json.load(f)[self.site]
            self.css_selectors = site['css']
            self.cleaning_tools = site['clean']

    def _load_urls(self):
        """
        Sitemap's urls compared to already scraped ones
        Parsing only new ones
        """
        with open(self.sitemap) as f:
            all_urls = json.load(f)['url']
            all_urls = list(all_urls.values())
        with open(f'news/{self.site}.csv', 'r') as f:
            lines = f.readlines()
            parsed_urls = [line.split(',')[0] for line in lines]
        print('Check remaining URLs:')
        self.urls = [url for url in tqdm(all_urls) if url not in parsed_urls]

    def _clean_article(self, name, block):
        """
        Apply cleaning techniques per specific article block
        from settings.json
        """
        return eval(self.cleaning_tools[name])

    def _get_article(self, soup):
        """
        Get article block by CSS selector
        """
        if '--test' in self.options:
            print(soup.select(self.css_selectors['time']))
            print(soup.select(self.css_selectors['title']))
            print(soup.select(self.css_selectors['text']))
        article = {
            'time': self._clean_article(
                'time', soup.select(self.css_selectors['time'])),
            'title': self._clean_article(
                'title', soup.select(self.css_selectors['title'])),
            'text': self._clean_article(
                'text', soup.select(self.css_selectors['text']))
        }
        return article

    def _save_article(self, article):
        """
        Write article to .csv database
        """
        with open(f'news/{self.site}.csv', 'a') as f:
            writer = csv.DictWriter(f, self.fieldnames)
            writer.writerow(article)

    def _create_csv(self):
        """
        Create .csv database in it's not exists
        """
        if os.path.exists(f'news/{self.site}.csv'):
            pass
        else:
            with open(f'news/{self.site}.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, self.fieldnames)
                writer.writeheader()

    @delayer
    def _get_html(self, url):
        r = requests.get(url, headers=headers)
        return r

    def _parse(self, url):
        """
        True parsing function:
            - get html
            - check status code
            - parse text
            - construct article
            - save article to .csv
        """
        try:
            r = self._get_html(url)
            article = {'url': url}
            soup = BeautifulSoup(r.text, 'html.parser')
            content = self._get_article(soup)
            article.update(content)
            self._save_article(article)
        except IndexError:
            pass

    def parallel_parse(self):
        """
        For quicker parsing using all CPUs
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

    def test_parse(self):
        self._create_csv()
        self._load_urls()
        self.url = self.urls[0]
        print('URL', self.url)
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        article = self._get_article(soup)
        self.title = article['title']
        print('TITLE', self.title)
        self.time = article['time']
        print('TIME', self.time)
        self.text = article['text']
        print('TEXT', self.text)


if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    for site in args:
        news = Scraper(site, opts)
    news.test_parse() if '--test' in opts else news.parallel_parse()
# TODO: novaya, tass, russia_today
