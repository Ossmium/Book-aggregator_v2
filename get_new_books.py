import os
import json
import time
import random
import zipfile
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium_recaptcha_solver import RecaptchaSolver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium_recaptcha_solver.exceptions import RecaptchaException

from labirint_parser import parser_labirint
from mybook_parser import parser_mybook
from chitai_gorod_parser import parser_chitai_gorod
from book_aggregator.services.utils import modify_data, make_sources, modify_books, add_books_v2, add_price_stats


BOOKS_NUMBER_TO_CHANGE = 40
CHANGE_PROXY_FLAG = 0
BOOKS_COUNTER = 0

LINK = f'https://api.litres.ru/foundation/api/arts/facets?art_types=text_book&is_for_pda=false&limit=200&o=new&offset=0'


def change_proxy(counter, start_time):
    proxy_dict = [
        {
            'PROXY_HOST': '185.148.27.146',
            'PROXY_PORT': 8000,
            'PROXY_USER': '9VCVu0',
            'PROXY_PASS': 'CoVSb7',
        },
        {
            'PROXY_HOST': '185.148.25.35',
            'PROXY_PORT': 8000,
            'PROXY_USER': '9VCVu0',
            'PROXY_PASS': 'CoVSb7',
        },
        {
            'PROXY_HOST': '185.148.25.167',
            'PROXY_PORT': 8000,
            'PROXY_USER': '9VCVu0',
            'PROXY_PASS': 'CoVSb7',
        },
    ]
    user_agent = UserAgent(min_percentage=5.0).random
    print(f'\nКоличество обработанных книг: {BOOKS_COUNTER}',
          f"Прокси: {proxy_dict[CHANGE_PROXY_FLAG % len(proxy_dict)]['PROXY_HOST']}", f"User-Agent: {user_agent} {time.time() - start_time}\n")

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"76.0.0"
    }
    """
    background_js = """
    let config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_dict[CHANGE_PROXY_FLAG % len(proxy_dict)]['PROXY_HOST'],
           proxy_dict[CHANGE_PROXY_FLAG % len(proxy_dict)]['PROXY_PORT'],
           proxy_dict[CHANGE_PROXY_FLAG % len(proxy_dict)]['PROXY_USER'],
           proxy_dict[CHANGE_PROXY_FLAG % len(proxy_dict)]['PROXY_PASS'])
    return get_chromedriver(use_proxy=True,
                            user_agent=user_agent,
                            manifest_json=manifest_json,
                            background_js=background_js)


