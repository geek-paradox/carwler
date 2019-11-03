from pymongo import MongoClient
import os


class MongoDb:
    def __init__(self):
        host = os.getenv('MONGODB_ADDON_URI') or 'mongodb://localhost:27017/'
        db_name = os.getenv('MONGODB_ADDON_DB') or 'carwler'
        conn = MongoClient(host)
        self.db = conn[db_name]
        self.brands_col = self.db['brands']

    def insert_data(self, rows):
        collection = self.brands_col
        x = collection.insert_many(rows)
        print('inserted ids: {ids}'.format(ids=x.inserted_ids))

    def get_brands(self):
        data = list(self.brands_col.find({}, {'_id': 0, 'name': 1}))
        return [row['name'] for row in data]

    def get_models(self, brand_name):
        return list(self.brands_col.find({'name': brand_name}, {
            'cars.name': 1, 'cars.short_name': 1, '_id': 0}))[0]['cars']

    def get_variants(self, brand_name, model_short_name):
        data = self.brands_col.find({'name': brand_name}, {
            'cars': {'$elemMatch': {'short_name': model_short_name}}, '_id': 0,
            'cars.variants.name': 1,
            'cars.variants.fuel_type': 1,
            'cars.variants.short_name': 1,
            'cars.variants.transmission_type': 1})
        return list(data)[0]['cars'][0]['variants']

    def get_details(self, filters):
        rows = []
        for q in filters:
            brand_name = q['brand']
            model_short_name = q['model']
            variant_short_name = q['variant']
            pipeline = [
                {'$match': {'name': brand_name}},
                {'$unwind': '$cars'},
                {'$match': {'cars.short_name': model_short_name}},
                {'$unwind': '$cars.variants'},
                {'$match': {'cars.variants.short_name': variant_short_name}}
            ]
            data = list(self.brands_col.aggregate(pipeline))[0]
            model_data = data['cars']
            variant_data = model_data['variants']
            row = {
                'brand': data['name'],
                'model': model_data['name'],
                'variant': variant_data['name'],
                'fuel_type': variant_data['fuel_type'],
                'transmission_type': variant_data['transmission_type'],
                'price': variant_data['price'],
                'short_specs': variant_data['short_specs'],
                'specifications': variant_data['specifications'],
                'features': variant_data['features']
            }
            rows.append(row)
        return rows


if __name__ == '__main__':
    mongodb = MongoDb()
    # print(mongodb.get_models('marutisuzuki'))
    # print(mongodb.get_variants('marutisuzuki', 'dzire'))
    print(mongodb.get_details([
        {'brand': 'marutisuzuki', 'model': 'dzire', 'variant': 'zxiamt'},
        {'brand': 'hyundai', 'model': 'grand-i10-nios', 'variant': 'sportzamt12kappavtvt'},
        {'brand': 'marutisuzuki', 'model': 'swift', 'variant': 'zxiamt'},
        {'brand': 'hyundai', 'model': 'venue', 'variant': 's10petrol'},
    ]))
