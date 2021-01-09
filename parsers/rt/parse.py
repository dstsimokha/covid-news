#!/usr/bin/python

def parse_rt_news(text):

    soup = BeautifulSoup(text, features='lxml')
    news_text_list = soup.find(name="div", attrs={'class': "arcticle-content"})

    if news_text_list:
        news_text = news_text_list.get_text(" ", strip=True)
        news_text = re.sub(r'[\n\r]+', ' ', news_text).replace(u'\xa0', u' ')
    else:
        news_text = ''

    description_elem = soup.find(name="meta", attrs={'name': "description"})
    description = re.sub(r'[\n\r]+', ' ', description_elem.get('content')).replace(u'\xa0', u' ') if description_elem else ''

    return {'news_text': news_text, 'description': description}

