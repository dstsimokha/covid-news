#!/usr/bin/python

from parser_smi import *

def parse_vesti_news(text):
    soup = BeautifulSoup(text, features='lxml')
    news_text_list = soup.find(name="div", attrs={'class': "js-mediator-article"})
    
    if news_text_list:
        scripts = news_text_list.find_all(name='script')
        for script in scripts:
            script.decompose()
        news_text = news_text_list.get_text(' ', strip=True)
        news_text = re.sub(r'[\n\r]+', ' ', news_text)
    else:
        news_text = ''
    
    tags_elem = soup.find(name="meta", attrs={'name': "keywords"})
    tags = re.sub(r'[\n\r]+', ' ', tags_elem.get('content')) if tags_elem else ''
    
    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+', ' ', description_elem.get('content')) if description_elem else ''

    return {'news_text': news_text, 'tags': tags, 'description': description}

iterate(parse_vesti_news)
