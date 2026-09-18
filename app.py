import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# =========================================================
# KONFIGURASI
# =========================================================
st.set_page_config(
    page_title="KAYU • Timber ERP",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="auto",
)

DB_NAME = "kayu.db"

# =========================================================
# DATABASE
# =========================================================
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
        CREATE TABLE IF NOT EXISTS pemasok (
            id_pemasok INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pemasok TEXT NOT NULL,
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
            total REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(id_pelanggan) REFERENCES pelanggan(id_pelanggan)
                ON DELETE SET NULL,
            FOREIGN KEY(id_user) REFERENCES users(id_user)
                ON DELETE SET NULL
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
            FOREIGN KEY(id_penjualan) REFERENCES penjualan(id_penjualan)
                ON DELETE CASCADE,
            FOREIGN KEY(id_kayu) REFERENCES kayu(id_kayu)
                ON DELETE RESTRICT
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO users (username, password, nama)
        VALUES (?, ?, ?)
    """, ("admin", "admin123", "Rafi Ahmad"))

    if cur.execute("SELECT COUNT(*) FROM kayu").fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO kayu (nama_kayu, satuan, harga, stok)
            VALUES (?, ?, ?, ?)
        """, [
            ("Kayu Jati", "Batang", 150000, 50),
            ("Kayu Meranti", "Batang", 100000, 40),
            ("Kayu Sengon", "Batang", 75000, 60),
            ("Kayu Mahoni", "Batang", 120000, 35),
            ("Kayu Ulin", "Batang", 200000, 25),
        ])

    conn.commit()
    conn.close()


# =========================================================
# HELPER
# =========================================================
def rupiah(nilai):
    return "Rp {:,.0f}".format(float(nilai)).replace(",", ".")


