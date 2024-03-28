import os
import json
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
from utils import remove_symbols


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
            book_price = soup.find("span", class_="buying-priceold-val").getText()
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


def main():
    count_pages = 0
    count_books = 0
    global FILENAME
    for file in os.listdir("./response_custom_all_labirint")[11:]:
        with open(f"./response_custom_all_labirint/{file}", 'r', encoding='utf-8') as f:
            books_info_pages = json.load(f)
        FILENAME = f"./response_custom_all_labirint/{file}"
        # print(file)
        try:
            for books_info_page in books_info_pages:
                for book_info in books_info_page:
                    if "labirint" not in book_info.keys() or book_info["labirint"] == []:
                        url = f"https://www.labirint.ru/search/{book_info['book_name']}/?stype=0"
                        urls = get_urls(url, book_info["book_name_without_symbols"])
                        try:
                            with Pool(8) as p:
                                result = p.map(get_book_data, urls)
                        except KeyboardInterrupt:
                            p.terminate()
                            p.join()
                            with open(FILENAME, 'w', encoding='utf-8') as f:
                                json.dump(books_info_pages, f, indent=4, ensure_ascii=False)
                        book_info["labirint"] = result
                    count_books += 1
                    if count_books % 25 == 0:
                        print(f"[+] Обработано {count_books}")
                count_pages += 1
                with open(FILENAME, 'w', encoding='utf-8') as f:
                    json.dump(books_info_pages, f, indent=4, ensure_ascii=False)
            print(f"[+] Файл {file} обработан")
        except:
            print("Исключение")
            with open(f"./response_custom_all_labirint/{file}", 'w', encoding='utf-8') as f:
                json.dump(books_info_pages, f, indent=4, ensure_ascii=False)

    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(books_info_pages, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
