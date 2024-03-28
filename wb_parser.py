import os
import json
import time
import random
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from utils import remove_symbols
from fake_useragent import UserAgent

url = "https://search.wb.ru/exactmatch/ru/common/v4/search?ab_testid=reranking_5&appType=1&curr=rub&dest=-1257786&page=1&query=мастер и маргарита&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false&xsubject=381"

response = requests.get(url)
with open("test.json", "w", encoding="utf-8") as file:
    json.dump(response.json(), file, indent=4, ensure_ascii=False)
data = response.json()["data"]["products"]
for book in data:
    if book["name"].lower() == "мастер и маргарита":
        print({
            "url": f"https://www.wildberries.ru/catalog/{book['id']}/detail.aspx",
            "rating": book["reviewRating"],
            "price": float(book["salePriceU"] / 100),
        })
