from datetime import datetime
import pandas as pd

import json
from tqdm import tqdm
tqdm.pandas()
import pickle
from googletrans import Translator
from icecream import ic
import aiohttp
import asyncio
import time

"""def parseArctilcesNumbers(pages,query):
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
    return articles"""


async def fetch_articles(session, url, page, query):
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/76.0',"Origin":
        'https://ieeexplore.ieee.org'}
    data = {
        "queryText": f"{query}",
        "highlight": True,
        "returnFacets": ["ALL"],
        "returnType": "SEARCH",
        "matchPubs": True,
        "pageNumber": str(page)
    }
    async with session.post(url, json=data,headers=headers) as response:
        return await response.json()
async def parseArctilcesNumbers(pages, query):
    articles = []
    url = 'https://ieeexplore.ieee.org/rest/search/'

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_articles(session, url, page, query) for page in range(pages)]
        results = await asyncio.gather(*tasks)
        for res in results:
            for record in res.get('records', []):
                articles.append(record.get('articleNumber'))

    return articles

async def fetch_article(session,id):
    try:
        async with session.get(f'https://ieeexplore.ieee.org/document/{int(id)}', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/76.0'}) as response:
            response_text= await response.text()
            xpl_index_start = response_text.index('xplGlobal.document.metadata')
            xpl_index_end = response_text.index('"};', xpl_index_start)
            data = response_text[xpl_index_start:xpl_index_end+2]  # Including the trailing '};'
            data = data[data.index('=') + 1:]
            return json.loads(data)
    except KeyError:
        return {f'{id}': 'failed to parse'}

async def parse_ids_to_dic(ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_article(session, id) for id in ids]
        results = await asyncio.gather(*tasks)
        return results

def fill_dataframe(d,id=True,title=True,abstract=True,authors=True,publicationDate=True,year_only=True):
    df = pd.json_normalize(d)
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

async def parse(number_of_pages=1,
          save=True,tranlsate_to_rus=False,id=True,title=True,
          abstract=True,authors=True,publicationDate=True,year_only=True):

    while True:
        try:
            query = input('Type in topic ("exit" to escape): ')
            if query == 'exit':
                break
        except ValueError:
            print('error')
        else:
            break
    print(f'Parsing {number_of_pages} documents, saving is {save}, \ntranslating to rus is {tranlsate_to_rus}')
    articles = await parseArctilcesNumbers(number_of_pages, query)
    res = await parse_ids_to_dic(articles)
    df = fill_dataframe(res,id,title,abstract,authors,publicationDate,year_only)
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
pd.set_option('display.max_columns', 500)


start_time = time.time()
df=asyncio.run(parse(5,save=False))
ic(df)
print("--- %s seconds ---" % (time.time() - start_time))