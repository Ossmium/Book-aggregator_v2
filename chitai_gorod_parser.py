import os
import json
import time
import random
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from book_aggregator.services.utils import remove_symbols
from fake_useragent import UserAgent


PROXIES = [
    {
        "https": "http://9VCVu0:CoVSb7@185.148.27.146:8000"
    },
    {
        "https": "http://9VCVu0:CoVSb7@185.148.25.35:8000"
    },
    {
        "https": "http://9VCVu0:CoVSb7@185.148.25.167:8000"
    },
]


def parser_chitai_gorod():
    count_pages = 0
    count_books = 0
    change_proxy = 0
    current_proxy = PROXIES[0]
    user_agent = UserAgent(min_percentage=0.5).random

    with open(f"response_custom.json", 'r', encoding='utf-8') as f:
        books_list = json.load(f)
    try:
        for book in books_list:
            if "chitai-gorod" not in book.keys() or book["chitai-gorod"] == []:
                if count_books % 10 == 0:
                    current_proxy = random.choice(PROXIES)
                    change_proxy += 1
                    user_agent = UserAgent(min_percentage=0.5).random
                url = f"https://www.chitai-gorod.ru/search?phrase={book['book_name']}&page=1&filters%5Bcategories%5D=18030"
                response = requests.get(url, proxies=current_proxy, headers={
                                        'User-Agent': user_agent}, stream=True)
                soup = BeautifulSoup(response.text, "lxml")
                books_response = soup.find_all(
                    "article", class_="product-card product-card product")
                books_suitable = []
                for book_response in books_response:
                    name = book_response.find(
                        "div", class_="product-title__head").text.strip()
                    # print(name)
                    rating = 0.0
                    link = ""
                    price = 0
                    if remove_symbols(book['book_name']) == remove_symbols(name):
                        link = f"https://www.chitai-gorod.ru{book_response.find('a', class_='product-card__picture product-card__row').get('href')}"
                        price = book_response.find(
                            "div", class_="product-price__value")
                        if price:
                            price = float(price.text.strip().replace(
                                '\xa0', '').split(' ')[0])
                        else:
                            price = "Нет в продаже"
                        if not book_response.find("div", class_="no-rating"):
                            rating = float(book_response.find("div", class_="star-rating__statistics").find("span",
                                                                                                            itemprop="ratingValue").text)
                    else:
                        continue
                    books_suitable.append({
                        "rating": rating,
                        "url": link,
                        "price": price,
                    })
                book["chitai-gorod"] = books_suitable
                time.sleep(random.uniform(0.5, 1))
            count_books += 1
            if count_books % 25 == 0:
                print(f"[+] Обработано {count_books}")
    except Exception as ex:
        print("Исключение", ex)
        # with open("response_custom.json", 'w', encoding='utf-8') as f:
        #     json.dump(books_list, f, indent=4, ensure_ascii=False)
    except KeyboardInterrupt:
        print('Исключение')
        # with open("response_custom.json", 'w', encoding='utf-8') as f:
        #     json.dump(books_list, f, indent=4, ensure_ascii=False)
    for book in books_list:
        if 'chitai-gorod' not in book.keys():
            book['chitai-gorod'] = []
    with open("response_custom.json", 'w', encoding='utf-8') as f:
        json.dump(books_list, f, indent=4, ensure_ascii=False)
