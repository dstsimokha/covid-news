#!/usr/bin/python

from parser_smi import *

def parse_news(text):
    soup = BeautifulSoup(text, features='lxml')
    news_page = soup.find(name="div", attrs={'id': "article-content"})

    if news_page:
        news_text = ''
        news_elems = news_page.find_all(name=['p', 'li', 'dl'])
        for news_elem in news_elems:
            news_text += news_elem.get_text(" ", strip=True)
        news_text = re.sub(r'[\n\r]+', ' ', news_text).replace(u'\xa0', u' ')
    else:
        news_text = ''

    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+', ' ', description_elem.get('content')).replace(u'\xa0', u' ') if description_elem else ''
    
    tags_elem = soup.find(name="meta", attrs={'name': "keywords"})
    tags = re.sub(r'[\n\r]+', ' ', tags_elem.get('content')).replace(u'\xa0', u' ') if tags_elem else ''
    
    return {'news_text': news_text, 'tags': tags, 'description': description}

iterate(parse_news)

