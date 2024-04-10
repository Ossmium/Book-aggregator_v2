import os
import json
# from book_aggregator.models import Book, SubCategory
from django.utils.timezone import make_aware
from slugify import slugify
import datetime

TRANSLATE_TABLE = {
    ord(','): None,
    ord('–'): None,
    ord('.'): None,
    ord(':'): None,
    ord('\\'): None,
    ord('/'): None,
    ord('«'): None,
    ord('»'): None,
    ord('\xa0'): ' ',
    ord('-'): None,
    ord('…'): None,
    ord('\"'): None,
    ord('\''): None,
    ord('ё'): 'е',
    ord(' '): None,
}
PROXIES = {
    "https": "http://gFF1LE:ZcQyJB@5.101.91.155:8000"
}


def remove_symbols(string):
    return string.translate(TRANSLATE_TABLE).replace('  ', ' ').lower()


def modify_data():
    with open(f"response_custom.json", 'r', encoding='utf-8') as f:
        books = json.load(f)
        for book in books:
            book['book_name'] = book['book_name'].replace(' ', ' ')
            book['book_name_without_symbols'] = book['book_name'].translate(
                TRANSLATE_TABLE).replace('  ', ' ').lower()
            book['book_title'] = book['book_title'].replace(' ', ' ')
    with open("response_custom.json", 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=4, ensure_ascii=False)


def find_books():
    for file in os.listdir("./response_custom_all"):
        with open(f"./response_custom_all/{file}", 'r', encoding='utf-8') as f:
            books_info = json.load(f)
            print(books_info[0][0]['book_name'])


def flat_book_lists():
    books_list = []
    for file in os.listdir("./response_test_sources_v2"):
        with open(f"./response_test_sources_v2/{file}", 'r', encoding='utf-8') as f:
            books_info_pages = json.load(f)
        for books_info_page in books_info_pages:
            for book_info in books_info_page:
                book_info["book_title"] = book_info["book_title"].replace(
                    '\n', ' ')
                books_list.append(book_info)
    with open("final_file.json", "w", encoding="utf-8") as file:
        json.dump(books_list, file, indent=4, ensure_ascii=False)
    return len(books_list)


def add_prices_litres():
    for file in os.listdir("./response_custom_all_final_test"):
        with open(f"./response_custom_all_final_test/{file}", 'r', encoding='utf-8') as f:
            books_info_pages = json.load(f)
        file_old = "_".join(file.split("_")[:3]) + ".json"
        with open(f"./response/{file_old}", 'r', encoding='utf-8') as f:
            books_info_pages_old = json.load(f)
        for i, books_info_page in enumerate(books_info_pages):
            for j, book_info in enumerate(books_info_page):
                book_info["price"] = books_info_pages_old[i][j]["prices"]["final_price"]
        with open(f"./response_custom_all_final_test/{file}", "w", encoding="utf-8") as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)


def make_sources():
    with open(f"response_custom.json", 'r', encoding='utf-8') as f:
        books = json.load(f)
    for book in books:
        book["sources"] = {
            "litres": [
                {
                    "url": book["book_link"],
                    "rating": book["book_rating"],
                    "price": book["price"],
                }
            ],
            "mybook": [
                {
                    "url": book["mybook_link"] if book["mybook_link"] else "",
                    "rating": book["mybook_rating"] if book["mybook_rating"] else None,
                    "price": book["mybook_price"] if book["mybook_price"] else None,
                }
            ],
            "labirint": book["labirint"],
            "chitai-gorod": book["chitai-gorod"]
        }
        book.pop("book_rating")
        book.pop("book_link")
        book.pop("mybook_link")
        book.pop("mybook_rating")
        book.pop("mybook_price")
        book.pop("labirint")
        book.pop("chitai-gorod")
        book.pop("price")
    with open(f"response_custom.json", "w", encoding="utf-8") as f:
        json.dump(books, f, indent=4, ensure_ascii=False)


def add_keys():
    for file in os.listdir("./response_test_sources_v2"):
        with open(f"./response_test_sources_v2/{file}", 'r', encoding='utf-8') as f:
            books_info_pages = json.load(f)
        for books_info_page in books_info_pages:
            for book_info in books_info_page:
                book_keys = book_info.keys()
                if "mybook_link" not in book_keys:
                    book_info["mybook_link"] = ""
                if "mybook_rating" not in book_keys:
                    book_info["mybook_rating"] = None
                if "mybook_price" not in book_keys:
                    book_info["mybook_price"] = None
        with open(f"./response_test_sources_v2/{file}", 'w', encoding='utf-8') as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)


def make_books_categories():
    with open("final_file.json", "r", encoding="utf-8") as file:
        books_list = json.load(file)
    books = set()
    for i, book in enumerate(books_list):
        book_name = book["book_name"]
        if i == len(books_list):
            break
        for j in range(i + 1, len(books_list)):
            if book_name == books_list[j]["book_name"]:
                book["book_category"] += f' | {books_list[j]["book_category"]}'
                books.add(book_name)
    with open("final_file_v2.json", "w", encoding="utf-8") as file:
        json.dump(books_list, file, indent=4, ensure_ascii=False)


