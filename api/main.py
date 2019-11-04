from flask import Flask, request, jsonify
from flask_cors import CORS
from carwler.mongo_db import MongoDb

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/brands', methods=['GET'])
def brands():
    mongo_db = MongoDb()
    return jsonify(mongo_db.get_brands())


@app.route('/models', methods=['GET'])
def models():
    brand = request.args.get('brand')
    mongo_db = MongoDb()
    return jsonify(mongo_db.get_models(brand))


@app.route('/variants', methods=['GET'])
def variants():
    brand = request.args.get('brand')
    model = request.args.get('model')
    mongo_db = MongoDb()
    return jsonify(mongo_db.get_variants(brand, model))


@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json(force=True)
    mongo_db = MongoDb()
    return jsonify(mongo_db.get_details(data))


if __name__ == '__main__':
    app.run(debug=True)
