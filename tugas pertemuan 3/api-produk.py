from flask import Flask, jsonify
import json

app = Flask(__name__)

def baca_data():
    with open('data_produk.json', 'r') as file:
        return json.load(file)

@app.route('/')
def home():
    return jsonify({
        "message": "Selamat Datang Di Produk UMKM"
    })

@app.route('/produk/snack')
def semua_snack():
    data = baca_data()
    return jsonify({
        "message": "Halaman Produk Semua Snack",
        "data": data['snack']
    })

@app.route('/produk/drink')
def semua_drink():
    data = baca_data()
    return jsonify({
        "message": "Halaman Produk Semua Soft Drink",
        "data": data['drink']
    })

@app.route('/produk/snack/<int:id>')
def snack_by_id(id):
    data = baca_data()
    snack = None
    
    for item in data['snack']:
        if item['id'] == id:
            snack = item
            break
    
    if snack:
        return jsonify({
            "message": f"Halaman Produk Snack dengan id = {id}",
            "data": snack
        })
    else:
        return jsonify({"message": "Produk tidak ditemukan"}), 404

@app.route('/produk/drink/<int:id>')
def drink_by_id(id):
    data = baca_data()
    drink = None
    
    for item in data['drink']:
        if item['id'] == id:
            drink = item
            break
    
    if drink:
        return jsonify({
            "message": f"Halaman Produk Soft Drink dengan id = {id}",
            "data": drink
        })
    else:
        return jsonify({"message": "Produk tidak ditemukan"}), 404

if __name__ == '__main__':
    app.run(debug=True)