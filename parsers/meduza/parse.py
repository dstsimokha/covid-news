#!/usr/bin/python

from parser import *

def parse_meduza(text):
    soup = BeautifulSoup(text, features='lxml')
    news_text_list = soup.find(name="div", attrs={'class': "GeneralMaterial-article"})

    if news_text_list:
        news_text = ''
        news_elems = news_text_list.find_all(name='p', attrs={'class': ['SimpleBlock-lead', 'SimpleBlock-p']})
        
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

if __name__ == '__main__':
    iterate(parse_meduza)
