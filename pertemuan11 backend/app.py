from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

# =========================
# KONFIGURASI APLIKASI
# =========================
app = Flask(__name__)

UPLOAD_FOLDER = "static/img"
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# KONEKSI DATABASE
# =========================
def db():
    conn = sqlite3.connect(r"C:\Users\ASUS\apotik.db")
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# ROUTE : CREATE
# =========================
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        kode = request.form["kode"]
        nama = request.form["nama"]
        harga = request.form["harga"]
        jumlah = request.form["jumlah"]

        # upload foto
        foto = request.files.get("foto")
        filename = None
        if foto and foto.filename != "":
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = db()
        conn.execute("""
            INSERT INTO obat (kode, nama, harga, jumlah, foto)
            VALUES (?, ?, ?, ?, ?)
        """, (kode, nama, harga, jumlah, filename))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add.html")

# =========================
# ROUTE : UPDATE
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = db()
    stok = conn.execute("SELECT * FROM obat WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        kode = request.form["kode"]
        nama = request.form["nama"]
        harga = request.form["harga"]
        jumlah = request.form["jumlah"]

        foto = request.files.get("foto")
        filename = stok["foto"]

        if foto and foto.filename != "":
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn.execute("""
            UPDATE obat 
            SET kode=?, nama=?, harga=?, jumlah=?, foto=? 
            WHERE id=?
        """, (kode, nama, harga, jumlah, filename, id))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    conn.close()
    return render_template("edit.html", stoks=stok)

# =========================
# ROUTE : DELETE
# =========================
@app.route("/delete/<int:id>")
def delete(id):
    conn = db()
    conn.execute("DELETE FROM obat WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/")
def index():
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    limit = 5                      # jumlah data per halaman
    offset = (page - 1) * limit

    conn = db()

    if search:
        rows = conn.execute("""
            SELECT * FROM obat
            WHERE nama LIKE ? OR kode LIKE ?
            LIMIT ? OFFSET ?
        """, (f"%{search}%", f"%{search}%", limit, offset)).fetchall()

        total = conn.execute("""
            SELECT COUNT(*) FROM obat
            WHERE nama LIKE ? OR kode LIKE ?
        """, (f"%{search}%", f"%{search}%")).fetchone()[0]
    else:
        rows = conn.execute("""
            SELECT * FROM obat
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

        total = conn.execute("SELECT COUNT(*) FROM obat").fetchone()[0]

    conn.close()

    total_pages = (total + limit - 1) // limit

    return render_template(
        "index.html",
        stoks=rows,
        page=page,
        total_pages=total_pages,
        search=search
    )


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)
