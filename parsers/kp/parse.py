#!/usr/bin/python

from parser_smi import *

def parse_news(text):
    soup = BeautifulSoup(text, features='lxml')
    
    news_text = ''
    news_body = soup.find(name='div', attrs={'class': 'js-mediator-article'})
    
    if news_body:
        scripts = news_body.find_all(name=['script'])
        if scripts:
            [script.decompose() for script in scripts]
        
        news_ps = news_body.find_all(name='p')
        if news_ps:
            news_text += " " + " ".join([news_p.get_text(" ", strip=True) for news_p in news_ps])
        news_text = re.sub(r'[\n\r]+', ' ', news_text)

    lastmod_elem = soup.find(name="meta", attrs={'name': "mediator_published_time"})
    lastmod = re.sub(r'[\n\r]+', ' ', lastmod_elem.get("content")) if lastmod_elem else ''
    
    tags_elem = soup.find(name="meta", attrs={'name': "keywords"})
    tags = re.sub(r'[\n\r]+', ' ', tags_elem.get("content")) if tags_elem else ''
    
    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+|<[^>]+>', ' ', description_elem.get('content')) if description_elem else ''
        
    return {'lastmod': lastmod, 'news_text': news_text, 'tags': tags, 'description': description}

iterate(parse_news)
