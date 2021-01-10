from scraper import *
news = Scraper('kp')
news.test_parse()
print('URL', news.url, sep='\n')
print('TITLE', news.title, sep='\n')
print('TIME', news.time, sep='\n')
print('TEXT', news.text, sep='\n')
