import os
import csv
import sys
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from joblib import Parallel, delayed, parallel_backend


class Scraper:
    """
    Helps to parse news from chosen source
    """

    def __init__(self, site):
        """
        Just pass a site name
        """
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
        self.urls = [url for url in all_urls if url not in parsed_urls]

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
        # Deriving title
        title = soup.select(self.css_selectors['title'])
        title = self._clean_article('title', title)
        # Then time
        time = soup.select(self.css_selectors['time'])
        time = self._clean_article('time', time)
        # Finally, text
        text = soup.select(self.css_selectors['text'])
        text = self._clean_article('text', text)
        return {'time': time, 'title': title, 'text': text}

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
                print('kek')
                writer = csv.DictWriter(f, self.fieldnames)
                writer.writeheader()

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
            r = requests.get(url)
            if r.status_code != 200:
                raise IndexError
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
        self._load_urls()
        self._create_csv()
        try:
            with parallel_backend("loky", n_jobs=-1):
                with Parallel(verbose=0) as parallel:
                    parallel(delayed(self._parse)(url)
                             for url in tqdm(self.urls))
        except requests.exceptions.ConnectionError:
            pass
        finally:
            # important to delete parallel workers to free ram
            del parallel

    def test_parse(self):
        self._load_urls()
        test = self.urls[0]
        r = requests.get(test)
        soup = BeautifulSoup(r.text, 'html.parser')
        article = self._get_news(soup)
        self.title = article['title']
        self.time = article['time']
        self.text = article['text']


if __name__ == '__main__':
    news = Scraper(sys.argv[1])
    news.parallel_parse()
