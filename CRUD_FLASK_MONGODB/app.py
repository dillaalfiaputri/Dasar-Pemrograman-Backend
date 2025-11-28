from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from pymongo import MongoClient
from bson.objectid import ObjectId
import os, math
from werkzeug.utils import secure_filename

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = 'viacantik'

# Konfigurasi upload foto
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Buat folder uploads jika belum ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Koneksi MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["crud_apotik"]
collection = db["items"]

# Cek ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =======================
# INDEX + PAGINATION
# =======================
@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    skip = (page - 1) * per_page

    # Filter pencarian
    query = {}
    if search_query:
        query = {"nama": {"$regex": search_query, "$options": "i"}}

    # Hitung total data
    total_rows = collection.count_documents(query)
    total_pages = math.ceil(total_rows / per_page)

    # Ambil data
    items = collection.find(query).skip(skip).limit(per_page)

    return render_template(
        'index.html',
        items=items,
        search_query=search_query,
        page=page,
        total_pages=total_pages
    )


# =======================
# ADD DATA
# =======================
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        jumlah = request.form['jumlah']

        foto = None
        if 'foto' in request.files:
            file = request.files['foto']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                filename = f"{kode}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto = filename

        collection.insert_one({
            'kode': kode,
            'nama': nama,
            'harga': harga,
            'jumlah': jumlah,
            'foto': foto
        })

        flash("Data berhasil ditambahkan!", "success")
        return redirect(url_for('index'))

    return render_template('add.html')


# =======================
# EDIT DATA
# =======================
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    item = collection.find_one({'_id': ObjectId(id)})

    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        jumlah = request.form['jumlah']

        foto = item.get('foto')

        file = request.files.get('foto')
        if file and allowed_file(file.filename):
            # Hapus foto lama
            if foto:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], foto)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            filename = f"{kode}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            foto = filename

        collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'kode': kode,
                'nama': nama,
                'harga': harga,
                'jumlah': jumlah,
                'foto': foto
            }}
        )

        flash("Data berhasil diperbarui!", "success")
        return redirect(url_for('index'))

    return render_template('edit.html', item=item)


# =======================
# DELETE DATA
# =======================
@app.route('/delete/<id>')
def delete(id):
    item = collection.find_one({'_id': ObjectId(id)})

    if item and item.get('foto'):
        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], item['foto'])
        if os.path.exists(foto_path):
            os.remove(foto_path)

    collection.delete_one({'_id': ObjectId(id)})
    flash("Data berhasil dihapus!", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
