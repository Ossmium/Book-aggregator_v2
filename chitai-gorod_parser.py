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


PROXIES = {
    0: {
        "https": "http://gFF1LE:ZcQyJB@5.101.91.155:8000"
    },
    1: {
        "https": "http://JhnjAj:fPoBvt@5.101.34.215:8000"
    },
    2: {
        "https": "http://JhnjAj:fPoBvt@5.101.35.2:8000"
    },
    3: {
        "https": "http://JhnjAj:fPoBvt@5.101.35.222:8000"
    },
    4: {
        "https": "http://JhnjAj:fPoBvt@5.101.34.195:8000"
    },
    5: {
        "https": "http://Ys7Eo5:YnjSDv@176.53.142.136:8000"
    },
    6: {
        "https": "http://Ys7Eo5:YnjSDv@176.53.142.64:8000"
    },
    7: {
        "https": "http://Ys7Eo5:YnjSDv@193.187.147.218:8000"
    },
    8: {
        "https": "http://Ys7Eo5:YnjSDv@193.187.145.101:8000"
    },
    9: {
        "https": "http://Ys7Eo5:YnjSDv@193.187.144.73:8000"
    },
    10: {
        "https": "http://Ys7Eo5:YnjSDv@193.187.146.73:8000"
    },
    11: {
        "https": "http://Ys7Eo5:YnjSDv@193.187.144.235:8000"
    },
    12: {
        "https": "http://Ys7Eo5:YnjSDv@193.187.145.76:8000"
    },
    13: {
        "https": "http://Ys7Eo5:YnjSDv@45.133.225.104:8000"
    },
    14: {
        "https": "http://Ys7Eo5:YnjSDv@45.133.226.130:8000"
    },
}
FILENAME = ""


def main():
    count_pages = 0
    count_books = 0
    change_proxy = 0
    current_proxy = PROXIES[0]
    user_agent = UserAgent(min_percentage=0.5).random
    global FILENAME
    try:
        for file in os.listdir("./response_custom_all_chitai-gorod")[:2]:
            with open(f"./response_custom_all_chitai-gorod/{file}", 'r', encoding='utf-8') as f:
                books_info_pages = json.load(f)
            FILENAME = f"./response_custom_all_chitai-gorod/{file}"
            # print(file)
            # try:
            for books_info_page in books_info_pages[:]:
                for book_info in books_info_page[:]:
                    if "chitai-gorod" not in book_info.keys() or book_info["chitai-gorod"] == []:
                        if count_books % 10 == 0:
                            current_proxy = random.choice(PROXIES)
                            change_proxy += 1
                            user_agent = UserAgent(min_percentage=0.5).random
                        url = f"https://www.chitai-gorod.ru/search?phrase={book_info['book_name']}&page=1&filters%5Bcategories%5D=18030"
                        response = requests.get(url, proxies=current_proxy, headers={'User-Agent': user_agent}, stream=True)
                        soup = BeautifulSoup(response.text, "lxml")
                        books = soup.find_all("article", class_="product-card product-card product")
                        books_suitable = []
                        for book in books:
                            name = book.find("div", class_="product-title__head").text.strip()
                            rating = 0.0
                            link = ""
                            price = 0
                            if remove_symbols(book_info['book_name']) == remove_symbols(name):
                                link = f"https://www.chitai-gorod.ru{book.find('a', class_='product-card__picture product-card__row').get('href')}"
                                price = book.find("div", class_="product-price__value")
                                if price:
                                    price = float(price.text.strip().replace('\xa0', '').split(' ')[0])
                                else:
                                    price = "Нет в продаже"
                                # print(book)
                                if not book.find("div", class_="no-rating"):
                                    rating = float(book.find("div", class_="star-rating__statistics").find("span",
                                                                                                     itemprop="ratingValue").text)
                            else:
                                continue
                            books_suitable.append({
                                "rating": rating,
                                "url": link,
                                "price": price,
                            })
                        book_info["chitai-gorod"] = books_suitable
                        # time.sleep(random.uniform(0.5, 1))
                    count_books += 1
                    if count_books % 25 == 0:
                        print(f"[+] Обработано {count_books}")
                count_pages += 1
            # time.sleep(random.uniform(30, 40))
            with open(FILENAME, 'w', encoding='utf-8') as f:
                json.dump(books_info_pages, f, indent=4, ensure_ascii=False)
            print(f"[+] Файл {file} обработан")
    except Exception as ex:
        print("Исключение", ex)
        print(PROXIES[change_proxy % len(PROXIES)])
        with open(FILENAME, 'w', encoding='utf-8') as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)
    except KeyboardInterrupt:
        with open(FILENAME, 'w', encoding='utf-8') as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)

    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(books_info_pages, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