def query_df(sql, params=()):
    conn = get_db()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def stok_status(stok):
    if stok <= 5:
        return "Sangat Rendah"
    if stok <= 10:
        return "Rendah"
    return "Aman"


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --brown: #3D2314;
        --brown-dark: #250F03;
        --orange: #FE932C;
        --cream: #F9F9FF;
        --muted: #6F625A;
        --line: #E9E1DB;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: var(--cream);
    }

    [data-testid="stHeader"] {
        background: rgba(249,249,255,.92);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(61,35,20,.08);
    }

    [data-testid="stSidebar"] {
        background: var(--brown-dark);
        border-right: 0;
    }

    [data-testid="stSidebar"] * {
        color: #FFF8F2;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #EADFD7;
        font-weight: 600;
    }

    [data-testid="stSidebar"] [role="radiogroup"] > label {
        padding: 10px 12px;
        border-radius: 9px;
        margin: 2px 0;
    }

    [data-testid="stSidebar"] [role="radiogroup"] > label:hover {
        background: rgba(255,255,255,.08);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        color: #FFF;
        letter-spacing: .04em;
    }

    .brand-box {
        padding: 8px 4px 20px;
    }

    .brand-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: .08em;
        color: white;
    }

    .brand-sub {
        font-size: 12px;
        color: #D5C8BE;
        margin-top: -4px;
    }

    .user-box {
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
    }

    .topbar {
        padding: 2px 0 20px;
    }

    .eyebrow {
        color: var(--orange);
        font-size: 12px;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .page-title {
        color: var(--brown);
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
    }

    .page-subtitle {
        color: var(--muted);
        margin-top: 6px;
        font-size: 14px;
    }

    .card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 3px 14px rgba(61,35,20,.04);
    }

    .metric-card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 18px;
        min-height: 116px;
        box-shadow: 0 3px 14px rgba(61,35,20,.04);
    }

    .metric-label {
        color: var(--muted);
        font-size: 12px;
        font-weight: 700;
    }

    .metric-value {
        color: var(--brown);
        font-size: 25px;
        font-weight: 800;
        margin-top: 8px;
    }

    .section-title {
        color: var(--brown);
        font-size: 18px;
        font-weight: 800;
        margin: 4px 0 12px;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        border-radius: 9px;
        font-weight: 700;
        min-height: 42px;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: var(--brown);
        border-color: var(--brown);
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stDateInput"] input {
        background: #FFFFFF !important;
        color: var(--brown) !important;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 15px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    .login-logo {
        text-align: center;
        color: var(--brown);
        font-size: 34px;
        font-weight: 800;
        margin-top: 7vh;
    }

    .login-desc {
        text-align: center;
        color: var(--muted);
        margin: 8px 0 24px;
    }

    /* Login form */
    [data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
        padding: 28px !important;
        box-shadow: 0 8px 28px rgba(61,35,20,.08) !important;
    }

    [data-testid="stForm"] label {
        color: var(--brown) !important;
        font-weight: 600 !important;
    }

    [data-testid="stForm"] input {
        background: #FFFFFF !important;
        color: var(--brown) !important;
        border: 1px solid #D9CEC5 !important;
        border-radius: 9px !important;
        min-height: 44px !important;
    }

    [data-testid="stForm"] input::placeholder {
        color: #8B817A !important;
        opacity: 1 !important;
    }

    [data-testid="stFormSubmitButton"] button {
        background: var(--brown) !important;
        border: 1px solid var(--brown) !important;
        color: #FFFFFF !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        min-height: 44px !important;
    }

    [data-testid="stFormSubmitButton"] button:hover {
        background: var(--brown-dark) !important;
        border-color: var(--brown-dark) !important;
        color: #FFFFFF !important;
    }

    .login-hint {
        text-align: center;
        color: var(--muted);
        font-size: 12px;
        margin-top: 14px;
    }

    @media (max-width: 700px) {
        .page-title { font-size: 25px; }
        .metric-value { font-size: 21px; }
        .topbar { padding-bottom: 12px; }
        .card, .metric-card { padding: 14px; }
    }
    </style>
    """, unsafe_allow_html=True)


# =========================================================
# SESSION
# =========================================================
defaults = {
    "is_logged_in": False,
    "current_user_id": None,
    "current_user_name": None,
    "page": "Dashboard",
    "cart_items": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOGIN
# =========================================================
def login_page():
    st.markdown('<div class="login-logo">🪵 KAYU</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-desc">Sistem Informasi Penjualan dan Pengelolaan Stok Kayu</div>',
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 2, 1])

    with center:
        with st.form("login_form", clear_on_submit=False):
            st.markdown(
                '<div style="font-size:20px;font-weight:800;color:#3D2314;margin-bottom:4px;">'
                'Masuk ke Sistem</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div style="font-size:13px;color:#6F625A;margin-bottom:18px;">'
                'Gunakan akun admin untuk mengakses dashboard.</div>',
                unsafe_allow_html=True
            )

            username = st.text_input(
                "Username",
                placeholder="Masukkan username"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password"
            )
            submitted = st.form_submit_button(
                "Masuk",
                type="primary",
                use_container_width=True
            )

            if submitted:
                if not username.strip() or not password:
                    st.error("Username dan password wajib diisi.")
                else:
                    conn = get_db()
                    user = conn.execute("""
                        SELECT * FROM users
                        WHERE username = ? AND password = ?
                    """, (username.strip(), password)).fetchone()
                    conn.close()

                    if user:
                        st.session_state.is_logged_in = True
                        st.session_state.current_user_id = user["id_user"]
                        st.session_state.current_user_name = user["nama"]
                        st.session_state.page = "Dashboard"
                        st.session_state.cart_items = []
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")

        st.markdown(
            '<div class="login-hint">Akun demo: <b>admin</b> / <b>admin123</b></div>',
            unsafe_allow_html=True
        )


# =========================================================
# SIDEBAR
# =========================================================
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="brand-box">
            <div class="brand-title">🌲 KAYU</div>
            <div class="brand-sub">Sistem Informasi</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f'<div class="user-box"><b>{st.session_state.current_user_name}</b><br>'
            '<span style="font-size:12px;color:#D5C8BE">Administrator</span></div>',
            unsafe_allow_html=True
        )

        menu = ["Dashboard", "Barang", "Pembelian", "Penjualan",
                "Pelanggan & Pemasok", "Laporan"]

        selected = st.radio(
            "MENU UTAMA",
            menu,
            index=menu.index(st.session_state.page) if st.session_state.page in menu else 0,
            key="main_navigation"
        )
        st.session_state.page = selected

        st.markdown("---")
        st.caption("Pengaturan")
        st.caption("v1.2.0 • Timber ERP")

        if st.button("Keluar", use_container_width=True, key="logout"):
            st.session_state.is_logged_in = False
            st.session_state.current_user_id = None
            st.session_state.current_user_name = None
            st.session_state.cart_items = []
            st.session_state.page = "Dashboard"
            st.rerun()


# =========================================================
# HEADER
# =========================================================
def page_header(title, subtitle):
    st.markdown(
        f'<div class="topbar"><div class="eyebrow">Operasional Kayu</div>'
        f'<div class="page-title">{title}</div>'
        f'<div class="page-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True
    )


# =========================================================
# DASHBOARD
# =========================================================
def dashboard():
    page_header("Dashboard", "Ringkasan aktivitas penjualan dan persediaan.")

    jenis = query_df("SELECT COUNT(*) n FROM kayu").iloc[0, 0]
    stok = query_df("SELECT COALESCE(SUM(stok),0) n FROM kayu").iloc[0, 0]
    pelanggan = query_df("SELECT COUNT(*) n FROM pelanggan").iloc[0, 0]
    transaksi = query_df("SELECT COUNT(*) n FROM penjualan").iloc[0, 0]
    omzet = query_df("SELECT COALESCE(SUM(total),0) n FROM penjualan").iloc[0, 0]

    cols = st.columns(5)
    cards = [
        ("Jenis Kayu", jenis),
        ("Total Stok", stok),
        ("Pelanggan", pelanggan),
        ("Transaksi", transaksi),
        ("Total Penjualan", rupiah(omzet)),
    ]
    for col, (label, value) in zip(cols, cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div></div>',
                unsafe_allow_html=True
            )

    st.write("")
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="section-title">Kondisi Stok</div>', unsafe_allow_html=True)
        df = query_df("""
            SELECT nama_kayu AS 'Nama Kayu', satuan AS 'Satuan',
                   stok AS 'Stok', harga AS 'Harga'
            FROM kayu ORDER BY stok ASC
        """)
        if df.empty:
            st.info("Belum ada data kayu.")
        else:
            df["Harga"] = df["Harga"].apply(rupiah)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with right:
        st.markdown('<div class="section-title">Transaksi Terbaru</div>', unsafe_allow_html=True)
        df = query_df("""
            SELECT p.id_penjualan AS 'ID', p.tanggal AS 'Tanggal',
                   COALESCE(pl.nama_pelanggan,'-') AS 'Pelanggan',
                   p.total AS 'Total'
            FROM penjualan p
            LEFT JOIN pelanggan pl ON p.id_pelanggan = pl.id_pelanggan
            ORDER BY p.id_penjualan DESC LIMIT 5
        """)
        if df.empty:
            st.info("Belum ada transaksi.")
        else:
            df["Total"] = df["Total"].apply(rupiah)
            st.dataframe(df, use_container_width=True, hide_index=True)


# =========================================================
# BARANG
# =========================================================
def barang_page():
    page_header("Barang", "Kelola data kayu, harga, dan persediaan.")

    df = query_df("""
        SELECT id_kayu AS 'ID', nama_kayu AS 'Nama Kayu',
               satuan AS 'Satuan', harga AS 'Harga', stok AS 'Stok'
        FROM kayu ORDER BY id_kayu DESC
    """)

    a, b, c = st.columns(3)
    with a:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Jenis Barang</div>'
                    f'<div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Stok</div>'
                    f'<div class="metric-value">{int(df["Stok"].sum()) if not df.empty else 0}</div></div>',
                    unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Stok Rendah</div>'
                    f'<div class="metric-value">{int((df["Stok"] <= 10).sum()) if not df.empty else 0}</div></div>',
                    unsafe_allow_html=True)

    st.write("")
    tab_list, tab_add, tab_edit = st.tabs(["Daftar Barang", "Tambah Barang", "Edit / Hapus"])

    with tab_list:
        search = st.text_input("Cari barang", placeholder="Cari nama kayu...")
        view = df.copy()
        if search:
            view = view[view["Nama Kayu"].str.contains(search, case=False, na=False)]
        if view.empty:
            st.info("Data barang tidak ditemukan.")
        else:
            display = view.copy()
            display["Harga"] = display["Harga"].apply(rupiah)
            display["Status"] = display["Stok"].apply(stok_status)
            st.dataframe(display, use_container_width=True, hide_index=True)

    with tab_add:
        with st.form("add_barang"):
            nama = st.text_input("Nama Kayu", placeholder="Contoh: Kayu Jati")
            satuan = st.selectbox("Satuan", ["Batang", "Kubik", "Papan", "Balok", "Lembar"])
            harga = st.number_input("Harga", min_value=0, step=1000)
            stok = st.number_input("Stok Awal", min_value=0, step=1)
            save = st.form_submit_button("Tambah Barang", type="primary", use_container_width=True)
            if save:
                if not nama.strip():
                    st.error("Nama kayu wajib diisi.")
                elif harga <= 0:
                    st.error("Harga harus lebih dari 0.")
                else:
                    conn = get_db()
                    conn.execute("""
                        INSERT INTO kayu (nama_kayu,satuan,harga,stok)
                        VALUES (?,?,?,?)
                    """, (nama.strip(), satuan, harga, stok))
                    conn.commit()
                    conn.close()
                    st.success("Barang berhasil ditambahkan.")
                    st.rerun()

    with tab_edit:
        if df.empty:
            st.info("Belum ada barang.")
        else:
            pilihan = st.selectbox(
                "Pilih barang",
                df["ID"].tolist(),
                format_func=lambda x: f"ID {x} • {df.loc[df['ID']==x,'Nama Kayu'].iloc[0]}"
            )
            row = query_df("SELECT * FROM kayu WHERE id_kayu=?", (pilihan,)).iloc[0]
            with st.form("edit_barang"):
                nama = st.text_input("Nama Kayu", value=row["nama_kayu"])
                satuan_list = ["Batang", "Kubik", "Papan", "Balok", "Lembar"]
                satuan = st.selectbox("Satuan", satuan_list,
                                      index=satuan_list.index(row["satuan"]) if row["satuan"] in satuan_list else 0)
                harga = st.number_input("Harga", min_value=0, value=int(row["harga"]), step=1000)
                stok = st.number_input("Stok", min_value=0, value=int(row["stok"]), step=1)
                save = st.form_submit_button("Simpan Perubahan", type="primary", use_container_width=True)
                if save:
                    if not nama.strip() or harga <= 0:
                        st.error("Nama dan harga harus valid.")
                    else:
                        conn = get_db()
                        conn.execute("""
                            UPDATE kayu SET nama_kayu=?, satuan=?, harga=?, stok=?
                            WHERE id_kayu=?
                        """, (nama.strip(), satuan, harga, stok, pilihan))
                        conn.commit()
                        conn.close()
                        st.success("Data barang diperbarui.")
                        st.rerun()

            if st.button("Hapus Barang", use_container_width=True, key="delete_barang"):
                conn = get_db()
                try:
                    conn.execute("DELETE FROM kayu WHERE id_kayu=?", (pilihan,))
                    conn.commit()
                    st.success("Barang berhasil dihapus.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Barang tidak dapat dihapus karena sudah digunakan dalam transaksi.")
                finally:
                    conn.close()


# =========================================================
# PEMBELIAN / STOK MASUK
# =========================================================
def pembelian_page():
    page_header("Pembelian", "Catat penambahan stok kayu dari pemasok.")

    st.info("Modul ini berfungsi sebagai pencatatan stok masuk. Setiap penyimpanan akan langsung menambah stok barang.")

    pemasok_df = query_df("SELECT id_pemasok, nama_pemasok FROM pemasok ORDER BY nama_pemasok")
    kayu_df = query_df("SELECT id_kayu, nama_kayu, satuan, harga, stok FROM kayu ORDER BY nama_kayu")

    tab_form, tab_supplier = st.tabs(["Stok Masuk", "Pemasok"])

    with tab_form:
        if kayu_df.empty:
            st.warning("Belum ada data barang. Tambahkan barang terlebih dahulu.")
        else:
            with st.form("pembelian_form"):
                kayu_id = st.selectbox(
                    "Barang",
                    kayu_df["id_kayu"].tolist(),
                    format_func=lambda x: kayu_df.loc[kayu_df["id_kayu"]==x, "nama_kayu"].iloc[0]
                )
                supplier = st.selectbox(
                    "Pemasok",
                    ["Tanpa pemasok"] + (
                        [f"{r.id_pemasok} • {r.nama_pemasok}" for r in pemasok_df.itertuples()]
                    )
                )
                jumlah = st.number_input("Jumlah Masuk", min_value=1, value=1, step=1)
                tanggal = st.date_input("Tanggal", value=date.today())
                save = st.form_submit_button("Simpan Stok Masuk", type="primary", use_container_width=True)

                if save:
                    conn = get_db()
                    conn.execute("UPDATE kayu SET stok=stok+? WHERE id_kayu=?", (jumlah, kayu_id))
                    conn.commit()
                    conn.close()
                    st.success(f"Stok berhasil ditambahkan sebanyak {jumlah}.")
                    st.rerun()

    with tab_supplier:
        supplier_df = query_df("""
            SELECT id_pemasok AS 'ID', nama_pemasok AS 'Nama Pemasok',
                   no_telepon AS 'No. Telepon', alamat AS 'Alamat'
            FROM pemasok ORDER BY id_pemasok DESC
        """)
        if not supplier_df.empty:
            st.dataframe(supplier_df, use_container_width=True, hide_index=True)

        with st.form("supplier_form"):
            nama = st.text_input("Nama Pemasok")
            telepon = st.text_input("No. Telepon")
            alamat = st.text_area("Alamat")
            save = st.form_submit_button("Tambah Pemasok", use_container_width=True)
            if save:
                if not nama.strip():
                    st.error("Nama pemasok wajib diisi.")
                else:
                    conn = get_db()
                    conn.execute("""
                        INSERT INTO pemasok(nama_pemasok,no_telepon,alamat)
                        VALUES(?,?,?)
                    """, (nama.strip(), telepon.strip(), alamat.strip()))
                    conn.commit()
                    conn.close()
                    st.success("Pemasok berhasil ditambahkan.")
                    st.rerun()


# =========================================================
# PENJUALAN
# =========================================================
def penjualan_page():
    page_header("Penjualan", "Buat transaksi penjualan kayu dengan perhitungan otomatis.")

    pelanggan_df = query_df("""
        SELECT id_pelanggan, nama_pelanggan FROM pelanggan ORDER BY nama_pelanggan
    """)
    kayu_df = query_df("""
        SELECT id_kayu, nama_kayu, satuan, harga, stok FROM kayu ORDER BY nama_kayu
    """)

    if pelanggan_df.empty:
        st.warning("Tambahkan pelanggan terlebih dahulu melalui menu Pelanggan & Pemasok.")
        return
    if kayu_df.empty:
        st.warning("Belum ada data barang.")
        return

    c1, c2 = st.columns([2, 1])
    with c1:
        pelanggan_id = st.selectbox(
            "Pelanggan",
            pelanggan_df["id_pelanggan"].tolist(),
            format_func=lambda x: pelanggan_df.loc[pelanggan_df["id_pelanggan"]==x, "nama_pelanggan"].iloc[0]
        )
    with c2:
        st.caption("Lokasi")
        st.write("Gudang Utama Jati Mulya")

    st.markdown('<div class="section-title">Tambah Barang</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 2, 1])

    with c1:
        kayu_id = st.selectbox(
            "Barang",
            kayu_df["id_kayu"].tolist(),
            format_func=lambda x: f"{kayu_df.loc[kayu_df['id_kayu']==x,'nama_kayu'].iloc[0]} • Stok {kayu_df.loc[kayu_df['id_kayu']==x,'stok'].iloc[0]}"
        )
    row = kayu_df[kayu_df["id_kayu"] == kayu_id].iloc[0]
    with c2:
        st.text_input("Harga", rupiah(row["harga"]), disabled=True)
    with c3:
        jumlah = st.number_input("Jumlah", min_value=1, max_value=max(1, int(row["stok"])), value=1)

    subtotal = float(row["harga"]) * int(jumlah)
    st.info(f"Subtotal: **{rupiah(subtotal)}**")

    if st.button("Masukkan ke Keranjang", use_container_width=True):
        existing = next((x for x in st.session_state.cart_items if x["id_kayu"] == int(kayu_id)), None)
        if existing:
            new_qty = existing["jumlah"] + int(jumlah)
            if new_qty > int(row["stok"]):
                st.error("Jumlah keranjang melebihi stok.")
            else:
                existing["jumlah"] = new_qty
                existing["subtotal"] = new_qty * float(row["harga"])
                st.rerun()
        else:
            if int(row["stok"]) <= 0:
                st.error("Stok barang habis.")
            else:
                st.session_state.cart_items.append({
                    "id_kayu": int(kayu_id),
                    "nama_kayu": row["nama_kayu"],
                    "satuan": row["satuan"],
                    "harga": float(row["harga"]),
                    "jumlah": int(jumlah),
                    "subtotal": subtotal,
                })
                st.rerun()

    st.markdown('<div class="section-title">Keranjang Penjualan</div>', unsafe_allow_html=True)

    if not st.session_state.cart_items:
        st.info("Keranjang masih kosong.")
        return

    cart = pd.DataFrame([{
        "No": i + 1,
        "Barang": x["nama_kayu"],
        "Satuan": x["satuan"],
        "Harga": rupiah(x["harga"]),
        "Jumlah": x["jumlah"],
        "Subtotal": rupiah(x["subtotal"])
    } for i, x in enumerate(st.session_state.cart_items)])
    st.dataframe(cart, use_container_width=True, hide_index=True)

    total = sum(x["subtotal"] for x in st.session_state.cart_items)
    st.markdown(f"### Total {rupiah(total)}")

    remove_idx = st.selectbox(
        "Hapus barang",
        range(len(st.session_state.cart_items)),
        format_func=lambda i: st.session_state.cart_items[i]["nama_kayu"]
    )
    if st.button("Hapus dari Keranjang", use_container_width=True):
        st.session_state.cart_items.pop(remove_idx)
        st.rerun()

    if st.button("Simpan Transaksi", type="primary", use_container_width=True):
        conn = get_db()
        try:
            for item in st.session_state.cart_items:
                latest = conn.execute("SELECT stok FROM kayu WHERE id_kayu=?", (item["id_kayu"],)).fetchone()
                if latest is None or int(latest["stok"]) < int(item["jumlah"]):
                    raise ValueError(f"Stok {item['nama_kayu']} tidak mencukupi.")

            cur = conn.execute("""
                INSERT INTO penjualan(tanggal,id_pelanggan,id_user,total)
                VALUES(?,?,?,?)
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                pelanggan_id,
                st.session_state.current_user_id,
                total
            ))
            trx_id = cur.lastrowid

            for item in st.session_state.cart_items:
                conn.execute("""
                    INSERT INTO detail_penjualan(id_penjualan,id_kayu,jumlah,harga,subtotal)
                    VALUES(?,?,?,?,?)
                """, (trx_id, item["id_kayu"], item["jumlah"], item["harga"], item["subtotal"]))
                conn.execute("UPDATE kayu SET stok=stok-? WHERE id_kayu=?", (item["jumlah"], item["id_kayu"]))

            conn.commit()
            st.session_state.cart_items = []
            st.success(f"Transaksi #{trx_id} berhasil disimpan.")
            st.session_state.page = "Laporan"
            st.rerun()
        except Exception as e:
            conn.rollback()
            st.error(f"Transaksi gagal: {e}")
        finally:
            conn.close()


