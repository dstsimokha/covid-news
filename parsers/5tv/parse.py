#!/usr/bin/python

from parser_smi import *

def parse_news(text):
    soup = BeautifulSoup(text, features='lxml')
    
    header = soup.find('p', attrs={'class': 'fsHeader'})
    news_text = header.get_text(" ", strip=True) if header else ''
    
    news_body = soup.find(name='article', attrs={'class': 'js-mediator-article'})
    if news_body:
        news_ps = news_body.find_all(name=['p', 'li'])
        if news_ps:
            news_text += " " + " ".join([news_p.get_text(" ", strip=True) for news_p in news_ps])
    news_text = re.sub(r'[\n\r]+', ' ', news_text).replace(u'\xa0', u' ')

    lastmod_elem = soup.find(name="meta", attrs={'name': "mediator_published_time"})
    lastmod = re.sub(r'[\n\r]+', ' ', lastmod_elem.get("content")) if lastmod_elem else ''
    
    tags_elem = soup.find(name="meta", attrs={'name': "news_keywords"})
    tags = re.sub(r'[\n\r]+', ' ', tags_elem.get("content")) if tags_elem else ''
    
    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+|<[^>]+>', ' ', description_elem.get('content')).replace(u'\xa0', u'') if description_elem else ''
        
    return {'lastmod': lastmod, 'news_text': news_text, 'tags': tags, 'description': description}

iterate(parse_news)
