# -*- coding: utf-8 -*-
# @Author  : Zijian li
# @Time    : 2023/5/5 14:28
import requests
import os

auth_token = os.getenv("auth_token")


def getDataBaseContent(database_id: str):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    payload = {"page_size": 100}
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "Authorization": f"{auth_token}"
    }

    response = requests.post(url, json=payload, headers=headers)

    result = response.json()
    return result


def getPageText(result):
    from collections import defaultdict
    import re
    from tqdm import tqdm

    page_get_headers =  {'Authorization': f'Bearer {auth_token}',
                                  'Notion-Version': '2022-06-28'}

    data_dict = defaultdict(dict)

    for res in tqdm(result['results']):
        title = res['properties']['Name']['title'][0]['plain_text']
        page_id = res['id']
        page_url = res['url']
        # get page content
        url = f'https://api.notion.com/v1/blocks/{page_id}/children'
        response = requests.get(url, headers=page_get_headers)
        json_data = response.json()
        json_str = str(json_data)
        text_list = re.findall(r'plain_text\': \'(.*?)\'', json_str)
        text_content = ' '.join(text_list)
        data_dict[title]['page_id'] = page_id
        data_dict[title]['page_url'] = page_url
        data_dict[title]['text_content'] = text_content

    return data_dict


def convert2csv(data_dict):
    # convert to dataframe
    import pandas as pd

    df = pd.DataFrame.from_dict(data_dict, orient='index')
    df.reset_index(inplace=True)

    df.columns = ['title', 'page_id', 'page_url', 'text_content']
    df.to_csv('notion_data.csv')


result = getDataBaseContent()

data_dict = getPageText()

convert2csv(data_dict)
