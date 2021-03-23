import time
import json
from pathlib import Path
import requests

#url = "https://5ka.ru/api/v2/special_offers/"

#params = {
#    "categories": None,
#    "ordering": None,
#    "page": 2,
#    "price_promo__gte": None,
#    "price_promo__lte": None,
#    "records_per_page": 12,
#    "search": None,
#    "store": None
#}

#response = requests.get(url, params=params)

#if response.status_code == 200:
#    Path(__file__).parent.joinpath('5ka.json').write_text(response.text, 'UTF-8')

class Parse5ka:
    params = {
        "records_per_page": 20
    }

    def __init__(self, start_url: str, categories_url: str, result_path: Path):
        self.start_url = start_url
        self.result_path = result_path
        self.categories_url = categories_url

    def _get_response(self, url, *args, **kwargs) -> requests.Response:
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def run(self):
         for categories in self._parse_categories(self.categories_url):
            self._save_categories(categories)       

    def _parse_categories(self, url):
        response = self._get_response(url)
        data = response.json()
        for categories in data:
            yield categories

    def _parse(self, url, params):         
        while url:
            response = self._get_response(url, params)
            data = response.json()
            url = data.get('next')
            for product in data.get('results', []):
                yield product    

    def _save_categories(self, data):
        fale_path = self.result_path.joinpath(f'{data["parent_group_name"]}.json')
        self.params["categories"] = data["parent_group_code"]
        array_product = []
        for product in self._parse(self.start_url, self.params):
            array_product.append(product)

        data["products"] = array_product              
        
        fale_path.write_text(json.dumps(data, ensure_ascii=False), 'UTF-8')

if __name__ == '__main__':
    file_path = Path(__file__).parent.joinpath("продукты по категориям") # "products"
    if not file_path.exists():
        file_path.mkdir()
    parser = Parse5ka("https://5ka.ru/api/v2/special_offers/", "https://5ka.ru/api/v2/categories/", file_path)
    parser.run()