# =========================================================
# PELANGGAN & PEMASOK
# =========================================================
def customers_page():
    page_header("Pelanggan & Pemasok", "Kelola data pelanggan dan mitra pemasok.")

    tab_pelanggan, tab_pemasok = st.tabs(["Pelanggan", "Pemasok"])

    with tab_pelanggan:
        df = query_df("""
            SELECT id_pelanggan AS 'ID', nama_pelanggan AS 'Nama Pelanggan',
                   no_telepon AS 'No. Telepon', alamat AS 'Alamat'
            FROM pelanggan ORDER BY id_pelanggan DESC
        """)
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Pelanggan</div>'
                    f'<div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
        st.write("")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

        with st.form("customer_add"):
            nama = st.text_input("Nama Pelanggan")
            telepon = st.text_input("No. Telepon")
            alamat = st.text_area("Alamat")
            save = st.form_submit_button("Tambah Pelanggan", type="primary", use_container_width=True)
            if save:
                if not nama.strip():
                    st.error("Nama pelanggan wajib diisi.")
                else:
                    conn = get_db()
                    conn.execute("""
                        INSERT INTO pelanggan(nama_pelanggan,no_telepon,alamat)
                        VALUES(?,?,?)
                    """, (nama.strip(), telepon.strip(), alamat.strip()))
                    conn.commit()
                    conn.close()
                    st.success("Pelanggan berhasil ditambahkan.")
                    st.rerun()

    with tab_pemasok:
        df = query_df("""
            SELECT id_pemasok AS 'ID', nama_pemasok AS 'Nama Pemasok',
                   no_telepon AS 'No. Telepon', alamat AS 'Alamat'
            FROM pemasok ORDER BY id_pemasok DESC
        """)
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Pemasok</div>'
                    f'<div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
        st.write("")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)


