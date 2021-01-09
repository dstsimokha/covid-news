#!/usr/bin/python

from parser_smi import *

def parse_news(text):
    soup = BeautifulSoup(text, features='lxml')
    
    news_text = ''
    lead = soup.find(name='div', attrs={'class': 'news-header__lead'})
    
    if lead:
        news_text += lead.get_text(' ', strip=True)

    news_body = soup.find(name='div', attrs={'class': 'text-content'})
    if news_body:
        news_ps = news_body.find_all(name='p')
        if news_ps:
            news_text += " " + " ".join([news_p.get_text(" ", strip=True) for news_p in news_ps])
    
    news_text = re.sub(r'[\n\r]+', ' ', news_text)

    tags_elems = soup.find_all(name="a", attrs={'class': "tags__item"})
    if tags_elems:
        tags = [re.sub(r'[\n\r]+', ' ', tag.get_text(" ", strip=True)) for tag in tags_elems]
        tags = ", ".join(tags)
    else:
        tags = ''
    
    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+', ' ', description_elem.get('content')).replace(u'\xa0', u' ') if description_elem else ''
        
    return {'news_text': news_text, 'tags': tags, 'description': description}

iterate(parse_news)
