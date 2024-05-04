import json


class Product:

    def __init__(self, product_id, title, url, regular_price, promo_price, brand):
        self.product_id = product_id
        self.title = title
        self.url = url
        self.regular_price = regular_price
        self.promo_price = promo_price
        self.brand = brand

    def __repr__(self):
        return f'ID: {self.product_id}, {self.title}, {self.brand}'

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'title': self.title,
            'url': self.url,
            'regular_price': self.regular_price,
            'promo_price': self.promo_price,
            'brand': self.brand,
        }


def save_to_json(products, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        products_dict = [product.to_dict() for product in products]
        json.dump(products_dict, f, ensure_ascii=False, indent=4)