import sys
from datetime import datetime
import pandas as pd
import requests
import json
from tqdm import tqdm
tqdm.pandas()
import pickle
from googletrans import Translator
from icecream import ic
def parseArctilcesNumbers(pages,query):
    articles = []
    #in page there is 25 docs
    for j in tqdm(range(0,pages),desc='Parsing article ids',unit='page'):
        res = requests.post(url='https://ieeexplore.ieee.org/rest/search/', headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/76.0',"Origin":
        'https://ieeexplore.ieee.org'},
                            json={"queryText": f"{query}", "highlight": True, "returnFacets": ["ALL"],
                                  "returnType": "SEARCH", "matchPubs": True, "pageNumber":str(j)})
        res_json=json.loads(res.text)
        for i in range(len(res_json['records'])):
            articles.append(res_json['records'][i]['articleNumber'])
    return articles
def parse_ids_to_dic(ids):
    data=[]
    for id in tqdm(ids,desc='Parsing articles',unit='article'):
        try:
            arctile = requests.get(url=f'https://ieeexplore.ieee.org/document/{int(id)}', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/76.0'})
            #конечно смешно, но обычный парс не работает, вроде не хочет заходить за какой то там элемент,
            #не помню как называется
            xpl_index_start=arctile.text.index('xplGlobal.document.metadata')
            xpl_index_end=arctile.text.index('"};',xpl_index_start)
            str=''
            for i in range(xpl_index_start,xpl_index_end):
                str+=arctile.text[i]
            str = str[str.index('=') + 1:]+'"}'
            dic=json.loads(str)
            data.append(dic)
        except KeyError:
            data.append({f'{id}':'failed to parse'})
    return data
def fill_dataframe(d,id=True,title=True,abstract=True,authors=True,publicationDate=True,year_only=True):
    df = pd.DataFrame(d)
    columns_to_get = []
    if id:
        columns_to_get.append('articleId')
    if title:
        columns_to_get.append('title')
    if abstract:
        columns_to_get.append('abstract')
    if authors:
        columns_to_get.append('authorNames')
    if publicationDate:
        columns_to_get.append('publicationDate')
        df['publicationDate'] = df['publicationDate'].apply(format_date)
        if year_only:
            df['publicationDate'] = pd.DatetimeIndex(df['publicationDate']).year.astype('Int64')
    df = df[columns_to_get]
    return df
def format_date(text):
    date_formats=('%d %B %Y','%B %Y', '%Y')
    for fmt in date_formats:
        try:
            return datetime.strptime(text,fmt)
        except ValueError:
            pass
        except TypeError:
            pass
    return None

def parse(number_of_pages=1,
          save=True,tranlsate_to_rus=False,id=True,title=True,
          abstract=True,authors=True,publicationDate=True,year_only=True):
    while True:
        try:
            query = input('Type in topic ("exit" to escape): ')
            if query == 'exit':
                break
        except OSError:
            print('error')
        else:
            break
    all_ids = parseArctilcesNumbers(number_of_pages,query)
    d = parse_ids_to_dic(all_ids)
    df = fill_dataframe(d,id,title,abstract,authors,publicationDate,year_only)
    if tranlsate_to_rus:
        trans = Translator()
        if title:
            print('\nTranslating titles')
            df['title'] = df['title'].progress_apply(lambda x: trans.translate(x, src='en', dest='ru').text)
        if abstract:
            print('\nTranslating abstracts')
            df['abstract'] = df['abstract'].progress_apply(lambda x: trans.translate(x, src='en', dest='ru').text)

    if save:
        while True:
            try:
                path = input("Path to save file (w/o .pickle): ")
                if path == 'exit':
                    break
                with open(path + '.pickle', 'wb') as f:
                    pickle.dump(df, f)
                    break  # добавляем break, чтобы выйти из цикла после успешного сохранения
            except OSError:
                choice = input(
                    'Non existing path. Type in "exit" to escape, '
                    'or press Enter to type in path again: ')
                if choice == 'exit':
                    break
                continue

    return df

df=parse(5,save=False)
ic(df)

