import os
import json
from book_aggregator.models import Book, SubCategory
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
    for file in os.listdir("./response_custom_all_test"):
        with open(f"./response_custom_all_test/{file}", 'r', encoding='utf-8') as f:
            books_info_pages = json.load(f)
    # with open('response_1.json', 'r', encoding='utf-8') as file:
    #     books_info_pages = json.load(file)
            for books_info_page in books_info_pages:
                for book_info in books_info_page:
                    book_info['book_name'] = book_info['book_name'].replace(' ', ' ')
                    book_info['book_name_without_symbols'] = book_info['book_name'].translate(TRANSLATE_TABLE).replace('  ', ' ').lower()
                    book_info['book_title'] = book_info['book_title'].replace(' ', ' ')
        with open(f"./response_custom_all_test/{file}", 'w', encoding='utf-8') as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)


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
                book_info["book_title"] = book_info["book_title"].replace('\n', ' ')
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
    for file in os.listdir("./response_test_sources_v2"):
        with open(f"./response_test_sources_v2/{file}", 'r', encoding='utf-8') as f:
            books_info_pages = json.load(f)
        counter = 0
        for books_info_page in books_info_pages:
            for book_info in books_info_page:
                counter += 1
                print(counter)
                book_info["sources"] = {
                    "litres": [
                        {
                            "url": book_info["book_link"],
                            "rating": book_info["book_rating"],
                            "price": book_info["price"],
                        }
                    ],
                    "mybook": [
                        {
                            "url": book_info["mybook_link"] if book_info["mybook_link"] else "",
                            "rating": book_info["mybook_rating"] if book_info["mybook_rating"] else None,
                            "price": book_info["mybook_price"] if book_info["mybook_price"] else None,
                        }
                    ],
                    "labirint": book_info["labirint"],
                    "chitai-gorod": book_info["chitai-gorod"]
                }
                book_info.pop("book_rating")
                book_info.pop("book_link")
                book_info.pop("mybook_link")
                book_info.pop("mybook_rating")
                book_info.pop("mybook_price")
                book_info.pop("labirint")
                book_info.pop("chitai-gorod")
                book_info.pop("price")
        with open(f"./response_test_sources_v2/{file}", "w", encoding="utf-8") as f:
            json.dump(books_info_pages, f, indent=4, ensure_ascii=False)
        print(f"[+] {file}")


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
    with open("final_file_v4.json", "r", encoding="utf-8") as file:
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
    with open("final_file_v4.json", "w", encoding="utf-8") as file:
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

if __name__ == "__main__":
    # flat_book_lists()
    # make_sources()
    # add_keys()
    # make_books_categories()
    # make_union_list()

    # with open("final_file_v3.json", 'r', encoding='utf-8') as file:
    #     books = json.load(file)
    # book = books[1]
    # print(slugify(book["book_name"]))
    # add_book(book)
    # print(datetime.datetime.now())
    # modify_books()
    add_subcategories()
