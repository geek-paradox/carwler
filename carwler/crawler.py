import csv
import json
import re
import requests
from bs4 import BeautifulSoup

# from carwler.mysql_db import MysqlTable
from carwler.mongo_db import MongoDb


def snake_case(string: str):
    s = re.sub("[\(\[].*?[\)\]]", "", string)
    s = s.strip().replace(' ', '_').lower()
    return s


class Brands:
    FORD = 'ford'
    HONDA = 'honda'
    HYUNDAI = 'hyundai'
    KIA = 'kia'
    MAHINDRA = 'mahindra'
    MARUTI_SUZUKI = 'marutisuzuki'
    RENAULT = 'renault'
    TATA = 'tata'
    TOYOTA = 'toyota'

    def crawlable_brands(self):
        return [self.MARUTI_SUZUKI]


class CrawlCarWale:
    base_url = 'https://www.carwale.com'

    def get_brand_url(self, brand):
        return '{}/{}-cars'.format(self.base_url, brand)

    def get_car_url(self, car_link):
        return '{}{}'.format(self.base_url, car_link)

    def crawl_variant(self, variant_link):
        variant_url = self.get_car_url(variant_link)
        req = requests.get(variant_url)
        soup = BeautifulSoup(req.text, features='html5lib')
        specs_table = soup.find('div', {'id': 'tab-Specs'}).find_all('table')
        specs_obj = []
        features_obj = []
        for table in specs_table:
            spec_obj = {'heading': table.find('th').text, 'specs': {}}
            specs = table.find_all('tr')[1:]
            for spec in specs:
                spec_name = spec.find_all('td')[0].text.replace('\n', '').replace('\t', '')
                spec_value = str(spec.find_all('td')[1].text).strip().replace('\n', '').replace('\t', '')
                spec_obj['specs'][spec_name] = spec_value
            specs_obj.append(spec_obj)
        features_table = soup.find('div', {'id': 'tab-Features'}).find_all('table')
        for table in features_table:
            heading = str(table.find('th').text).replace('"', '')
            feature_obj = {'heading': heading, 'features': {}}
            features = table.find_all('tr')[1:]
            for feature in features:
                feature_name = feature.find_all('td')[0].text.replace('\n', '').replace('\t', '')
                feature_value = str(feature.find_all('td')[1].text).strip().replace('\n', '').replace('\t', '')
                feature_obj['features'][feature_name] = feature_value
            features_obj.append(feature_obj)
        return {'specifications': specs_obj, 'features': features_obj}

    def crawl_car(self, car_name, car_link):
        # TODO: find type -> Hatchback/Sedan etc.
        print(car_name, car_link)
        car_url = self.get_car_url(car_link)
        print('url', car_url)
        req = requests.get(car_url)
        soup = BeautifulSoup(req.text, features='html5lib')
        variant_list = []
        model_variants = soup.find('section', {'class': 'model__variants'})
        if model_variants:
            variants = model_variants.find('div', {'class': 'variant-list'})\
                .find('ul', {'class': 'variant-table-data'})\
                .find('table', {'class': 'variant-table'})\
                .find('tbody').find_all('tr')
            for variant in variants:
                variant_obj = {}
                variant_obj['fuel_type'] = variant.get('fuel-type')
                variant_obj['transmission_type'] = variant.get('transmission-type')
                variant_obj['name'] = variant.find('div', {'class': 'variant__name'}).find('a').text.strip()
                variant_link = variant.find('div', {'class': 'variant__name'}).find('a').get('href')
                variant_obj['link'] = variant_link
                variant_obj['short_name'] = variant_link[len(car_link): -1]
                variant_obj['short_specs'] = variant.find('span', {'class': 'variant__specs'}).text
                variant_obj['price'] = variant.find('span', {'class': 'variant__price'}).text
                variant_details = self.crawl_variant(variant_link)
                variant_obj['specifications'] = variant_details['specifications']
                variant_obj['features'] = variant_details['features']
                variant_list.append(variant_obj)

        return variant_list

    def crawl_brands(self):
        brands = Brands()
        result = []
        parse_brands = ['marutisuzuki', 'honda', 'hyundai', 'tata', 'toyota', 'mahindra', 'renault', 'ford']
        parse_models = []
        # parse_models = ['Maruti Suzuki Swift', 'Maruti Suzuki Baleno', 'Maruti Suzuki Dzire',
        #                 'Hyundai Grand i10 Nios', 'Hyundai Elite i20', 'Honda Amaze', 'Tata Tiago',
        #                 'Hyundai Venue', 'Tata Nexon']
        for brand in parse_brands:
            brand_data = {}
            print('## Brand', brand)
            brand_data['name'] = brand
            brand_url = self.get_brand_url(brand)
            brand_data['link'] = brand_url
            req = requests.get(brand_url)
            soup = BeautifulSoup(req.text, features='html5lib')

            div_models = soup.find('ul', {'id': 'divModels'})
            model_list = div_models.find_all('li', {'class': 'list-seperator'})
            cars = []
            for model in model_list:
                res = {}
                car = model.find('div', {'class': 'omega'}).find('a')
                car_name = car.get('title')
                car_link = car.get('href')
                res['name'] = car_name
                brand_name_len = len('/' + brand_data['name'] + '-cars/')
                res['short_name'] = car_link[brand_name_len:-1]
                res['link'] = car_link
                print('Car: {car} Link: {link}'.format(car=car_name, link=car_link))
                res['variants'] = self.crawl_car(car_name, car_link)
                cars.append(res)
            brand_data['cars'] = cars
            result.append(brand_data)

        with open('data.json', 'w') as file:
            json.dump(result, file)

    @staticmethod
    def save_to_csv(file):
        headers = ['Brand', 'Model', 'Variant', 'Fuel Type', 'Transmission Type', 'Price']
        flat_obj = []
        with open(file) as json_file:
            data = json.load(json_file)
            for brand in data:
                brand_name = brand['name']
                cars = brand['cars']
                for car in cars:
                    car_name = car['name']
                    variants = car['variants']
                    for variant in variants:
                        new_obj = {
                            'Brand': brand_name,
                            'Model': car_name,
                            'Variant': variant['variant_name'],
                            'Fuel Type': variant['fuel_type'],
                            'Transmission Type': variant['transmission_type'],
                            'Price': variant['variant_price']
                        }
                        specifications = variant['specifications']
                        for specification in specifications:
                            specs = specification['specs']
                            for k, v in specs.items():
                                if k not in headers:
                                    headers.append(k)
                                new_obj[k] = v
                        features = variant['features']
                        for feature in features:
                            f = feature['features']
                            for k, v in f.items():
                                if k not in headers:
                                    headers.append(k)
                                new_obj[k] = v
                        flat_obj.append(new_obj)

        # print(flat_obj)
        # print(headers)
        with open('fav.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(flat_obj)
        print('success')

    @staticmethod
    def save_to_mongo(file):
        mongo_db = MongoDb()
        mongo_db.connect()
        with open(file) as json_file:
            data = json.load(json_file)
            mongo_db.insert_data('brands', data)

    @staticmethod
    def save_to_db(file):
        brands = []
        models = []
        variant_rows = []
        variant_columns = ['model_id', 'name', 'url', 'fuel_type', 
                           'transmission_type', 'price', 'specifications', 'features']
        brand_i, model_i, variant_i = 1, 1, 1
        with open(file) as json_file:
            data = json.load(json_file)
            for brand in data:
                brand_name = brand['name']
                brand_url = brand['link']
                brands.append({'name': brand_name, 'link': brand_url})
                cars = brand['cars']
                for car in cars:
                    models.append({
                        'name': car['name'],
                        'link': car['link'],
                        'body_type': car['type'] or None,
                        'brand_id': brand_i
                    })
                    variants = car['variants']
                    for variant in variants:
                        variant_row = {
                            'model_id': model_i,
                            'name': variant['variant_name'],
                            'link': variant['variant_link'],
                            'fuel_type': variant['fuel_type'],
                            'transmission_type': variant['transmission_type'],
                            'price': variant['variant_price']
                        }
                        specifications = variant['specifications']
                        spec_obj = {}
                        for specification in specifications:
                            specs = specification['specs']
                            for k, v in specs.items():
                                spec_obj[k] = v
                        variant_row['specifications'] = spec_obj
                        features = variant['features']
                        feature_obj = {}
                        for feature in features:
                            f = feature['features']
                            for k, v in f.items():
                                feature_obj[k] = v
                        variant_row['features'] = feature_obj
                        variant_rows.append(variant_row)
                        variant_i += 1
                    model_i += 1
                brand_i += 1
        
        # mysql_cmd = MysqlTable()
        # mysql_cmd.delete_tables(['brand', 'model'])
        # mysql_cmd.create_tables()
        # # mysql_cmd.create_dynamic_table('variant', variant_columns)
        # mysql_cmd.insert_dynamic_table('brand', brands)
        # mysql_cmd.insert_dynamic_table('model', models)
        # mysql_cmd.insert_dynamic_table('variant', variant_rows)
        # mysql_cmd.commit()


class CrawlCarDekho:
    pass


class CrawlZigWheels:
    pass


if __name__ == "__main__":
    crawler = CrawlCarWale()
    crawler.crawl_brands()
    crawler.save_to_mongo('data.json')
