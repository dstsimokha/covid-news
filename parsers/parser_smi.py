#!/usr/bin/python

import pandas as pd
import re
import json
import requests as req
import time
import glob
import csv
import tqdm
import pytz
import os
import numpy as np
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}

def order_dict(dic, lst):
    index_map = {v: i for i, v in enumerate(lst)}
    return dict(sorted(dic.items(), key=lambda pair: index_map[pair[0]]))

def iterate(parse_func, df_filename=None, csv_filename=None):

    # Inferring filenames
    if not df_filename:
        df_filename = glob.glob('db/*.json')[0]
        
    if not csv_filename:
        csv_files_list = glob.glob('db/*.csv')
        if csv_files_list:
            csv_filename = csv_files_list[0]
            df_csv = pd.read_csv(csv_filename, index_col=0)
            csv_file_empty = os.stat(csv_filename).st_size == 0
            col_order = np.concatenate(([df_csv.index.name], df_csv.columns.values)).tolist()
        else:
            csv_filename = re.sub(r'\..*?$', '', os.path.dirname(df_filename) + os.path.sep + os.path.basename(df_filename)) + '.csv'
            df_csv = pd.DataFrame()
            csv_file_empty = True
            col_order = False
    else:
        df_csv = pd.read_csv(csv_filename, index_col=0)
        col_order = np.concatenate(([df_csv.index.name], df_csv.columns.values)).tolist()
   
    
    # Loading data
    df = pd.read_json(df_filename)
    
    # Processing indices
    csv_urls = df_csv.url if df_csv.size > 0 else df_csv
    urls_to_parse = set(np.setdiff1d(df.url, csv_urls, assume_unique=True))

    # Nothing to do
    if not urls_to_parse:
        return False

    # Init
    csv_rows = []
    csv_keys = ''
    
    # Begin
    for url in tqdm.tqdm(urls_to_parse):
        
        item = df.loc[df.url == url].iloc[0]
        attempt = 0        
        while attempt < 5:
            try:
                
                # Processing row from db
                csv_row = {'news_id': item.name}
                csv_row.update(item.to_dict())
                start = time.time()
                
                # Downloading file
                resp = req.get(csv_row['url'], headers=headers)

                if resp.status_code == 200:
                    csv_row.update(parse_func(resp.content))
                    csv_rows.append(csv_row)
                    if not col_order:
                        col_order = list(csv_row.keys())
                    if not csv_keys:
                        csv_keys = list(csv_row.keys())

                    # Saving progress
                    if len(csv_rows) > 1000:

                        # Saving row to csv file
                        with open(csv_filename, 'a', encoding='utf-8') as csv_file:
                            writer = csv.DictWriter(csv_file, col_order)
                            if csv_file_empty:
                                writer.writeheader()
                                csv_file_empty = False
                            
                            for csv_row in csv_rows:
                                writer.writerow(csv_row)

                        csv_rows = []
                    
                    # Calculating wait time (must be 1 sec minimum!)
                    end = time.time()
                    wait = max(0, 1.1 - (end - start))
                    time.sleep(wait)
                    break

                elif resp.status_code >= 300:
                    print('Error:', csv_row['url'])
                    with open('errors.log', 'a') as error_file:
                        error_file.write(csv_row['url'] + os.linesep)
                    break

            except Exception as e:
                print(e)
                attempt += 1
                continue
        
    # Saving rows to csv file
    with open(csv_filename, 'a', encoding='utf-8') as csv_file:
        if len(csv_rows) > 0:
            writer = csv.DictWriter(csv_file, col_order)
            if csv_file_empty:
                writer.writeheader()

            for csv_row in csv_rows:
                writer.writerow(csv_row)


    return True
