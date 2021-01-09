# covid-news
University project on news topic modelling: comparison of pro-governmental an ani-governmental news medias agendas in the pandemic period.


## HOW TO: use for project purposes
Run all code in Python interpreter and change news media sources's name - that's all.

For all used sites CSS selectors and cleaning techniques are already described in *settings.json* and using automatically.


## HOW TO: add new site for loading
Firstly, you will need to find/gather sitemap: it needs to be in .json format and looks like {"url": {"news_id1": "news_url1", "news_id2": "news_url2", ..., "news_idN": "news_urlN"}}.

Secondly, you will need to add into **settings.json** CSS selectors for news *title*, *time* and *text* blocks - use [SelectorGadget](https://selectorgadget.com/).

Finally, you will need to add into **settings.json** cleaning techniques for news title, time and text blocks - use function **test_parse** to look at output of each block and develop cleaning technique.




## META:
- Python's virtual environment (venv) in **env**: only necessary packages were loaded and used.
- This *app* was written in Visual Studio Code: *.vscode* folder is added too