def get_chromedriver(use_proxy=False, user_agent=None,  manifest_json=None, background_js=None):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--window-size=1280,720")

    # chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless=new')
    # chrome_options.add_argument('--disable-dev-sh-usage')
    # chrome_options.add_argument('--blink-settings=imagesEnabled=False')
    # chrome_options.page_load_strategy = 'eager'

    if use_proxy:
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        chrome_options.add_extension(plugin_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver = uc.Chrome(options=chrome_options,
                       executable_path="./chromedriver-linux64/chromedriver")
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
      '''
    })
    return driver


def get_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15'
    }

    books_dict = []
    i = 0
    books_dict = requests.get(LINK).json()['payload']['data']
    with open('response_litres.json', 'w', encoding='utf-8') as file:
        json.dump(books_dict, file, indent=4, ensure_ascii=False)

    books_dict_custom = []
    for book in books_dict:
        book_info = {
            'book_name': book['title'] if book['title'] else None,
            'book_author': book['persons'][0]['full_name'] if book['persons'] else None,
            'book_category': 'Публицистика и периодические издания',
            'book_rating': book['rating']['rated_avg'] if book['rating'] else None,
            'book_link': f"https://litres.ru{book['url']}" if book['url'] else None,
            'book_image': f"https://litres.ru{book['cover_url']}" if book['cover_url'] else None,
            'price': book['prices']['final_price'] if book['prices']['final_price'] else None,
        }
        books_dict_custom.append(book_info)

    with open('response.json', 'w', encoding='utf-8') as file:
        json.dump(books_dict_custom, file, indent=4, ensure_ascii=False)
    return books_dict_custom


def get_book_data(driver, book):
    global CHANGE_PROXY_FLAG
    source_data = driver.page_source
    soup = BeautifulSoup(source_data, "lxml")
    if soup.find('input', class_='coolbtn'):
        print('--------------Капча тута--------------')
        solver = RecaptchaSolver(driver=driver)
        try:
            WebDriverWait(driver, 20).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//iframe[@title="reCAPTCHA"]'))
            )
            recaptcha_iframe = driver.find_element(
                By.XPATH, '//iframe[@title="reCAPTCHA"]')
            solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        except RecaptchaException:
            time.sleep(300)
            # driver.refresh()
            WebDriverWait(driver, 20).until(
                ec.presence_of_element_located(
                    (By.XPATH, '//iframe[@title="reCAPTCHA"]'))
            )
            recaptcha_iframe = driver.find_element(
                By.XPATH, '//iframe[@title="reCAPTCHA"]')
            solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        if soup.find('input', class_='coolbtn'):
            WebDriverWait(driver, 20).until(
                ec.presence_of_element_located((By.CLASS_NAME, "coolbtn"))
            )
            WebDriverWait(driver, 20).until(
                ec.element_to_be_clickable((By.CLASS_NAME, "coolbtn"))
            )
            driver.find_element(By.CLASS_NAME, "coolbtn").click()
            time.sleep(5)
        element = WebDriverWait(driver, 20).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, "BookCard-module__genresList_1HXfh"))
        )
        driver.refresh()
        time.sleep(100)
    source_data = driver.page_source
    soup = BeautifulSoup(source_data, "lxml")

    genres = soup.find('div', class_='BookGenresAndTags_genresList__rd8vU')
    genres_list = []
    if genres:
        genres = genres.find_all('a')
        for genre in genres:
            genres_list.append(genre.text.strip())

    book_title = ''
    if soup.find('div', class_='BookCard_book__annotation__8wq0r'):
        book_title = soup.find(
            'div', class_='BookCard_book__annotation__8wq0r').text

    book["book_genres"] = genres_list
    book["book_title"] = book_title


def check_books_count(books_dict):
    counter = 0
    for item in books_dict:
        for book in item:
            if "book_genres" not in book.keys():
                counter += 1
    return counter


def get_books():
    global CHANGE_PROXY_FLAG
    global BOOKS_COUNTER

    books = get_data()

    start_time = time.time()
    books_list = []
    print('Litres')
    try:
        for book in books[:5]:
            if BOOKS_COUNTER % 25 == 0:
                print(f'[+] Обработано {BOOKS_COUNTER}')
            if "book_genres" not in book.keys() or book["book_genres"] == []:
                try:
                    if BOOKS_COUNTER % BOOKS_NUMBER_TO_CHANGE == 0:
                        if CHANGE_PROXY_FLAG > 0:
                            driver.close()
                            driver.quit()
                        driver = change_proxy(
                            CHANGE_PROXY_FLAG, start_time)
                        CHANGE_PROXY_FLAG += 1
                    driver.get(f"{book['book_link']}")
                    get_book_data(driver, book)
                except TimeoutException:
                    try:
                        driver.refresh()
                        get_book_data(driver, book)
                    except TimeoutException:
                        book["book_genres"] = []
                        book["book_title"] = ""
                        print('Exception:', book['book_name'] if book['book_name'] else None, book['book_link'], [
                        ], BOOKS_COUNTER)
                time.sleep(random.uniform(1, 2))
                BOOKS_COUNTER += 1
            books_list.append(book)
    except:
        print("Исключение")
        with open('response_custom.json', 'w', encoding='utf-8') as file:
            json.dump(books_list, file, indent=4, ensure_ascii=False)

    with open('response_custom.json', 'w', encoding='utf-8') as file:
        json.dump(books_list, file, indent=4, ensure_ascii=False)
    modify_data()
    print('Labirint')
    parser_labirint()
    print('MyBook')
    parser_mybook()
    print('Читай Город')
    parser_chitai_gorod()
    print('Остальное')
    make_sources()
    modify_books()
    add_books_v2()
    add_price_stats()


if __name__ == '__main__':
    get_books()
