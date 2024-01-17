import math
import multiprocessing
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from utils.exporter import convert_to_json, remove_old_data, save_to_sqlite
from utils.parser import parsing_product_listing, parsing_products, parsing_region_list, \
    parsing_sitemaps
from utils.utils import check_reports_folder_exist, get_requests, print_template, random_sleep


os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.abspath(__file__))
futures = []


def start(city):
    try:
        DOMAIN = 'https://nlmk.shop'

        reports_folder = check_reports_folder_exist()
        if not reports_folder:
            sys.exit(1)

        print(print_template("Parse links to categories from the sitemap..."))
        catalog_links = parsing_sitemaps(DOMAIN, city)

        if not catalog_links:
            print(print_template("Error when parsing links to categories from the sitemap!"))
            return False

        print(print_template(f"Found {len(catalog_links)} links to product categories, start parsing..."))

        for index, catalog_link in enumerate(catalog_links):
            print(print_template(f'({index}/{len(catalog_links)})Start parsing category: {catalog_link}'))
            response = get_requests(catalog_link, city)

            if not response:
                print(print_template(f"({index}/{len(catalog_links)})Error parsing category, skip: {catalog_link}"))
                random_sleep(1)
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            product_listing = parsing_product_listing(soup)

            if not product_listing:
                print(print_template(f"({index}/{len(catalog_links)})No products in category: {catalog_link}"))
                random_sleep(1)
                continue

            products = parsing_products(product_listing, soup, catalog_link)

            if not products:
                print(print_template(f"({index}/{len(catalog_links)})Error parsing product page: {catalog_link}"))
                random_sleep(1)
                continue

            save_to_sqlite(f'{city}-', products, reports_folder)

            button_catalog_more = product_listing.find('button', id='button_catalog_more')
            if button_catalog_more:
                total_products = int(button_catalog_more.get_text().split('Показать ещё: ')[1])
                total_pages = math.ceil(total_products / 10)

                for page in range(total_pages):
                    page_url = f'{catalog_link}?page={page + 1}'

                    print(print_template(
                        f'({index}/{len(catalog_links)})Start parsing page #{page + 1}/{total_pages}: {page_url}'))

                    response = get_requests(page_url, city)
                    if not response:
                        print(print_template(
                            f"({index}/{len(catalog_links)})Error parsing product page #{page + 1}: {page_url}"))
                        continue
                    soup = BeautifulSoup(response.text, 'html.parser')

                    product_listing = parsing_product_listing(soup)

                    if not product_listing:
                        print(print_template(f"({index}/{len(catalog_links)})No products in category: {catalog_link}"))
                        random_sleep(1)
                        continue

                    products = parsing_products(product_listing, soup, catalog_link)
                    if not products:
                        print(print_template(f"({index}/{len(catalog_links)})Error parsing product page: {catalog_link}"))
                        random_sleep(1)
                        continue

                    save_to_sqlite(f'{city}-', products, reports_folder)

            random_sleep(1)

        return True
    except Exception as e:
        print(e)


if __name__ == '__main__':
    print(print_template(f"Get available for parsing cities/regions..."))

    cities = parsing_region_list()

    if not cities:
        print(print_template(f"Error when retrieving a list of cities"))
    else:
        cities = list(set(cities))
        reports_folder = check_reports_folder_exist()
        if not reports_folder:
            sys.exit(1)

        # remove_old_data(reports_folder, cities)
        #
        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     results = executor.map(start, cities)

        # with multiprocessing.Pool(1) as pool:
        #      pool.map(start, cities)

        total_count = convert_to_json(reports_folder, cities)

        print(f"Total count: {total_count}")