def make_union_list():
    with open("final_file_v2.json", "r", encoding="utf-8") as file:
        books_list = json.load(file)
    books_list_temp = []
    books_set = set()
    for book in books_list:
        if book["book_name"] in books_set:
            continue
        books_list_temp.append(book)
        books_set.add(book["book_name"])
    with open("final_file_v3.json", "w", encoding="utf-8") as file:
        json.dump(books_list_temp, file, indent=4, ensure_ascii=False)


def modify_books():
    with open("response_custom.json", "r", encoding="utf-8") as file:
        books_list = json.load(file)
    for book in books_list:
        if type(book['book_category']) != list:
            book['book_category'] = book['book_category'].split(' | ')

        if book['sources']['litres'] != [] or book['sources']['mybook'] != []:
            book['have_electronic_version'] = True
        else:
            book['have_electronic_version'] = False
        if book['sources']['labirint'] != [] or book['sources']['chitai-gorod'] != []:
            book['have_physical_version'] = True
        else:
            book['have_physical_version'] = False

        book_rating = 0
        book_sources_counter = 0
        book_prices = []
        for source in book['sources']:
            book_source = book['sources'][source]
            for book_info in book_source:
                if book_info['rating'] is not None:
                    book_rating += book_info['rating']
                    book_sources_counter += 1
                if type(book_info['price']) != str and book_info['price'] is not None:
                    book_prices.append(book_info['price'])
        # print(book_prices, min(book_prices), max(book_prices))
        book_rating = book_rating / book_sources_counter
        if len(book_prices) == 0:
            book_prices.append(0)
        book['book_avg_rating'] = book_rating
        book['min_price'] = min(book_prices)
        book['max_price'] = max(book_prices)

        # print(book_rating, book_sources_counter)
    with open("response_custom.json", "w", encoding="utf-8") as file:
        json.dump(books_list, file, indent=4, ensure_ascii=False)


def add_book(book, idx):
    updated_at = make_aware(datetime.datetime.now())
    slug = slugify(book["book_name"][:50] + f" {idx + 1}")
    Book(name=book["book_name"],
         author=book["book_author"],
         categories=book["book_category"],
         image_url=book["book_image"],
         genres=book["book_genres"],
         description=book["book_title"],
         avg_rating=book['book_avg_rating'],
         min_price=book['min_price'],
         max_price=book['max_price'],
         have_electronic_version=book['have_electronic_version'],
         have_physical_version=book['have_physical_version'],
         sources=book["sources"],
         updated_at=updated_at,
         slug=slug).save()


def add_subcategories():
    with open("final_file_v4.json", "r", encoding="utf-8") as file:
        books_list = json.load(file)
    books_subcategories_set = set()
    for book in books_list:
        book_genres = book['book_genres']
        for book_genre in book_genres:
            books_subcategories_set.add(book_genre)
    for books_subcategory in books_subcategories_set:
        SubCategory(
            name=books_subcategory,
            slug=slugify(books_subcategory)
        ).save()


def add_books_v2():
    with open(f"response_custom.json", 'r', encoding='utf-8') as f:
        books = json.load(f)
    for book in books:
        for source in book['sources']:
            if len(book['sources'][source]):
                if book['sources'][source][-1]['url'] != '':
                    books_sources = []
                    for book_sources in book['sources'][source]:
                        book_sources_list = []
                        dt = datetime.datetime.now()
                        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        book_sources_list.append([book_sources, dt_str])
                        books_sources.append(book_sources_list)
                    book['sources'][source] = books_sources
            else:
                book['sources'][source] = []
    with open('response_custom.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=4, ensure_ascii=False)


def add_price_stats():
    with open(f"response_custom.json", 'r', encoding='utf-8') as f:
        books = json.load(f)
    for book in books:
        summary_counter = 0
        summary_avg_price = 0
        stats = {
            'data': []
        }
        obj = {}
        for source in book['sources']:
            if source == 'mybook':
                continue
            source_avg_sum = 0
            counter = 0
            for el in book['sources'][source]:
                if type(el[-1][0]['price']) != str and el[-1][0]['price'] != None:
                    source_avg_sum += el[-1][0]['price']
                    summary_avg_price += el[-1][0]['price']
                    counter += 1
                    summary_counter += 1
            if not counter:
                continue
            obj[source] = source_avg_sum / counter
        # print(book.url, summary_avg_price)
        obj['summary'] = summary_avg_price / summary_counter
        dt = datetime.datetime.now()
        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        obj['updated_at'] = dt_str
        stats['data'].append(obj)
        book['price_stats'] = stats

    with open('response_custom.json', 'w', encoding='utf-8') as f:
        json.dump(books, f, indent=4, ensure_ascii=False)
