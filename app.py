import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import html

st.set_page_config(page_title="Sistem Informasi Penjualan Kayu", page_icon="🪵", layout="wide")

DB_NAME = "kayu.db"

def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nama TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS kayu (
        id_kayu INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_kayu TEXT NOT NULL,
        satuan TEXT NOT NULL,
        harga REAL NOT NULL,
        stok INTEGER NOT NULL DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pelanggan (
        id_pelanggan INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pelanggan TEXT NOT NULL,
        no_telepon TEXT,
        alamat TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS penjualan (
        id_penjualan INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT NOT NULL,
        id_pelanggan INTEGER,
        id_user INTEGER,
        total REAL NOT NULL,
        FOREIGN KEY(id_pelanggan) REFERENCES pelanggan(id_pelanggan) ON DELETE SET NULL,
        FOREIGN KEY(id_user) REFERENCES users(id_user) ON DELETE SET NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS detail_penjualan (
        id_detail INTEGER PRIMARY KEY AUTOINCREMENT,
        id_penjualan INTEGER NOT NULL,
        id_kayu INTEGER NOT NULL,
        jumlah INTEGER NOT NULL,
        harga REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY(id_penjualan) REFERENCES penjualan(id_penjualan) ON DELETE CASCADE,
        FOREIGN KEY(id_kayu) REFERENCES kayu(id_kayu) ON DELETE RESTRICT
    )
    """)

    cur.execute("INSERT OR IGNORE INTO users(username,password,nama) VALUES(?,?,?)", ("admin", "admin123", "Administrator"))

    jumlah = cur.execute("SELECT COUNT(*) AS jumlah FROM kayu").fetchone()["jumlah"]

    if jumlah == 0:
        data = [
            ("Kayu Jati", "Batang", 150000, 50),
            ("Kayu Meranti", "Batang", 100000, 40),
            ("Kayu Sengon", "Batang", 75000, 60),
            ("Kayu Mahoni", "Batang", 120000, 35),
            ("Kayu Ulin", "Batang", 200000, 25)
        ]
        cur.executemany("INSERT INTO kayu(nama_kayu,satuan,harga,stok) VALUES(?,?,?,?)", data)

    conn.commit()
    conn.close()

def rupiah(nilai):
    return "Rp {:,.0f}".format(float(nilai)).replace(",", ".")

def login_page():
    st.markdown("""
    <style>
    .judul{text-align:center;font-size:35px;font-weight:bold;margin-top:70px}
    .subjudul{text-align:center;color:#666;margin-bottom:30px}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="judul">🪵 Sistem Informasi Penjualan Kayu</div>', unsafe_allow_html=True)
    st.markdown('<div class="subjudul">Penjualan dan Pengelolaan Stok Kayu Berbasis Web</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        with st.form("login"):
            st.subheader("🔐 Login Admin")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            masuk = st.form_submit_button("Login", use_container_width=True)

            if masuk:
                conn = get_db()
                user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password)).fetchone()
                conn.close()

                if user:
                    st.session_state.login = True
                    st.session_state.user_id = user["id_user"]
                    st.session_state.nama_user = user["nama"]
                    st.session_state.halaman = "Dashboard"
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

        st.info("Login demo: admin / admin123")

def dashboard():
    st.title("📊 Dashboard")
    st.write(f"Selamat datang, **{st.session_state.nama_user}**.")

    conn = get_db()

    jenis_kayu = conn.execute("SELECT COUNT(*) AS x FROM kayu").fetchone()["x"]
    stok = conn.execute("SELECT COALESCE(SUM(stok),0) AS x FROM kayu").fetchone()["x"]
    pelanggan = conn.execute("SELECT COUNT(*) AS x FROM pelanggan").fetchone()["x"]
    transaksi = conn.execute("SELECT COUNT(*) AS x FROM penjualan").fetchone()["x"]
    penjualan = conn.execute("SELECT COALESCE(SUM(total),0) AS x FROM penjualan").fetchone()["x"]

    conn.close()

    a,b,c,d,e = st.columns(5)
    a.metric("🪵 Jenis Kayu", jenis_kayu)
    b.metric("📦 Total Stok", stok)
    c.metric("👥 Pelanggan", pelanggan)
    d.metric("🧾 Transaksi", transaksi)
    e.metric("💰 Penjualan", rupiah(penjualan))

    st.divider()

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("📦 Kondisi Stok")
        conn = get_db()
        df = pd.read_sql_query("SELECT nama_kayu AS 'Nama Kayu',satuan AS 'Satuan',stok AS 'Stok',harga AS 'Harga' FROM kayu ORDER BY stok ASC",conn)
        conn.close()

        if not df.empty:
            df["Harga"] = df["Harga"].apply(rupiah)
            st.dataframe(df,use_container_width=True,hide_index=True)

    with col2:
        st.subheader("🧾 Transaksi Terbaru")
        conn = get_db()
        df = pd.read_sql_query("""
        SELECT p.id_penjualan AS 'ID Transaksi',p.tanggal AS 'Tanggal',
        COALESCE(pl.nama_pelanggan,'-') AS 'Pelanggan',p.total AS 'Total'
        FROM penjualan p
        LEFT JOIN pelanggan pl ON p.id_pelanggan=pl.id_pelanggan
        ORDER BY p.id_penjualan DESC LIMIT 5
        """,conn)
        conn.close()

        if not df.empty:
            df["Total"] = df["Total"].apply(rupiah)
            st.dataframe(df,use_container_width=True,hide_index=True)
        else:
            st.info("Belum ada transaksi.")

def data_kayu():
    st.title("🪵 Data Kayu")

    tab1,tab2 = st.tabs(["📋 Data Kayu","➕ Tambah Kayu"])

    with tab1:
        conn = get_db()
        df = pd.read_sql_query("SELECT id_kayu AS 'ID',nama_kayu AS 'Nama Kayu',satuan AS 'Satuan',harga AS 'Harga',stok AS 'Stok' FROM kayu ORDER BY id_kayu DESC",conn)
        conn.close()

        if df.empty:
            st.info("Belum ada data kayu.")
        else:
            tampil = df.copy()
            tampil["Harga"] = tampil["Harga"].apply(rupiah)
            st.dataframe(tampil,use_container_width=True,hide_index=True)

            st.divider()
            pilihan = st.selectbox("Pilih data untuk diedit/dihapus",df["ID"].tolist())

            conn = get_db()
            data = conn.execute("SELECT * FROM kayu WHERE id_kayu=?",(pilihan,)).fetchone()
            conn.close()

            col1,col2 = st.columns(2)

            with col1:
                with st.form("edit_kayu"):
                    nama = st.text_input("Nama Kayu",data["nama_kayu"])
                    satuan = st.selectbox("Satuan",["Batang","Kubik","Papan","Balok","Lembar"],index=["Batang","Kubik","Papan","Balok","Lembar"].index(data["satuan"]) if data["satuan"] in ["Batang","Kubik","Papan","Balok","Lembar"] else 0)
                    harga = st.number_input("Harga",min_value=0,value=int(data["harga"]),step=1000)
                    stok = st.number_input("Stok",min_value=0,value=int(data["stok"]),step=1)

                    simpan = st.form_submit_button("💾 Simpan Perubahan",use_container_width=True)

                    if simpan:
                        if nama.strip():
                            conn = get_db()
                            conn.execute("UPDATE kayu SET nama_kayu=?,satuan=?,harga=?,stok=? WHERE id_kayu=?",(nama.strip(),satuan,harga,stok,pilihan))
                            conn.commit()
                            conn.close()
                            st.success("Data kayu berhasil diperbarui.")
                            st.rerun()
                        else:
                            st.error("Nama kayu wajib diisi.")

            with col2:
                st.warning("Data kayu yang sudah digunakan pada transaksi tidak dapat dihapus.")

                if st.button("🗑️ Hapus Data",use_container_width=True):
                    conn = get_db()
                    try:
                        conn.execute("DELETE FROM kayu WHERE id_kayu=?",(pilihan,))
                        conn.commit()
                        conn.close()
                        st.success("Data berhasil dihapus.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        conn.close()
                        st.error("Data tidak dapat dihapus karena sudah digunakan dalam transaksi.")

    with tab2:
        with st.form("tambah_kayu"):
            nama = st.text_input("Nama Kayu")
            satuan = st.selectbox("Satuan",["Batang","Kubik","Papan","Balok","Lembar"])
            harga = st.number_input("Harga",min_value=0,value=0,step=1000)
            stok = st.number_input("Stok Awal",min_value=0,value=0,step=1)
            tambah = st.form_submit_button("➕ Tambahkan Kayu",use_container_width=True)

            if tambah:
                if not nama.strip():
                    st.error("Nama kayu wajib diisi.")
                elif harga <= 0:
                    st.error("Harga harus lebih dari 0.")
                else:
                    conn = get_db()
                    conn.execute("INSERT INTO kayu(nama_kayu,satuan,harga,stok) VALUES(?,?,?,?)",(nama.strip(),satuan,harga,stok))
                    conn.commit()
                    conn.close()
                    st.success("Data kayu berhasil ditambahkan.")
                    st.rerun()

def stok_kayu():
    st.title("📦 Stok Kayu")

    conn = get_db()
    df = pd.read_sql_query("SELECT id_kayu AS 'ID',nama_kayu AS 'Nama Kayu',satuan AS 'Satuan',stok AS 'Stok',harga AS 'Harga' FROM kayu ORDER BY stok ASC",conn)
    conn.close()

    if df.empty:
        st.info("Belum ada data stok.")
        return

    def status(x):
        if x <= 5:
            return "🔴 Sangat Rendah"
        if x <= 10:
            return "🟠 Rendah"
        return "🟢 Aman"

    tampil = df.copy()
    tampil["Status"] = tampil["Stok"].apply(status)
    tampil["Harga"] = tampil["Harga"].apply(rupiah)

    st.dataframe(tampil,use_container_width=True,hide_index=True)

    a,b,c = st.columns(3)
    a.metric("🔴 Sangat Rendah",len(df[df["Stok"]<=5]))
    b.metric("🟠 Rendah",len(df[(df["Stok"]>5)&(df["Stok"]<=10)]))
    c.metric("🟢 Aman",len(df[df["Stok"]>10]))

def pelanggan():
    st.title("👥 Data Pelanggan")

    tab1,tab2 = st.tabs(["📋 Data Pelanggan","➕ Tambah Pelanggan"])

    with tab1:
        conn = get_db()
        df = pd.read_sql_query("SELECT id_pelanggan AS 'ID',nama_pelanggan AS 'Nama Pelanggan',no_telepon AS 'No. Telepon',alamat AS 'Alamat' FROM pelanggan ORDER BY id_pelanggan DESC",conn)
        conn.close()

        if df.empty:
            st.info("Belum ada pelanggan.")
        else:
            st.dataframe(df,use_container_width=True,hide_index=True)

            st.divider()
            pilihan = st.selectbox("Pilih pelanggan",df["ID"].tolist())

            conn = get_db()
            data = conn.execute("SELECT * FROM pelanggan WHERE id_pelanggan=?",(pilihan,)).fetchone()
            conn.close()

            col1,col2 = st.columns(2)

            with col1:
                with st.form("edit_pelanggan"):
                    nama = st.text_input("Nama Pelanggan",data["nama_pelanggan"])
                    telepon = st.text_input("No. Telepon",data["no_telepon"] or "")
                    alamat = st.text_area("Alamat",data["alamat"] or "")
                    simpan = st.form_submit_button("💾 Simpan Perubahan",use_container_width=True)

                    if simpan:
                        conn = get_db()
                        conn.execute("UPDATE pelanggan SET nama_pelanggan=?,no_telepon=?,alamat=? WHERE id_pelanggan=?",(nama.strip(),telepon.strip(),alamat.strip(),pilihan))
                        conn.commit()
                        conn.close()
                        st.success("Data pelanggan berhasil diperbarui.")
                        st.rerun()

            with col2:
                if st.button("🗑️ Hapus Pelanggan",use_container_width=True):
                    conn = get_db()
                    conn.execute("DELETE FROM pelanggan WHERE id_pelanggan=?",(pilihan,))
                    conn.commit()
                    conn.close()
                    st.success("Pelanggan berhasil dihapus.")
                    st.rerun()

    with tab2:
        with st.form("tambah_pelanggan"):
            nama = st.text_input("Nama Pelanggan")
            telepon = st.text_input("No. Telepon")
            alamat = st.text_area("Alamat")
            tambah = st.form_submit_button("➕ Tambahkan Pelanggan",use_container_width=True)

            if tambah:
                if not nama.strip():
                    st.error("Nama pelanggan wajib diisi.")
                else:
                    conn = get_db()
                    conn.execute("INSERT INTO pelanggan(nama_pelanggan,no_telepon,alamat) VALUES(?,?,?)",(nama.strip(),telepon.strip(),alamat.strip()))
                    conn.commit()
                    conn.close()
                    st.success("Pelanggan berhasil ditambahkan.")
                    st.rerun()

def penjualan():
    st.title("🛒 Transaksi Penjualan")

    conn = get_db()

    pelanggan_df = pd.read_sql_query("SELECT id_pelanggan,nama_pelanggan FROM pelanggan ORDER BY nama_pelanggan",conn)
    kayu_df = pd.read_sql_query("SELECT id_kayu,nama_kayu,satuan,harga,stok FROM kayu ORDER BY nama_kayu",conn)

    conn.close()

    if pelanggan_df.empty:
        st.warning("Tambahkan pelanggan terlebih dahulu.")
        return

    if kayu_df.empty:
        st.warning("Belum ada data kayu.")
        return

    if "cart" not in st.session_state:
        st.session_state.cart = []

    pelanggan_dict = dict(zip(pelanggan_df["id_pelanggan"],pelanggan_df["nama_pelanggan"]))

    pelanggan_id = st.selectbox("👤 Pilih Pelanggan",list(pelanggan_dict.keys()),format_func=lambda x: pelanggan_dict[x])

    st.divider()
    st.subheader("➕ Tambah Barang")

    col1,col2,col3 = st.columns([3,2,2])

    with col1:
        kayu_id = st.selectbox("Pilih Kayu",kayu_df["id_kayu"].tolist(),format_func=lambda x: f"{kayu_df.loc[kayu_df.id_kayu==x,'nama_kayu'].iloc[0]} | Stok: {kayu_df.loc[kayu_df.id_kayu==x,'stok'].iloc[0]}")

    data = kayu_df[kayu_df["id_kayu"]==kayu_id].iloc[0]

    with col2:
        st.text_input("Harga",rupiah(data["harga"]),disabled=True)

    with col3:
        jumlah = st.number_input("Jumlah",min_value=1,max_value=max(1,int(data["stok"])),value=1)

    subtotal = float(data["harga"])*jumlah
    st.info(f"Subtotal: **{rupiah(subtotal)}**")

    if st.button("➕ Masukkan ke Keranjang",use_container_width=True):
        ditemukan = False

        for item in st.session_state.cart:
            if item["id_kayu"] == int(kayu_id):
                jumlah_baru = item["jumlah"] + int(jumlah)

                if jumlah_baru > int(data["stok"]):
                    st.error("Jumlah melebihi stok.")
                else:
                    item["jumlah"] = jumlah_baru
                    item["subtotal"] = jumlah_baru*float(data["harga"])
                    st.success("Jumlah barang diperbarui.")
                ditemukan = True
                break

        if not ditemukan:
            if int(data["stok"]) <= 0:
                st.error("Stok habis.")
            else:
                st.session_state.cart.append({
                    "id_kayu":int(kayu_id),
                    "nama_kayu":data["nama_kayu"],
                    "satuan":data["satuan"],
                    "harga":float(data["harga"]),
                    "jumlah":int(jumlah),
                    "subtotal":float(subtotal)
                })
                st.success("Barang ditambahkan.")

        st.rerun()

    st.divider()
    st.subheader("🧾 Detail Penjualan")

    if not st.session_state.cart:
        st.info("Keranjang masih kosong.")
        return

    table = []

    for i,item in enumerate(st.session_state.cart):
        table.append({
            "No":i+1,
            "Kayu":item["nama_kayu"],
            "Satuan":item["satuan"],
            "Harga":rupiah(item["harga"]),
            "Jumlah":item["jumlah"],
            "Subtotal":rupiah(item["subtotal"])
        })

    st.dataframe(pd.DataFrame(table),use_container_width=True,hide_index=True)

    total = sum(item["subtotal"] for item in st.session_state.cart)

    st.markdown(f"## Total: {rupiah(total)}")

    pilihan = st.selectbox("Pilih barang untuk dihapus",range(len(st.session_state.cart)),format_func=lambda x: st.session_state.cart[x]["nama_kayu"])

    if st.button("🗑️ Hapus Barang"):
        st.session_state.cart.pop(pilihan)
        st.rerun()

    if st.button("💾 SIMPAN TRANSAKSI",type="primary",use_container_width=True):
        conn = get_db()

        try:
            for item in st.session_state.cart:
                stok = conn.execute("SELECT stok FROM kayu WHERE id_kayu=?",(item["id_kayu"],)).fetchone()["stok"]

                if stok < item["jumlah"]:
                    raise Exception(f"Stok {item['nama_kayu']} tidak mencukupi.")

            tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor = conn.execute(
                "INSERT INTO penjualan(tanggal,id_pelanggan,id_user,total) VALUES(?,?,?,?)",
                (tanggal,pelanggan_id,st.session_state.user_id,total)
            )

            id_transaksi = cursor.lastrowid

            for item in st.session_state.cart:
                conn.execute(
                    "INSERT INTO detail_penjualan(id_penjualan,id_kayu,jumlah,harga,subtotal) VALUES(?,?,?,?,?)",
                    (id_transaksi,item["id_kayu"],item["jumlah"],item["harga"],item["subtotal"])
                )

                conn.execute(
                    "UPDATE kayu SET stok=stok-? WHERE id_kayu=?",
                    (item["jumlah"],item["id_kayu"])
                )

            conn.commit()
            st.session_state.cart = []

            st.success(f"Transaksi berhasil disimpan. ID Transaksi: {id_transaksi}")
            st.session_state.halaman = "Riwayat Transaksi"
            st.rerun()

        except Exception as e:
            conn.rollback()
            st.error(f"Transaksi gagal: {e}")

        finally:
            conn.close()

def riwayat():
    st.title("📜 Riwayat Transaksi")

    conn = get_db()

    df = pd.read_sql_query("""
    SELECT p.id_penjualan AS 'ID Transaksi',
    p.tanggal AS 'Tanggal',
    COALESCE(pl.nama_pelanggan,'-') AS 'Pelanggan',
    COALESCE(u.nama,'-') AS 'Admin',
    p.total AS 'Total'
    FROM penjualan p
    LEFT JOIN pelanggan pl ON p.id_pelanggan=pl.id_pelanggan
    LEFT JOIN users u ON p.id_user=u.id_user
    ORDER BY p.id_penjualan DESC
    """,conn)

    conn.close()

    if df.empty:
        st.info("Belum ada transaksi.")
        return

    tampil = df.copy()
    tampil["Total"] = tampil["Total"].apply(rupiah)

    st.dataframe(tampil,use_container_width=True,hide_index=True)

    st.divider()

    id_transaksi = st.selectbox("Pilih transaksi",df["ID Transaksi"].tolist())

    conn = get_db()

    transaksi = conn.execute("""
    SELECT p.*,COALESCE(pl.nama_pelanggan,'-') AS pelanggan,
    COALESCE(pl.no_telepon,'-') AS telepon,
    COALESCE(u.nama,'-') AS admin
    FROM penjualan p
    LEFT JOIN pelanggan pl ON p.id_pelanggan=pl.id_pelanggan
    LEFT JOIN users u ON p.id_user=u.id_user
    WHERE p.id_penjualan=?
    """,(id_transaksi,)).fetchone()

    detail = conn.execute("""
    SELECT d.*,k.nama_kayu,k.satuan
    FROM detail_penjualan d
    JOIN kayu k ON d.id_kayu=k.id_kayu
    WHERE d.id_penjualan=?
    """,(id_transaksi,)).fetchall()

    conn.close()

    st.subheader("🧾 Nota Penjualan")

    col1,col2 = st.columns(2)

    col1.write(f"**ID Transaksi:** {transaksi['id_penjualan']}")
    col1.write(f"**Tanggal:** {transaksi['tanggal']}")
    col2.write(f"**Pelanggan:** {transaksi['pelanggan']}")
    col2.write(f"**Admin:** {transaksi['admin']}")

    data=[]

    for item in detail:
        data.append({
            "Kayu":item["nama_kayu"],
            "Satuan":item["satuan"],
            "Jumlah":item["jumlah"],
            "Harga":rupiah(item["harga"]),
            "Subtotal":rupiah(item["subtotal"])
        })

    st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
    st.markdown(f"## Total: {rupiah(transaksi['total'])}")

    nota = "========================================\n"
    nota += "          NOTA PENJUALAN KAYU\n"
    nota += "========================================\n"
    nota += f"ID Transaksi : {transaksi['id_penjualan']}\n"
    nota += f"Tanggal      : {transaksi['tanggal']}\n"
    nota += f"Pelanggan    : {transaksi['pelanggan']}\n"
    nota += "----------------------------------------\n"

    for item in detail:
        nota += f"{item['nama_kayu']} - {item['jumlah']} {item['satuan']}\n"
        nota += f"{rupiah(item['harga'])} x {item['jumlah']} = {rupiah(item['subtotal'])}\n"

    nota += "----------------------------------------\n"
    nota += f"TOTAL: {rupiah(transaksi['total'])}\n"
    nota += "========================================\n"

    st.download_button("⬇️ Download Nota",nota,f"nota_{id_transaksi}.txt","text/plain",use_container_width=True)

def laporan():
    st.title("📑 Laporan")

    tab1,tab2 = st.tabs(["💰 Penjualan","📦 Stok"])

    with tab1:
        conn = get_db()

        df = pd.read_sql_query("""
        SELECT p.id_penjualan AS 'ID Transaksi',
        p.tanggal AS 'Tanggal',
        COALESCE(pl.nama_pelanggan,'-') AS 'Pelanggan',
        p.total AS 'Total'
        FROM penjualan p
        LEFT JOIN pelanggan pl ON p.id_pelanggan=pl.id_pelanggan
        ORDER BY p.id_penjualan DESC
        """,conn)

        conn.close()

        if df.empty:
            st.info("Belum ada penjualan.")
        else:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])

            awal = st.date_input("Tanggal Awal",df["Tanggal"].min().date())
            akhir = st.date_input("Tanggal Akhir",df["Tanggal"].max().date())

            hasil = df[(df["Tanggal"].dt.date>=awal)&(df["Tanggal"].dt.date<=akhir)].copy()

            a,b = st.columns(2)
            a.metric("Jumlah Transaksi",len(hasil))
            b.metric("Total Penjualan",rupiah(hasil["Total"].sum()))

            hasil["Tanggal"] = hasil["Tanggal"].dt.strftime("%d-%m-%Y %H:%M")
            hasil["Total"] = hasil["Total"].apply(rupiah)

            st.dataframe(hasil,use_container_width=True,hide_index=True)

            csv = hasil.to_csv(index=False).encode("utf-8")

            st.download_button("⬇️ Download Laporan Penjualan",csv,"laporan_penjualan.csv","text/csv",use_container_width=True)

    with tab2:
        conn = get_db()

        df = pd.read_sql_query("SELECT id_kayu AS 'ID',nama_kayu AS 'Nama Kayu',satuan AS 'Satuan',stok AS 'Stok',harga AS 'Harga' FROM kayu ORDER BY stok ASC",conn)

        conn.close()

        if df.empty:
            st.info("Belum ada data stok.")
        else:
            def status(x):
                if x<=5:
                    return "Sangat Rendah"
                if x<=10:
                    return "Rendah"
                return "Aman"

            laporan_stok = df.copy()
            laporan_stok["Status"] = laporan_stok["Stok"].apply(status)

            tampil = laporan_stok.copy()
            tampil["Harga"] = tampil["Harga"].apply(rupiah)

            st.dataframe(tampil,use_container_width=True,hide_index=True)

            csv = laporan_stok.to_csv(index=False).encode("utf-8")

            st.download_button("⬇️ Download Laporan Stok",csv,"laporan_stok.csv","text/csv",use_container_width=True)

def sidebar():
    with st.sidebar:
        st.markdown("# 🪵 Sistem Kayu")
        st.caption("Penjualan dan Pengelolaan Stok Kayu")
        st.divider()
        st.write(f"👤 **{st.session_state.nama_user}**")
        st.divider()

        menu = st.radio(
            "MENU",
            ["Dashboard","Data Kayu","Stok Kayu","Pelanggan","Penjualan","Riwayat Transaksi","Laporan"],
            index=["Dashboard","Data Kayu","Stok Kayu","Pelanggan","Penjualan","Riwayat Transaksi","Laporan"].index(st.session_state.halaman)
        )

        st.session_state.halaman = menu

        st.divider()

        if st.button("🚪 Logout",use_container_width=True):
            st.session_state.login=False
            st.session_state.user_id=None
            st.session_state.nama_user=None
            st.session_state.cart=[]
            st.rerun()

init_db()

if "login" not in st.session_state:
    st.session_state.login=False

if "halaman" not in st.session_state:
    st.session_state.halaman="Dashboard"

if "user_id" not in st.session_state:
    st.session_state.user_id=None

if "nama_user" not in st.session_state:
    st.session_state.nama_user=None

if not st.session_state.login:
    login_page()
else:
    sidebar()

    if st.session_state.halaman=="Dashboard":
        dashboard()
    elif st.session_state.halaman=="Data Kayu":
        data_kayu()
    elif st.session_state.halaman=="Stok Kayu":
        stok_kayu()
    elif st.session_state.halaman=="Pelanggan":
        pelanggan()
    elif st.session_state.halaman=="Penjualan":
        penjualan()
    elif st.session_state.halaman=="Riwayat Transaksi":
        riwayat()
    elif st.session_state.halaman=="Laporan":
        laporan()
