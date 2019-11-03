from flask import Flask, request
from carwler.mongo_db import MongoDb
import json

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/brands', methods=['GET'])
def brands():
    mongo_db = MongoDb()
    return json.dumps(mongo_db.get_brands(), indent=4)


@app.route('/models', methods=['GET'])
def models():
    brand = request.args.get('brand')
    mongo_db = MongoDb()
    return json.dumps(mongo_db.get_models(brand), indent=4)


@app.route('/variants', methods=['GET'])
def variants():
    brand = request.args.get('brand')
    model = request.args.get('model')
    mongo_db = MongoDb()
    return json.dumps(mongo_db.get_variants(brand, model), indent=4)


@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json(force=True)
    mongo_db = MongoDb()
    return json.dumps(mongo_db.get_details(data), indent=4)


if __name__ == '__main__':
    app.run(debug=True)
