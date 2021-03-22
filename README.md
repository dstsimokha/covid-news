# News Scraper
Code for the university project on scraping news for topic modelling.


## How to use
0. This code helps you to gather *title, time and text* from news without major modifications in itself.
1. Put all urls in the **sitemaps** folder in **.csv** format with **,** as newline delimeter - first line as a header named 'url', all following lines are just urls.
2. In the **settings.json** file map:
    - **css-selectors** for scraping what you want from the site
    - **cleaning techniques** for deleting html-/css-tags and any other garbage from the text
3. Set folder with this code as working directory and run `python scraper.py --test sitename url` to test previously mapped css-selectors and cleaning techniques.
4. After that run `python scraper.py sitename` for basic parsing with *requests* package or `python scraper.py --selenium sitename` for more complex parsing with *selenium* package (will silently run browser window and behaves more like a human - sometimes it helps)
5. ...
6. PROFIT
