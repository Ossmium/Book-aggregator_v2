import os
import json
import requests
from bs4 import BeautifulSoup
# from multiprocessing import Pool
from book_aggregator.services.utils import remove_symbols
# from billiard import pool
from billiard.pool import Pool


PROXIES = {
    "https": "http://gFF1LE:ZcQyJB@5.101.91.155:8000"
}
FILENAME = ""


def get_urls(url, book_name):
    urls_list = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    books = soup.find_all("a", class_="product-card__name")
    for book in books:
        # print(book)
        if remove_symbols(book_name) == remove_symbols(book.get("title")):
            urls_list.append(f"https://www.labirint.ru{book.get('href')}")
        elif remove_symbols(book_name).replace('ё', 'е') == remove_symbols(book.get("title")):
            urls_list.append(f"https://www.labirint.ru{book.get('href')}")
    return urls_list


def get_book_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    book_price = soup.find("span", class_="buying-pricenew-val-number")
    if not book_price:
        book_price = soup.find("span", class_="buying-price-val-number")
        if not book_price:
            book_price = soup.find(
                "span", class_="buying-priceold-val").getText()
        else:
            book_price = book_price.text
    else:
        book_price = book_price.getText()
    book_dict = {
        "url": url,
        "rating": round(float(soup.find("div", class_="left").find("div").text) / 2, 1),
        "price": float(book_price) if book_price.isdigit() else book_price
    }
    # print(book_dict)
    return book_dict


def parser_labirint():
    count_books = 0
    with open(f"response_custom.json", 'r', encoding='utf-8') as f:
        books = json.load(f)
    try:
        for book in books:
            if "labirint" not in book.keys() or book["labirint"] == []:
                url = f"https://www.labirint.ru/search/{book['book_name']}/?stype=0"
                urls = get_urls(
                    url, book["book_name_without_symbols"])
                try:
                    with Pool(8) as p:
                        result = p.map(get_book_data, urls)
                except KeyboardInterrupt:
                    p.terminate()
                    p.join()
                    with open("response_custom.json", 'w', encoding='utf-8') as f:
                        json.dump(book, f, indent=4, ensure_ascii=False)
                book["labirint"] = result
            count_books += 1
            if count_books % 25 == 0:
                print(f"[+] Обработано {count_books}")
    except Exception as ex:
        print(ex)
    for book in books:
        if 'labirint' not in book.keys():
            book["labirint"] = []
    with open("response_custom.json", 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=4, ensure_ascii=False)
