#!/usr/bin/python

from parser_smi import *

def parse_news(text):
    soup = BeautifulSoup(text, features='lxml')
    
    news_text = ''
    news_body = soup.find(name='div', attrs={'class': 'mz-publish__wrapper'})
    
    if news_body:
        bad = news_body.find_all(name=['script', 'iframe', 'svg'])
        if bad:
            [tag.decompose() for tag in bad]
        
        news_ps = news_body.find_all(name=['p', 'h2', 'li'])
        if news_ps:
            news_text += " " + " ".join([news_p.get_text(" ", strip=True) for news_p in news_ps])
        news_text = re.sub(r'[\n\r]+', ' ', news_text)
    
    
    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+|<[^>]+>', ' ', description_elem.get('content')) if description_elem else ''
        
    return {'news_text': news_text, 'description': description}

iterate(parse_news)
