import os
import json
import time

import requests
from bs4 import BeautifulSoup
from book_aggregator.services.utils import remove_symbols

PROXIES = {
    "https": "http://9VCVu0:CoVSb7@185.148.27.146:8000"
}


def parser_mybook():
    count_pages = 0
    count_books = 0
    filename = ""
    with open(f"response_custom.json", 'r', encoding='utf-8') as f:
        books = json.load(f)
    try:
        for book in books:
            if "mybook_link" not in book.keys():
                url = f"https://mybook.ru/search/books/?q={book['book_name_without_symbols']}"
                response = requests.get(url, proxies=PROXIES)
                soup = BeautifulSoup(response.text, "lxml")
                response_books = soup.find_all(
                    "div", class_="e4xwgl-0 iJwsmp")
                if not len(response_books):
                    book["mybook_link"] = ""
                    book["mybook_rating"] = None
                    book["mybook_price"] = None
                    count_books += 1
                    continue
                flag = False
                for response_book in response_books:
                    if flag:
                        break
                    book_name = response_book.find(
                        "p", class_="lnjchu-1 hhskLb")
                    book_link = response_book.find("a")
                    book_rating = response_book.find(
                        "p", class_="lnjchu-1 kgTBVx")
                    book_price = response_book.find(
                        "p", class_="lnjchu-1 kgTBVx sc-3u14ee-1 OSKeK")
                    if book_name:
                        if remove_symbols(book["book_name_without_symbols"]) == remove_symbols(book_name.text):
                            flag = True
                            if not book_price.text.isdigit():
                                book_price = "Подписка " + book_price.text
                            book["mybook_link"] = f"https://mybook.ru{book_link.get('href')}"
                            book["mybook_rating"] = float(
                                book_rating.text)
                            book["mybook_price"] = book_price
                if not flag:
                    book["mybook_link"] = ""
                    book["mybook_rating"] = None
                    book["mybook_price"] = None
            count_books += 1
            if count_books % 50 == 0:
                print(f"[+] Обработано {count_books}")
    except:
        print("Исключение")
        # with open(f"response_custom.json", 'w', encoding='utf-8') as f:
        #     json.dump(books, f, indent=4, ensure_ascii=False)

    for book in books:
        if 'mybook_link' not in book.keys():
            book["mybook_link"] = ""
            book["mybook_rating"] = None
            book["mybook_price"] = None
    with open("response_custom.json", 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=4, ensure_ascii=False)
