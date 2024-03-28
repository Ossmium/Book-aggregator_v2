import json
import time
import random
import zipfile
import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from hcaptcha_solver import hcaptcha_solver
from selenium_recaptcha_solver import RecaptchaSolver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium_recaptcha_solver.exceptions import RecaptchaException

LITRES_URLS = {
    "Легкое чтение": "https://api.litres.ru/foundation/api/genres/201583/arts/facets?art_types=text_book&genre=201583&limit=1000&o=popular&offset=",
    "Бизнес": "https://api.litres.ru/foundation/api/genres/5003/arts/facets?art_types=text_book&genre=5003&limit=1000&o=popular&offset=",
    "Спорт, здоровье, красота": "https://api.litres.ru/foundation/api/genres/201615/arts/facets?art_types=text_book&genre=201615&limit=1000&o=popular&offset=",
    "Детские книги": "https://api.litres.ru/foundation/api/genres/5007/arts/facets?art_types=text_book&genre=5007&limit=1000&o=popular&offset=",
    "Серьезное чтение": "https://api.litres.ru/foundation/api/genres/201591/arts/facets?art_types=text_book&genre=201591&limit=1000&o=popular&offset=",
    "Знания и навыки": "https://api.litres.ru/foundation/api/genres/201623/arts/facets?art_types=text_book&genre=201623&limit=1000&o=popular&offset=",
    "Хобби, досуг": "https://api.litres.ru/foundation/api/genres/201639/arts/facets?art_types=text_book&genre=201639&limit=1000&o=popular&offset=",
    "Родителям": "https://api.litres.ru/foundation/api/genres/201607/arts/facets?art_types=text_book&genre=201607&limit=1000&o=popular&offset=",
    "История": "https://api.litres.ru/foundation/api/genres/201599/arts/facets?art_types=text_book&genre=201599&limit=1000&o=popular&offset=0",
    "Психология, мотивация": "https://api.litres.ru/foundation/api/genres/201631/arts/facets?art_types=text_book&genre=201631&limit=1000&o=popular&offset=",
    "Дом, дача": "https://api.litres.ru/foundation/api/genres/201647/arts/facets?art_types=text_book&genre=201647&limit=1000&o=popular&offset=",
    "Публицистика и периодические издания": "https://api.litres.ru/foundation/api/genres/201655/arts/facets?art_types=text_book&genre=201655&limit=1000&o=popular&offset=",
}
BOOKS_NUMBER_TO_CHANGE = 100
CHANGE_PROXY_FLAG = 0
BOOKS_COUNTER = 0


