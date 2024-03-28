import os
import json
import time

import requests
from bs4 import BeautifulSoup
from utils import remove_symbols

PROXIES = {
    "https": "http://gFF1LE:ZcQyJB@5.101.91.155:8000"
}

count_pages = 0
count_books = 0
filename = ""
for file in os.listdir("./response_custom_all_test"):
    with open(f"./response_custom_all_test/{file}", 'r', encoding='utf-8') as f:
        books_info_pages = json.load(f)
    filename = f"./response_custom_all_test/{file}"
    try:
        for books_info_page in books_info_pages:
            for book_info in books_info_page:
                if "mybook_link" not in book_info.keys():
                    url = f"https://mybook.ru/search/books/?q={book_info['book_name_without_symbols']}"
                    response = requests.get(url, proxies=PROXIES)
                    soup = BeautifulSoup(response.text, "lxml")
                    response_books = soup.find_all("div", class_="e4xwgl-0 iJwsmp")
                    if not len(response_books):
                        book_info["mybook_link"] = ""
                        book_info["mybook_rating"] = None
                        book_info["mybook_price"] = None
                        count_books += 1
                        continue
                    flag = False
                    for response_book in response_books:
                        if flag:
                            break
                        book_name = response_book.find("p", class_="lnjchu-1 hhskLb")
                        book_link = response_book.find("a")
                        book_rating = response_book.find("p", class_="lnjchu-1 kgTBVx")
                        book_price = response_book.find("p", class_="lnjchu-1 kgTBVx sc-3u14ee-1 OSKeK")
                        if book_name:
                            if remove_symbols(book_info["book_name_without_symbols"]) == remove_symbols(book_name.text):
                                flag = True
                                if not book_price.text.isdigit():
                                    book_price = "Подписка " + book_price.text
                                book_info["mybook_link"] = f"https://mybook.ru{book_link.get('href')}"
                                book_info["mybook_rating"] = float(book_rating.text)
                                book_info["mybook_price"] = book_price
                count_books += 1
                if count_books % 50 == 0:
                    print(f"[+] Обработано {count_books}")
            count_pages += 1
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)
        print(f"[+] Файл {file} обработан")
    except:
        print("Исключение")
        with open(f"./response_custom_all_test/{file}", 'w', encoding='utf-8') as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)

with open(filename, 'w', encoding='utf-8') as f:
    json.dump(books_info_pages, f, indent=4, ensure_ascii=False)


