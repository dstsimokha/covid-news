#!/usr/bin/python

from parser_smi import *

def parse_news(text):
    soup = BeautifulSoup(text, features='lxml')
    
    news_text = ''
    sub = soup.find('h2', attrs={'class': 'b-text__subtitle'})
    if sub:
        news_text = sub.get_text(" ", strip=True)

    news_body = soup.find(name='div', attrs={'class': 'b-text__content'})
    if news_body:
        news_ps = news_body.find_all(name='p')
        if news_ps:
            news_text += " " + " ".join([news_p.get_text(" ", strip=True) for news_p in news_ps])
        news_text = re.sub(r'[\n\r]+', ' ', news_text).replace(u'\xa0', u' ')
        
    tags_elem = soup.find_all(name="a", attrs={'class': "b-tag__link"})
    tags = re.sub(r'[\n\r]+', ' ', ",".join([tag.get_text("content") for tag in tags_elem])).replace('#', '') if tags_elem else ''
    
    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+|<[^>]+>', ' ', description_elem.get('content')) if description_elem else ''
        
    return {'news_text': news_text, 'tags': tags, 'description': description}

iterate(parse_news)