# =========================================================
# LAPORAN
# =========================================================
def reports_page():
    page_header("Laporan", "Pantau transaksi penjualan dan kondisi stok.")

    tab_sales, tab_stock = st.tabs(["Laporan Penjualan", "Laporan Stok"])

    with tab_sales:
        df = query_df("""
            SELECT p.id_penjualan AS 'ID Transaksi', p.tanggal AS 'Tanggal',
                   COALESCE(pl.nama_pelanggan,'-') AS 'Pelanggan',
                   p.total AS 'Total'
            FROM penjualan p
            LEFT JOIN pelanggan pl ON p.id_pelanggan = pl.id_pelanggan
            ORDER BY p.id_penjualan DESC
        """)

        if df.empty:
            st.info("Belum ada transaksi.")
        else:
            df["Tanggal_dt"] = pd.to_datetime(df["Tanggal"])
            min_date = df["Tanggal_dt"].min().date()
            max_date = df["Tanggal_dt"].max().date()

            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                awal = st.date_input("Tanggal Awal", value=min_date, key="report_start")
            with c2:
                akhir = st.date_input("Tanggal Akhir", value=max_date, key="report_end")
            with c3:
                st.write("")
                st.write("")
                st.caption("Gudang Utama Jati Mulya")

            if awal > akhir:
                st.error("Tanggal awal tidak boleh lebih besar dari tanggal akhir.")
            else:
                result = df[(df["Tanggal_dt"].dt.date >= awal) & (df["Tanggal_dt"].dt.date <= akhir)].copy()
                total = result["Total"].sum()

                a, b = st.columns(2)
                a.metric("Jumlah Transaksi", len(result))
                b.metric("Total Penjualan", rupiah(total))

                display = result[["ID Transaksi", "Tanggal", "Pelanggan", "Total"]].copy()
                display["Total"] = display["Total"].apply(rupiah)
                st.dataframe(display, use_container_width=True, hide_index=True)

                csv = result[["ID Transaksi", "Tanggal", "Pelanggan", "Total"]].to_csv(index=False).encode("utf-8")
                st.download_button("Download Laporan Penjualan", csv,
                                   "laporan_penjualan.csv", "text/csv", use_container_width=True)

                st.markdown('<div class="section-title">Detail Transaksi</div>', unsafe_allow_html=True)
                trx_ids = result["ID Transaksi"].tolist()
                trx_id = st.selectbox("Pilih transaksi", trx_ids, key="report_trx")
                detail = query_df("""
                    SELECT d.id_detail AS 'No', k.nama_kayu AS 'Barang',
                           d.jumlah AS 'Jumlah', d.harga AS 'Harga',
                           d.subtotal AS 'Subtotal'
                    FROM detail_penjualan d
                    JOIN kayu k ON d.id_kayu = k.id_kayu
                    WHERE d.id_penjualan = ?
                    ORDER BY d.id_detail
                """, (trx_id,))
                if not detail.empty:
                    detail["Harga"] = detail["Harga"].apply(rupiah)
                    detail["Subtotal"] = detail["Subtotal"].apply(rupiah)
                    st.dataframe(detail, use_container_width=True, hide_index=True)

    with tab_stock:
        df = query_df("""
            SELECT id_kayu AS 'ID', nama_kayu AS 'Nama Kayu',
                   satuan AS 'Satuan', stok AS 'Stok', harga AS 'Harga'
            FROM kayu ORDER BY stok ASC
        """)
        if df.empty:
            st.info("Belum ada data stok.")
        else:
            result = df.copy()
            result["Status"] = result["Stok"].apply(stok_status)
            display = result.copy()
            display["Harga"] = display["Harga"].apply(rupiah)
            st.dataframe(display, use_container_width=True, hide_index=True)
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("Download Laporan Stok", csv,
                               "laporan_stok.csv", "text/csv", use_container_width=True)


# =========================================================
# RUN
# =========================================================
init_db()
inject_css()

if not st.session_state.is_logged_in:
    login_page()
else:
    sidebar()

    if st.session_state.page == "Dashboard":
        dashboard()
    elif st.session_state.page == "Barang":
        barang_page()
    elif st.session_state.page == "Pembelian":
        pembelian_page()
    elif st.session_state.page == "Penjualan":
        penjualan_page()
    elif st.session_state.page == "Pelanggan & Pemasok":
        customers_page()
    elif st.session_state.page == "Laporan":
        reports_page()
