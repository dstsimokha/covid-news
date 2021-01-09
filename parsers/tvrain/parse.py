#!/usr/bin/python

from parser_smi import *

def parse_rain_news(text):
    soup = BeautifulSoup(text, features='lxml')
    
    news_text = ''
    lead = soup.find(name='div', attrs={'class': 'document-lead'})
    
    if lead:
        lead_ps = lead.find_all(name='p')
        news_text += " ".join([lead_p.get_text(" ", strip=True) for lead_p in lead_ps])
        
    article = soup.find(name="div", attrs={'class': "article-full__text"})

    if article:
        article_ps = article.find_all(name='p')
        news_text += " ".join([article_p.get_text(" ", strip=True) for article_p in article_ps])
        news_text = re.sub(r'[\n\r]+', ' ', news_text).replace(u'\xa0', u' ')
    else:
        news_text = ''

    tags_elem = soup.find(name="meta", attrs={'name': "keywords"})
    tags = re.sub(r'[\n\r]+', ' ', tags_elem.get('content')).replace(u'\xa0', u' ') if tags_elem else ''
    
    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+', ' ', description_elem.get('content')).replace(u'\xa0', u' ') if description_elem else ''
    
    return {'news_text': news_text, 'tags': tags, 'description': description}

iterate(parse_rain_news)
