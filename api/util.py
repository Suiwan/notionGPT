# -*- coding: utf-8 -*-
# @Author  : Zijian li
# @Time    : 2023/5/5 14:39
import time

import openai
import requests
import datetime
import os


def check_usage():
    # check openai usage
    apikey = os.getenv("OPENAI_API_KEY")
    total = 0
    total_usage = 0
    apikey = apikey
    subscription_url = "https://api.openai.com/v1/dashboard/billing/subscription"
    headers = {
        "Authorization": "Bearer " + apikey,
        "Content-Type": "application/json"
    }
    subscription_response = requests.get(subscription_url, headers=headers)
    if subscription_response.status_code == 200:
        data = subscription_response.json()
        total = data.get("hard_limit_usd")
    else:
        print(subscription_response.text)
    start_date = (datetime.datetime.now() - datetime.timedelta(days=99)).strftime("%Y-%m-%d")
    end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    billing_url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
    billing_response = requests.get(billing_url, headers=headers)
    if billing_response.status_code == 200:
        data = billing_response.json()
        total_usage = data.get("total_usage") / 100
    else:
        print(billing_response.text)
    print(f"Total: {total} USD", f"Total Usage: {total_usage} USD", f"Remaining: {total - total_usage} USD")

def get_embedding(text, model="text-embedding-ada-002", delay=1, max_retries=3):
    # 防止请求过快，限制1min内只能发送60个请求
    time.sleep(1)
    retries = 0
    while retries < max_retries:
        try:
            embed_data = openai.Embedding.create(input=text, model=model)
            return embed_data['data'][0]['embedding']
        except openai.error.APIError as error:
            # 如果出现请求过于频繁的错误，等待指定时间再尝试发送请求
            if error.status == 429:
                time.sleep(delay)
                retries += 1
                continue
            else:
                raise error
    raise Exception("Maximum number of retries exceeded.")