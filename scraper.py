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
        with open(self.sitemap) as f:
            self.urls = json.load(f)['url']

    def _clean_news(self, title, time, text):
        pass

    def _get_article(self, soup):
        """
        Removing html tags with get_text()
        Restoring Unicode spaces with replace(u'\xa0', u' ')
        For time block: remove '\n' and get only date
        """
        # TODO: move all cleaning to _clean_news()
        # Deriving title
        title = soup.select(self.css_selectors['title'])
        title = title[0].get_text().replace(u'\xa0', u' ')
        # Then time
        time = soup.select(self.css_selectors['time'])
        time = time[0].get_text().replace('\n', '').split(',')[0]
        # Finally, text
        text = soup.select(self.css_selectors['text'])
        text = ' '.join([i.get_text().replace(u'\xa0', u' ') for i in text])
        return {'time': time, 'title': title, 'text': text}

    def _save_article(self, article):
        with open(f'news/{self.site}.csv', 'a') as f:
            writer = csv.DictWriter(f, self.fieldnames)
            writer.writerow(article)

    def _create_csv(self):
        try:
            with open(f'news/{self.site}.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, self.fieldnames)
                writer.writeheader()
        except FileExistsError:
            pass

    def _parse(self, url):
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
        with parallel_backend("loky", n_jobs=-1):
            with Parallel(verbose=0) as parallel:
                parallel(delayed(self._parse)(url)
                         for url in tqdm(self.urls.values()))

    def test_parse(self):
        self._load_urls()
        test = list(self.urls.values())[0]  # TODO: change to random element
        r = requests.get(test)
        soup = BeautifulSoup(r.text, 'html.parser')
        article = self._get_news(soup)
        self.title = article['title']
        self.time = article['time']
        self.text = article['text']


if __name__ == '__main__':
    news = Scraper(sys.argv[1])
    news.parallel_parse()
