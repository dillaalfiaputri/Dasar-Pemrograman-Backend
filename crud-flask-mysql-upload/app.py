from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret123'

# Konfigurasi database MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'viaa'
app.config['MYSQL_DB'] = 'crud_upload_db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = ('png', 'jpg', 'jpeg', 'gif')

mysql = MySQL(app)

# Fungsi untuk memeriksa ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Halaman utama untuk menampilkan data
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stok")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', files=data)

# Menampilkan gambar di folder uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# Halaman untuk menambah data
@app.route('/add', methods=['GET', 'POST'])
def add_file():
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        
        # Cek apakah kode barang sudah ada
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stok WHERE kode = %s", (kode,))
        existing = cur.fetchone()
        
        # Proses upload gambar dan insert data
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("INSERT INTO stok (kode, nama, harga, filename) VALUES (%s, %s, %s, %s)", (kode, nama, harga, filename))
            mysql.connection.commit()
            cur.close()
            flash('Data berhasil ditambahkan!', 'success')
            return redirect(url_for('index'))
        else:
            cur.close()
            flash('File tidak valid! Gunakan format: png, jpg, jpeg, gif', 'warning')
            return redirect(url_for('add_file'))
    
    return render_template('add.html')

# Halaman untuk menghapus data
@app.route('/delete/<id>', methods=['GET'])
def delete_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filename FROM stok WHERE kode = %s", (id,))
    file_data = cur.fetchone()
    if file_data:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[0])
        if os.path.exists(file_path):
            os.remove(file_path)
        cur.execute("DELETE FROM stok WHERE kode = %s", (id,))
        mysql.connection.commit()
        flash('Data berhasil dihapus!', 'success')
    cur.close()
    return redirect(url_for('index'))

# Halaman untuk mengedit data
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_file(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stok WHERE kode = %s", (id,))
    file_data = cur.fetchone()
    
    if not file_data:
        cur.close()
        flash('Data tidak ditemukan!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        kode = request.form['kode']
        nama = request.form['nama']
        harga = request.form['harga']
        
        # Cek apakah kode sudah digunakan oleh barang lain
        cur.execute("SELECT * FROM stok WHERE kode = %s AND kode != %s", (kode, id))
        existing = cur.fetchone()
        
        
        new_file = request.files.get('file')
        
        # Jika ada file baru yang diupload
        if new_file and new_file.filename != '' and allowed_file(new_file.filename):
            # Hapus gambar lama
            if file_data[3]:
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data[3])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Upload gambar baru
            filename = secure_filename(new_file.filename)
            new_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE stok SET kode = %s, nama = %s, harga = %s, filename = %s WHERE kode = %s", 
                       (kode, nama, harga, filename, id))
        else:
            # Update tanpa mengubah gambar
            cur.execute("UPDATE stok SET kode = %s, nama = %s, harga = %s WHERE kode = %s", 
                       (kode, nama, harga, id))
        
        mysql.connection.commit()
        cur.close()
        flash('Data berhasil diupdate!', 'success')
        return redirect(url_for('index'))
    
    cur.close()
    return render_template('edit.html', file=file_data)


if __name__ == '__main__':
    app.run(debug=True)