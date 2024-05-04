from typing import List

import requests
from bs4 import BeautifulSoup

from models import Product
from config import PARSE_URL, IN_STOCK, MAX_COUNT, PREFIX


def parse_page(page: int) -> List[Product]:
    current_url = generate_current_url(page)
    result = []
    response = requests.get(current_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('div', class_='catalog-2-level-product-card product-card subcategory-or-type__products-item with-prices-drop')
    for product in products:
        product_id = product['id']
        title = str(product.find('span', class_='product-card-name__text').text).strip()
        product_price_sum_rubles = str(product.find('span', class_='product-price__sum-rubles').text).strip()
        product_price_sum_pennys = product.find('span', class_='product-price__sum-penny')
        if product_price_sum_pennys:
            product_price = product_price_sum_rubles + str(product_price_sum_pennys.text).strip()
        else:
            product_price = product_price_sum_rubles
        is_two_price = product.find('div', class_='product-unit-prices__old-wrapper')
        try:
            two_price_sum_rubles = str(is_two_price.find('span', class_='product-price__sum-rubles').text).strip()
            two_price_sum_pennys = is_two_price.find('span', class_='product-price__sum-penny')
            if two_price_sum_pennys:
                two_price = two_price_sum_rubles + str(two_price_sum_pennys.text).strip()
            else:
                two_price = two_price_sum_rubles
        except:
            two_price = None

        if product_price and two_price:
            regular_price = two_price
            promo_price = product_price
        else:
            regular_price = product_price
            promo_price = '-'
        url = PREFIX + str(product.find('a', class_='product-card-photo__link reset-link')['href']).strip()
        product_data = requests.get(url)
        soup_product = BeautifulSoup(product_data.text, 'html.parser')
        brand_span = soup_product.find('span', class_='product-attributes__list-item-name-text', text=lambda t: 'Бренд' in t)
        if brand_span:
            brand_a = brand_span.find_next('a')
            if brand_a:
                brand = brand_a.text.strip()
            else:
                brand = '-'
        else:
            brand = '-'
        result.append(Product(product_id, title, url, regular_price, promo_price, brand))
        print(result)
    return result


def parser_start() -> List[Product]:
    products = []
    start_page = 1
    while len(products) < MAX_COUNT:
        products.extend(parse_page(start_page))
        start_page += 1
    return products[:MAX_COUNT]


def generate_current_url(page: int):
    return PARSE_URL + f'&page={page}&in_stock={IN_STOCK}'
