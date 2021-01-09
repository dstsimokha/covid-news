import sys
import json
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


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

    def test_parse(self):
        self._load_urls()
        test = list(self.urls.values())[0]  # TODO: change to random element
        r = requests.get(test)
        r.status_code
        soup = BeautifulSoup(r.text, 'html.parser')
        article = self._get_news(soup)
        self.title = article['title']
        self.time = article['time']
        self.text = article['text']


if __name__ == '__main__':
    news = Scraper(sys.argv[1])
    news.parse()
