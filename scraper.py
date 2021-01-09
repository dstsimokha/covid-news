import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

# TODO: create class(es) with methods for scraping, make universal app

# TODO: add css_selectors & cleaning_tools for each used site to settings.json
#       and load from there needed tools to functions


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
        with open('settings.json') as f:
            site = json.load(f)[self.site]
            self.css_selectors = site['css']
            self.cleaning_tools = site['clean']

    def _load_urls(self):
        with open(self.sitemap) as f:
            self.urls = json.load(f)['url']

    def _clean_news(self, title, time, text):
        pass

    def _get_news(self, soup):
        title = soup.select(self.css_selectors['title'])
        time = soup.select(self.css_selectors['time'])
        text = soup.select(self.css_selectors['text'])
        return {'title': title, 'time': time, 'text': text}

    def _save_news(self, news):
        with open(f'news/{self.site}.json', 'w+') as f:
            json.dump(news, f)

    def parse(self):
        self._load_urls()
        news = dict()
        for url in tqdm(self.urls.values()):
            r = requests.get(url)
            r.status_code  # Handling errors here
            soup = BeautifulSoup(r.text, 'html.parser')
            article = self._get_news(soup)
            news.update({url: article})
        self._save_news(news)


# TODO: make script executable from terminal and sys.args

news = Scraper('5tv')
news.parse()
