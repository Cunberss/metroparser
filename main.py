from config import MAX_COUNT
from functions import parser_start
from models import save_to_json


def main():
    products = parser_start()
    save_to_json(products, 'data.json')


if __name__ == '__main__':
    main()
