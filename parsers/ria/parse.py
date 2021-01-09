#!/usr/bin/python

from parser_smi import *

def parse_ria_news(text):

    soup = BeautifulSoup(resp.text, features='lxml')
    news_text_list = soup.find_all(name="div", attrs={'class': "article__text"})

    if news_text_list:
        news_text = ''
        for news in news_text_list:
            scripts = news.find_all(name="script")
            [script.decompose() for script in scripts]
            news_text += ' ' + news.get_text(" ", strip=True)

        news_text = re.sub(r'[\n\r]+', ' ', news_text)
    else:
        news_text = ''

    title_elem = soup.find(name="meta", attrs={'name': "analytics:title"})
    title = re.sub(r'[\n\r]+', ' ', title_elem.get('content')) if title_elem else ''

    tags_elem = soup.find(name="meta", attrs={'name': "analytics:tags"})
    tags = re.sub(r'[\n\r]+', ' ', tags_elem.get('content')) if tags_elem else ''
    return {'news_text': news_text, 'tags': tags, 'title': title}

iterate(parse_ria_news)