def change_proxy(counter, start_time):
    proxy_dict = {
        0: {
            'PROXY_HOST': '83.217.6.7',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'nVUhy3',
            'PROXY_PASS': 'Uk0DWY',
        },
        1: {
            'PROXY_HOST': '83.217.7.48',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'nVUhy3',
            'PROXY_PASS': 'Uk0DWY',
        },
        2: {
            'PROXY_HOST': '212.192.207.79',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'nVUhy3',
            'PROXY_PASS': 'Uk0DWY',
        },
        3: {
            'PROXY_HOST': '195.19.200.80',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'nVUhy3',
            'PROXY_PASS': 'Uk0DWY',
        },
        4: {
            'PROXY_HOST': '212.192.207.203',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'nVUhy3',
            'PROXY_PASS': 'Uk0DWY',
        },
        5: {
            'PROXY_HOST': '195.19.115.137',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'nVUhy3',
            'PROXY_PASS': 'Uk0DWY',
        },
        6: {
            'PROXY_HOST': '45.139.108.202',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'cpjeyJ',
            'PROXY_PASS': 'okZ34h',
        },
        7: {
            'PROXY_HOST': '5.101.32.73',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'VsJhMs',
            'PROXY_PASS': 'yAXTup',
        },
        8: {
            'PROXY_HOST': '5.101.91.155',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'gFF1LE',
            'PROXY_PASS': 'ZcQyJB',
        },
        9: {
            'PROXY_HOST': '77.83.118.157',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'DrFVHB',
            'PROXY_PASS': 'LawGmT',
        },
        10: {
            'PROXY_HOST': '77.83.119.110',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'DrFVHB',
            'PROXY_PASS': 'LawGmT',
        },
        11: {
            'PROXY_HOST': '77.83.119.44',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'DrFVHB',
            'PROXY_PASS': 'LawGmT',
        },
        12: {
            'PROXY_HOST': '79.143.19.111',
            'PROXY_PORT': 8000,
            'PROXY_USER': 'DrFVHB',
            'PROXY_PASS': 'LawGmT',
        },
        13: {
            'PROXY_HOST': '77.83.119.135',
            'PROXY_PORT': 8000,
            'PROXY_USER': '6h6jhc',
            'PROXY_PASS': '4s4jQu',
        },
        14: {
            'PROXY_HOST': '79.143.19.67',
            'PROXY_PORT': 8000,
            'PROXY_USER': '6h6jhc',
            'PROXY_PASS': '4s4jQu',
        },
        15: {
            'PROXY_HOST': '77.83.118.148',
            'PROXY_PORT': 8000,
            'PROXY_USER': '6h6jhc',
            'PROXY_PASS': '4s4jQu',
        },
        16: {
            'PROXY_HOST': '77.83.119.14',
            'PROXY_PORT': 8000,
            'PROXY_USER': '6h6jhc',
            'PROXY_PASS': '4s4jQu',
        },
        17: {
            'PROXY_HOST': '77.83.119.127',
            'PROXY_PORT': 8000,
            'PROXY_USER': '6h6jhc',
            'PROXY_PASS': '4s4jQu',
        },
        18: {
            'PROXY_HOST': '77.83.119.46',
            'PROXY_PORT': 8000,
            'PROXY_USER': '6h6jhc',
            'PROXY_PASS': '4s4jQu',
        },
        19: {
            'PROXY_HOST': '79.143.19.141',
            'PROXY_PORT': 8000,
            'PROXY_USER': '6h6jhc',
            'PROXY_PASS': '4s4jQu',
        }
    }
    user_agent = UserAgent().getRandom['useragent']
    print(CHANGE_PROXY_FLAG, f'Количество обработанных книг: {BOOKS_COUNTER}', f"Прокси: {proxy_dict[CHANGE_PROXY_FLAG % 20]['PROXY_HOST']}", f"User-Agent: {user_agent}", time.time() - start_time)

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
    """ % (proxy_dict[CHANGE_PROXY_FLAG % 20]['PROXY_HOST'],
           proxy_dict[CHANGE_PROXY_FLAG % 20]['PROXY_PORT'],
           proxy_dict[CHANGE_PROXY_FLAG % 20]['PROXY_USER'],
           proxy_dict[CHANGE_PROXY_FLAG % 20]['PROXY_PASS'])
    return get_chromedriver(use_proxy=True,
                            user_agent=user_agent,
                            manifest_json=manifest_json,
                            background_js=background_js)


def get_chromedriver(use_proxy=False, user_agent=None,  manifest_json=None, background_js=None):
    chrome_options = webdriver.ChromeOptions()
    chrome_service = Service(executable_path='chromedriver-win64/chromedriver.exe')
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.page_load_strategy = 'eager'

    if use_proxy:
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        chrome_options.add_extension(plugin_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver = webdriver.Chrome(
        options=chrome_options,
        service=chrome_service
    )
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
    url = 'https://api.litres.ru/foundation/api/genres/201583/arts/facets?art_types=text_book&genre=201583&limit=1000&o=popular&offset=32'
    i = 0
    while requests.get(f"https://api.litres.ru/foundation/api/genres/201583/arts/facets?art_types=text_book&genre=201583&limit=1000&o=popular&offset={i * 1000}").json()['payload']['data'] != []:
        if i * 1000 > 4000:
            break
        response = requests.get(f"https://api.litres.ru/foundation/api/genres/201583/arts/facets?art_types=text_book&genre=201583&limit=1000&o=popular&offset={i * 1000}",
                                headers=headers).json()['payload']['data']
        books_dict.append(response)
        print(f'Обработано {(i + 1) * 1000}')
        i += 1
        time.sleep(1)

    with open('response/response_litres_legkoe_chtenie.json', 'w', encoding='utf-8') as file:
        json.dump(books_dict, file, indent=4, ensure_ascii=False)


def get_book_data(driver, book):
    global CHANGE_PROXY_FLAG
    source_data = driver.page_source
    # print(driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]'))

    soup = BeautifulSoup(source_data, "lxml")
    if soup.find('input', class_='coolbtn'):
        print('--------------Капча тута--------------')
        solver = RecaptchaSolver(driver=driver)
        try:
            WebDriverWait(driver, 20).until(
                ec.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
            )
            recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
            solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        except RecaptchaException:
            time.sleep(300)
            driver.refresh()
            WebDriverWait(driver, 20).until(
                ec.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
            )
            recaptcha_iframe = driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
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
            ec.presence_of_element_located((By.CLASS_NAME, "BookCard-module__genresList_1HXfh"))
        )
        time.sleep(5)
        driver.refresh()
    source_data = driver.page_source
    soup = BeautifulSoup(source_data, "lxml")
    # element = WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located((By.CLASS_NAME, "BookCard-module__genresList_1HXfh"))
    # )

    genres = soup.find('div', class_='BookCard-module__genresList_1HXfh')
    genres_list = []
    if genres:
        genres = genres.find_all('a')
        for genre in genres:
            genres_list.append(genre.text.strip())

    book_title = ''
    if soup.find('div', class_='BookCard-module__truncate_7elJD'):
        book_title = soup.find('div', class_='BookCard-module__truncate_7elJD').text

    print(book['title'] if book['title'] else None, f"https://litres.ru{book['url']}" if book['url'] else None, genres_list)

    book_info = {
        'book_name': book['title'] if book['title'] else None,
        'book_author': book['persons'][0]['full_name'] if book['persons'] else None,
        'book_genres': genres_list,
        'book_category': 'Бизнес',
        'book_title': book_title,
        'book_rating': book['rating']['rated_avg'] if book['rating'] else None,
        'book_link': f"https://litres.ru{book['url']}" if book['url'] else None,
        'book_image': f"https://litres.ru{book['cover_url']}" if book['cover_url'] else None
    }
    return book_info


def main():
    # get_data()
    global CHANGE_PROXY_FLAG
    global BOOKS_COUNTER

    with open('response/response_litres_business.json', 'r', encoding='utf-8') as file:
        books_dict = json.load(file)

    # change_proxy_flag = 0
    books_list = []
    # counter = 0
    start_time = time.time()
    for item in books_dict:
        books_info = []
        for book in item:
            try:
                if BOOKS_COUNTER % BOOKS_NUMBER_TO_CHANGE == 0:
                    if CHANGE_PROXY_FLAG > 0:
                        driver.close()
                        driver.quit()
                        if BOOKS_COUNTER % 1000 == 0:
                            time.sleep(120)
                    driver = change_proxy(CHANGE_PROXY_FLAG, start_time)
                    CHANGE_PROXY_FLAG += 1
                driver.get(f"https://litres.ru{book['url']}")
                # source_data = driver.page_source
                # # print(driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]'))
                #
                # soup = BeautifulSoup(source_data, "lxml")
                # if soup.find('input', class_='coolbtn'):
                #     driver.close()
                #     driver.quit()
                #     print('--------------Капча тута--------------')
                #     print('До:', CHANGE_PROXY_FLAG)
                #     CHANGE_PROXY_FLAG += 1
                #     print('После:', CHANGE_PROXY_FLAG)
                #     time.sleep(300)
                #     driver = change_proxy(CHANGE_PROXY_FLAG, start_time)
                #     driver.get(f"https://litres.ru{book['url']}")
                #     time.sleep(5)

                # time.sleep(10000)
                book_info = get_book_data(driver, book)
            except TimeoutException:
                try:
                    driver.refresh()
                    book_info = get_book_data(driver, book)
                except TimeoutException:
                    book_info = {
                        'book_name': book['title'] if book['title'] else None,
                        'book_author': book['persons'][0]['full_name'] if book['persons'] else None,
                        'book_genres': [],
                        'book_category': 'Бизнес',
                        'book_title': '',
                        'book_rating': book['rating']['rated_avg'] if book['rating'] else None,
                        'book_link': f"https://litres.ru{book['url']}" if book['url'] else None,
                        'book_image': f"https://litres.ru{book['cover_url']}" if book['cover_url'] else None
                    }
                    print('Exception:', book['title'] if book['title'] else None, book_info['book_link'], [], BOOKS_COUNTER)
            books_info.append(book_info)
            # time.sleep(random.uniform(2, 3))
            BOOKS_COUNTER += 1
        books_list.append(books_info)
        # time.sleep(180)
    driver.close()
    driver.quit()

    with open('response_custom/response_litres_business_custom.json', 'w', encoding='utf-8') as file:
        json.dump(books_list, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    CHANGE_PROXY_FLAG = 0
    main()
