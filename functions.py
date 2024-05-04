import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

import requests
from bs4 import BeautifulSoup

from models import Product
from config import PARSE_URL, IN_STOCK, MAX_COUNT, PREFIX


def timing_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Время выполнения функции {func.__name__}: {end_time - start_time} секунд.")
        return result

    return wrapper


def extract_price(product, class_name):
    price_rubles_span = product.find('span', class_=f'{class_name}__sum-rubles')
    price_rubles = price_rubles_span.text.strip() if price_rubles_span else ''

    price_pennys_span = product.find('span', class_=f'{class_name}__sum-penny')
    price_pennys = price_pennys_span.text.strip() if price_pennys_span else ''

    return f'{price_rubles}{price_pennys}'


def extract_brand(soup_product):
    brand_span = soup_product.find('span', class_='product-attributes__list-item-name-text',
                                   text=lambda t: 'Бренд' in t)
    if brand_span:
        brand_a = brand_span.find_next('a')
        return brand_a.text.strip() if brand_a else '-'
    return '-'


def parse_price(product):
    product_price = extract_price(product, 'product-price')
    is_two_price = product.find('div', class_='product-unit-prices__old-wrapper')
    if is_two_price:
        two_price = extract_price(is_two_price, 'product-price')
        if product_price and two_price:
            return product_price, two_price
        else:
            return product_price, '-'
    return product_price, '-'


def parse_product(product):
    product_id = product['id']
    title = product.find('span', class_='product-card-name__text').text.strip()
    product_price, promo_price = parse_price(product)
    url = PREFIX + product.find('a', class_='product-card-photo__link reset-link')['href'].strip()
    product_data = requests.get(url)
    soup_product = BeautifulSoup(product_data.text, 'html.parser')
    brand = extract_brand(soup_product)
    return Product(product_id, title, url, product_price, promo_price, brand)


def parse_page(page: int) -> List[Product]:
    current_url = generate_current_url(page)
    response = requests.get(current_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div',
                             class_='catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop')

    with ThreadPoolExecutor(max_workers=10) as executor:
        result = list(executor.map(parse_product, products))
    return result


@timing_function
def parser_start() -> List[Product]:
    products = []
    start_page = 1
    while len(products) < MAX_COUNT:
        products.extend(parse_page(start_page))
        start_page += 1
    return products[:MAX_COUNT]


def generate_current_url(page: int):
    return PARSE_URL + f'&page={page}&in_stock={IN_STOCK}'
