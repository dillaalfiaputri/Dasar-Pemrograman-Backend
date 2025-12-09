from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mysqldb import MySQL
import os, math
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'viacantik'

# Konfigurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'apotik_db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = ('png', 'jpg', 'jpeg')

mysql = MySQL(app)

# Fungsi untuk cek ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# index
@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()

    # Hitung total data sesuai pencarian
    if search_query:
        cur.execute("""
            SELECT COUNT(*) FROM obat
            WHERE nama_obat LIKE %s
        """, (f"%{search_query}%",))
    else:
        cur.execute("SELECT COUNT(*) FROM obat")
    total_rows = cur.fetchone()[0]
    total_pages = math.ceil(total_rows / per_page)

    # Ambil data berdasarkan pencarian + pagination
    if search_query:
        cur.execute("""
            SELECT * FROM obat
            WHERE nama_obat LIKE %s
            LIMIT %s OFFSET %s
        """, (f"%{search_query}%", per_page, offset))
    else:
        cur.execute("SELECT * FROM obat LIMIT %s OFFSET %s", (per_page, offset))

    data = cur.fetchall()
    cur.close()

    return render_template(
        'index.html',
        files=data,
        search_query=search_query,
        page=page,
        total_pages=total_pages
    )

# upload file
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# add data
@app.route('/add', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        kode_obat = request.form['kode_obat']
        nama_obat = request.form['nama_obat']
        jenis = request.form['jenis']
        harga = request.form['harga']
        stok = request.form['stok']

        cur = mysql.connection.cursor()

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("INSERT INTO obat (kode_obat, nama_obat, jenis, harga, stok, filename) VALUES (%s, %s, %s, %s, %s, %s)",
                        (kode_obat, nama_obat, jenis, harga, stok, filename))
            mysql.connection.commit()
            cur.close()
            flash('Data berhasil ditambahkan!', 'success')
            return redirect(url_for('index'))
        else:
            flash('File tidak valid! Gunakan format: png, jpg, jpeg', 'warning')
            cur.close()
            return redirect(url_for('add_file'))

    return render_template('add.html')

# delete data
@app.route('/delete/<id>', methods=['GET'])
def delete_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM obat WHERE kode_obat = %s", (id,))
    file_data = cur.fetchone()
    if file_data:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[0])
        if os.path.exists(file_path):
            os.remove(file_path)
        cur.execute("DELETE FROM obat WHERE kode_obat = %s", (id,))
        mysql.connection.commit()
        flash('Data berhasil dihapus!', 'success')
    cur.close()
    return redirect(url_for('index'))

# edit data
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM obat WHERE kode_obat = %s", (id,))
    file_data = cur.fetchone()

    if not file_data:
        cur.close()
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        kode_obat = request.form['kode_obat']
        nama_obat = request.form['nama_obat']
        jenis = request.form['jenis']
        harga = request.form['harga']
        stok = request.form['stok']
        new_file = request.files.get('file')

        # Jika ada file baru
        if new_file and new_file.filename != '' and allowed_file(new_file.filename):
            # Hapus file lama
            if file_data[3]:
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[5])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("""
            UPDATE obat SET
            kode_obat=%s, nama_obat=%s, jenis=%s, harga=%s, stok=%s, filename=%s 
            WHERE kode_obat=%s
            """, (kode_obat, nama_obat, jenis, harga, stok, filename, id))

        else:
            # Tanpa ubah gambar
            cur.execute("""
            UPDATE obat SET 
            kode_obat=%s, nama_obat=%s, jenis=%s, harga=%s, stok=%s
            WHERE kode_obat=%s
            """, (kode_obat, nama_obat, jenis, harga, stok, id))


        mysql.connection.commit()
        cur.close()
        flash('Data berhasil diupdate!', 'success')
        return redirect(url_for('index'))

    cur.close()
    return render_template('edit.html', file=file_data)


if __name__ == '__main__':
    app.run(debug=True)