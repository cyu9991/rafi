import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# =========================================================
# KONFIGURASI
# =========================================================

st.set_page_config(
    page_title="Sistem Informasi Penjualan Kayu",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded"
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
        CREATE TABLE IF NOT EXISTS penjualan (
            id_penjualan INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            id_pelanggan INTEGER,
            id_user INTEGER,
            total REAL NOT NULL,
            FOREIGN KEY (id_pelanggan)
                REFERENCES pelanggan(id_pelanggan)
                ON DELETE SET NULL,
            FOREIGN KEY (id_user)
                REFERENCES users(id_user)
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
            FOREIGN KEY (id_penjualan)
                REFERENCES penjualan(id_penjualan)
                ON DELETE CASCADE,
            FOREIGN KEY (id_kayu)
                REFERENCES kayu(id_kayu)
                ON DELETE RESTRICT
        )
    """)

    # Admin default
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO users (username, password, nama)
            VALUES (?, ?, ?)
        """, ("admin", "admin123", "Administrator"))

    # Data kayu awal
    cur.execute("SELECT COUNT(*) FROM kayu")
    if cur.fetchone()[0] == 0:
        data_kayu = [
            ("Jati", "Batang", 150000, 50),
            ("Meranti", "Batang", 100000, 40),
            ("Sengon", "Batang", 75000, 60),
            ("Mahoni", "Batang", 120000, 35),
            ("Ulin", "Batang", 200000, 25)
        ]

        cur.executemany("""
            INSERT INTO kayu
            (nama_kayu, satuan, harga, stok)
            VALUES (?, ?, ?, ?)
        """, data_kayu)

    conn.commit()
    conn.close()


# =========================================================
# HELPER
# =========================================================

def rupiah(value):
    return "Rp {:,.0f}".format(float(value)).replace(",", ".")


def query_df(sql, params=()):
    conn = get_db()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def execute(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id


# =========================================================
# SESSION STATE
# =========================================================

if "login" not in st.session_state:
    st.session_state.login = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "cart" not in st.session_state:
    st.session_state.cart = []


# =========================================================
# CSS - GAYA UI HTML KAYU
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: #f7f5f2;
}

[data-testid="stSidebar"] {
    background: #201812;
    border-right: 1px solid #3b2b20;
}

[data-testid="stSidebar"] * {
    color: #f5eee7 !important;
}

.sidebar-brand {
    padding: 10px 5px 25px 5px;
}

.sidebar-brand-title {
    font-size: 20px;
    font-weight: 800;
    color: #ffffff;
}

.sidebar-brand-sub {
    font-size: 11px;
    color: #b9aaa0;
    margin-top: 3px;
}

.page-title {
    font-size: 30px;
    font-weight: 800;
    color: #2b1d15;
    margin-bottom: 3px;
}

.page-subtitle {
    color: #786b63;
    font-size: 14px;
    margin-bottom: 25px;
}

.card {
    background: white;
    border: 1px solid #e9e2dc;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(50, 35, 20, 0.04);
}

.metric-card {
    background: white;
    border: 1px solid #e9e2dc;
    border-radius: 16px;
    padding: 20px;
    min-height: 135px;
}

.metric-label {
    color: #7b6d64;
    font-size: 13px;
    font-weight: 600;
}

.metric-value {
    color: #2b1d15;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

.metric-icon {
    font-size: 25px;
    margin-bottom: 8px;
}

.section-title {
    color: #2b1d15;
    font-size: 20px;
    font-weight: 800;
    margin-top: 25px;
    margin-bottom: 15px;
}

.badge {
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}

.badge-safe {
    background: #e8f5e9;
    color: #2e7d32;
}

.badge-low {
    background: #fff3e0;
    color: #ef6c00;
}

.badge-danger {
    background: #ffebee;
    color: #c62828;
}

.login-box {
    max-width: 450px;
    margin: 70px auto;
    background: white;
    padding: 40px;
    border-radius: 22px;
    border: 1px solid #e6ddd5;
    box-shadow: 0 10px 35px rgba(50,35,20,.08);
}

.login-logo {
    text-align: center;
    font-size: 55px;
}

.login-title {
    text-align: center;
    font-size: 27px;
    font-weight: 800;
    color: #2b1d15;
}

.login-subtitle {
    text-align: center;
    color: #80736b;
    font-size: 13px;
    margin-bottom: 25px;
}

.info-box {
    background: #f4ede7;
    border-left: 4px solid #8b5e3c;
    padding: 14px;
    border-radius: 8px;
    color: #4d3a2e;
    font-size: 13px;
}

.stButton > button {
    border-radius: 9px;
    font-weight: 700;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e9e2dc;
    padding: 15px;
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOGIN
# =========================================================

def login_page():

    st.markdown("""
    <div class="login-box">
        <div class="login-logo">🪵</div>
        <div class="login-title">
            Sistem Informasi Penjualan Kayu
        </div>
        <div class="login-subtitle">
            Penjualan dan Pengelolaan Stok Kayu Berbasis Web
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        with st.form("login_form"):

            username = st.text_input(
                "Username",
                placeholder="Masukkan username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password"
            )

            submit = st.form_submit_button(
                "Masuk",
                use_container_width=True
            )

            if submit:

                conn = get_db()

                user = conn.execute("""
                    SELECT *
                    FROM users
                    WHERE username = ?
                    AND password = ?
                """, (username, password)).fetchone()

                conn.close()

                if user:

                    st.session_state.login = True
                    st.session_state.user_id = user["id_user"]
                    st.session_state.user_name = user["nama"]
                    st.session_state.page = "Dashboard"

                    st.rerun()

                else:
                    st.error("Username atau password salah.")

        st.markdown("""
        <div class="info-box">
            <b>Login demo</b><br>
            Username: admin<br>
            Password: admin123
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

def sidebar():

    with st.sidebar:

        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">🪵 KayuKu</div>
            <div class="sidebar-brand-sub">
                Sistem Penjualan & Stok Kayu
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        menu = [
            "Dashboard",
            "Data Kayu",
            "Stok Kayu",
            "Pelanggan",
            "Penjualan",
            "Riwayat Transaksi",
            "Laporan"
        ]

        for item in menu:

            if st.button(
                item,
                key="menu_" + item,
                use_container_width=True
            ):
                st.session_state.page = item
                st.rerun()

        st.markdown("---")

        st.caption(
            "Login sebagai\n" +
            str(st.session_state.user_name)
        )

        if st.button(
            "Keluar",
            use_container_width=True
        ):
            st.session_state.login = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.cart = []
            st.rerun()


# =========================================================
# HEADER
# =========================================================

def header(title, subtitle):

    st.markdown(
        f"""
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DASHBOARD
# =========================================================

def halaman_dashboard():

    header(
        "Dashboard",
        "Ringkasan aktivitas penjualan dan persediaan kayu."
    )

    df_kayu = query_df("""
        SELECT *
        FROM kayu
    """)

    df_pelanggan = query_df("""
        SELECT *
        FROM pelanggan
    """)

    df_transaksi = query_df("""
        SELECT *
        FROM penjualan
    """)

    jumlah_jenis = len(df_kayu)
    total_stok = int(df_kayu["stok"].sum()) if not df_kayu.empty else 0
    jumlah_pelanggan = len(df_pelanggan)
    jumlah_transaksi = len(df_transaksi)

    total_penjualan = (
        float(df_transaksi["total"].sum())
        if not df_transaksi.empty
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🪵</div>
            <div class="metric-label">Jenis Kayu</div>
            <div class="metric-value">{jumlah_jenis}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📦</div>
            <div class="metric-label">Total Stok</div>
            <div class="metric-value">{total_stok}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-label">Pelanggan</div>
            <div class="metric-value">{jumlah_pelanggan}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-label">Total Penjualan</div>
            <div class="metric-value" style="font-size:22px;">
                {rupiah(total_penjualan)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Status Stok Kayu</div>',
        unsafe_allow_html=True
    )

    if not df_kayu.empty:

        tabel = df_kayu[
            ["id_kayu", "nama_kayu", "satuan", "harga", "stok"]
        ].copy()

        tabel.columns = [
            "ID",
            "Nama Kayu",
            "Satuan",
            "Harga",
            "Stok"
        ]

        tabel["Harga"] = tabel["Harga"].apply(rupiah)

        st.dataframe(
            tabel,
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        '<div class="section-title">Transaksi Terbaru</div>',
        unsafe_allow_html=True
    )

    terbaru = query_df("""
        SELECT
            p.id_penjualan,
            p.tanggal,
            COALESCE(pl.nama_pelanggan, 'Umum') AS pelanggan,
            p.total
        FROM penjualan p
        LEFT JOIN pelanggan pl
            ON p.id_pelanggan = pl.id_pelanggan
        ORDER BY p.id_penjualan DESC
        LIMIT 5
    """)

    if terbaru.empty:
        st.info("Belum ada transaksi.")
    else:

        terbaru["total"] = terbaru["total"].apply(rupiah)

        terbaru.columns = [
            "ID",
            "Tanggal",
            "Pelanggan",
            "Total"
        ]

        st.dataframe(
            terbaru,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# DATA KAYU
# =========================================================

def halaman_data_kayu():

    header(
        "Data Kayu",
        "Kelola data barang, harga dan persediaan kayu."
    )

    tab1, tab2 = st.tabs(
        ["📋 Data Kayu", "➕ Tambah Kayu"]
    )

    with tab1:

        df = query_df("""
            SELECT *
            FROM kayu
            ORDER BY id_kayu DESC
        """)

        if df.empty:
            st.info("Belum ada data kayu.")
        else:

            search = st.text_input(
                "🔎 Cari kayu",
                placeholder="Masukkan nama kayu..."
            )

            if search:
                df = df[
                    df["nama_kayu"].str.contains(
                        search,
                        case=False,
                        na=False
                    )
                ]

            tampil = df.copy()

            tampil["harga"] = tampil["harga"].apply(rupiah)

            tampil.columns = [
                "ID",
                "Nama Kayu",
                "Satuan",
                "Harga",
                "Stok"
            ]

            st.dataframe(
                tampil,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Edit / Hapus Data")

            pilihan = st.selectbox(
                "Pilih kayu",
                df["id_kayu"].tolist(),
                format_func=lambda x:
                    df.loc[
                        df["id_kayu"] == x,
                        "nama_kayu"
                    ].iloc[0]
            )

            data = df[df["id_kayu"] == pilihan].iloc[0]

            col1, col2 = st.columns(2)

            with col1:

                nama = st.text_input(
                    "Nama Kayu",
                    value=data["nama_kayu"]
                )

                satuan = st.selectbox(
                    "Satuan",
                    [
                        "Batang",
                        "Kubik",
                        "Papan",
                        "Balok",
                        "Lembar"
                    ],
                    index=[
                        "Batang",
                        "Kubik",
                        "Papan",
                        "Balok",
                        "Lembar"
                    ].index(data["satuan"])
                )

            with col2:

                harga = st.number_input(
                    "Harga",
                    min_value=0.0,
                    value=float(data["harga"]),
                    step=1000.0
                )

                stok = st.number_input(
                    "Stok",
                    min_value=0,
                    value=int(data["stok"]),
                    step=1
                )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "💾 Simpan Perubahan",
                    use_container_width=True
                ):

                    execute("""
                        UPDATE kayu
                        SET nama_kayu = ?,
                            satuan = ?,
                            harga = ?,
                            stok = ?
                        WHERE id_kayu = ?
                    """, (
                        nama,
                        satuan,
                        harga,
                        stok,
                        pilihan
                    ))

                    st.success("Data berhasil diperbarui.")
                    st.rerun()

            with c2:

                if st.button(
                    "🗑️ Hapus Kayu",
                    use_container_width=True
                ):

                    try:

                        execute("""
                            DELETE FROM kayu
                            WHERE id_kayu = ?
                        """, (pilihan,))

                        st.success("Data berhasil dihapus.")
                        st.rerun()

                    except sqlite3.IntegrityError:

                        st.error(
                            "Kayu tidak dapat dihapus karena "
                            "sudah digunakan dalam transaksi."
                        )

    with tab2:

        with st.form("form_tambah_kayu"):

            nama = st.text_input("Nama Kayu")

            satuan = st.selectbox(
                "Satuan",
                [
                    "Batang",
                    "Kubik",
                    "Papan",
                    "Balok",
                    "Lembar"
                ]
            )

            harga = st.number_input(
                "Harga",
                min_value=0.0,
                step=1000.0
            )

            stok = st.number_input(
                "Stok Awal",
                min_value=0,
                step=1
            )

            submit = st.form_submit_button(
                "Tambah Kayu",
                use_container_width=True
            )

            if submit:

                if not nama.strip():
                    st.error("Nama kayu wajib diisi.")
                else:

                    execute("""
                        INSERT INTO kayu
                        (nama_kayu, satuan, harga, stok)
                        VALUES (?, ?, ?, ?)
                    """, (
                        nama,
                        satuan,
                        harga,
                        stok
                    ))

                    st.success(
                        f"Kayu {nama} berhasil ditambahkan."
                    )

                    st.rerun()


# =========================================================
# STOK
# =========================================================

def halaman_stok():

    header(
        "Stok Kayu",
        "Pantau kondisi persediaan kayu."
    )

    df = query_df("""
        SELECT *
        FROM kayu
        ORDER BY stok ASC
    """)

    if df.empty:
        st.info("Belum ada data stok.")
        return

    sangat_rendah = len(df[df["stok"] <= 5])
    rendah = len(
        df[
            (df["stok"] >= 6) &
            (df["stok"] <= 10)
        ]
    )
    aman = len(df[df["stok"] > 10])

    c1, c2, c3 = st.columns(3)

    c1.metric("🔴 Sangat Rendah", sangat_rendah)
    c2.metric("🟠 Rendah", rendah)
    c3.metric("🟢 Aman", aman)

    st.markdown(
        '<div class="section-title">Daftar Stok</div>',
        unsafe_allow_html=True
    )

    for _, row in df.iterrows():

        if row["stok"] <= 5:
            status = "Sangat Rendah"
        elif row["stok"] <= 10:
            status = "Rendah"
        else:
            status = "Aman"

        c1, c2, c3, c4 = st.columns([3, 1, 1, 2])

        c1.write(f"**{row['nama_kayu']}**")
        c2.write(f"{row['stok']} {row['satuan']}")
        c3.write(rupiah(row["harga"]))

        if status == "Aman":
            c4.success("🟢 Aman")
        elif status == "Rendah":
            c4.warning("🟠 Rendah")
        else:
            c4.error("🔴 Sangat Rendah")

        st.divider()


# =========================================================
# PELANGGAN
# =========================================================

def halaman_pelanggan():

    header(
        "Pelanggan",
        "Kelola data pelanggan."
    )

    tab1, tab2 = st.tabs(
        ["📋 Data Pelanggan", "➕ Tambah Pelanggan"]
    )

    with tab1:

        df = query_df("""
            SELECT *
            FROM pelanggan
            ORDER BY id_pelanggan DESC
        """)

        if df.empty:
            st.info("Belum ada data pelanggan.")
        else:

            search = st.text_input(
                "🔎 Cari pelanggan"
            )

            if search:
                df = df[
                    df["nama_pelanggan"].str.contains(
                        search,
                        case=False,
                        na=False
                    )
                ]

            tampil = df.copy()

            tampil.columns = [
                "ID",
                "Nama Pelanggan",
                "No. Telepon",
                "Alamat"
            ]

            st.dataframe(
                tampil,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Edit Data Pelanggan")

            pilihan = st.selectbox(
                "Pilih pelanggan",
                df["id_pelanggan"].tolist(),
                format_func=lambda x:
                    df.loc[
                        df["id_pelanggan"] == x,
                        "nama_pelanggan"
                    ].iloc[0]
            )

            data = df[
                df["id_pelanggan"] == pilihan
            ].iloc[0]

            nama = st.text_input(
                "Nama",
                value=data["nama_pelanggan"]
            )

            telepon = st.text_input(
                "No. Telepon",
                value=data["no_telepon"] or ""
            )

            alamat = st.text_area(
                "Alamat",
                value=data["alamat"] or ""
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "💾 Simpan",
                    use_container_width=True
                ):

                    execute("""
                        UPDATE pelanggan
                        SET nama_pelanggan = ?,
                            no_telepon = ?,
                            alamat = ?
                        WHERE id_pelanggan = ?
                    """, (
                        nama,
                        telepon,
                        alamat,
                        pilihan
                    ))

                    st.success("Data diperbarui.")
                    st.rerun()

            with c2:

                if st.button(
                    "🗑️ Hapus",
                    use_container_width=True
                ):

                    execute("""
                        DELETE FROM pelanggan
                        WHERE id_pelanggan = ?
                    """, (pilihan,))

                    st.success("Pelanggan dihapus.")
                    st.rerun()

    with tab2:

        with st.form("form_pelanggan"):

            nama = st.text_input(
                "Nama Pelanggan"
            )

            telepon = st.text_input(
                "No. Telepon"
            )

            alamat = st.text_area(
                "Alamat"
            )

            submit = st.form_submit_button(
                "Tambah Pelanggan",
                use_container_width=True
            )

            if submit:

                if not nama.strip():
                    st.error(
                        "Nama pelanggan wajib diisi."
                    )
                else:

                    execute("""
                        INSERT INTO pelanggan
                        (nama_pelanggan, no_telepon, alamat)
                        VALUES (?, ?, ?)
                    """, (
                        nama,
                        telepon,
                        alamat
                    ))

                    st.success(
                        "Pelanggan berhasil ditambahkan."
                    )

                    st.rerun()


# =========================================================
# PENJUALAN
# =========================================================

def halaman_penjualan():

    header(
        "Penjualan",
        "Buat transaksi penjualan kayu."
    )

    pelanggan = query_df("""
        SELECT *
        FROM pelanggan
        ORDER BY nama_pelanggan
    """)

    kayu = query_df("""
        SELECT *
        FROM kayu
        WHERE stok > 0
        ORDER BY nama_kayu
    """)

    if pelanggan.empty:
        st.warning(
            "Belum ada pelanggan. "
            "Tambahkan pelanggan terlebih dahulu."
        )

    if kayu.empty:
        st.warning(
            "Tidak ada kayu dengan stok tersedia."
        )
        return

    st.markdown(
        '<div class="section-title">Informasi Transaksi</div>',
        unsafe_allow_html=True
    )

    if pelanggan.empty:

        pelanggan_id = None

    else:

        pelanggan_id = st.selectbox(
            "Pelanggan",
            pelanggan["id_pelanggan"].tolist(),
            format_func=lambda x:
                pelanggan.loc[
                    pelanggan["id_pelanggan"] == x,
                    "nama_pelanggan"
                ].iloc[0]
        )

    st.markdown(
        '<div class="section-title">Tambah Barang</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:

        kayu_id = st.selectbox(
            "Pilih Kayu",
            kayu["id_kayu"].tolist(),
            format_func=lambda x:
                kayu.loc[
                    kayu["id_kayu"] == x,
                    "nama_kayu"
                ].iloc[0]
        )

    data = kayu[kayu["id_kayu"] == kayu_id].iloc[0]

    with col2:

        st.write("Harga")
        st.write(f"**{rupiah(data['harga'])}**")

    with col3:

        st.write("Stok")
        st.write(f"**{data['stok']} {data['satuan']}**")

    jumlah = st.number_input(
        "Jumlah",
        min_value=1,
        max_value=int(data["stok"]),
        value=1,
        step=1
    )

    if st.button(
        "➕ Tambahkan ke Keranjang",
        use_container_width=True
    ):

        found = False

        for item in st.session_state.cart:

            if item["id_kayu"] == kayu_id:

                if item["jumlah"] + jumlah <= int(data["stok"]):
                    item["jumlah"] += jumlah
                else:
                    st.error(
                        "Jumlah melebihi stok yang tersedia."
                    )

                found = True
                break

        if not found:

            st.session_state.cart.append({
                "id_kayu": int(kayu_id),
                "nama": data["nama_kayu"],
                "satuan": data["satuan"],
                "harga": float(data["harga"]),
                "jumlah": int(jumlah)
            })

        st.rerun()

    st.markdown(
        '<div class="section-title">Keranjang Penjualan</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.cart:

        st.info("Keranjang masih kosong.")
        return

    total = 0

    for i, item in enumerate(
        st.session_state.cart
    ):

        subtotal = (
            item["harga"] *
            item["jumlah"]
        )

        total += subtotal

        c1, c2, c3, c4, c5 = st.columns(
            [3, 1, 1, 2, 1]
        )

        c1.write(
            f"**{item['nama']}**"
        )

        c2.write(
            f"{item['jumlah']} {item['satuan']}"
        )

        c3.write(
            rupiah(item["harga"])
        )

        c4.write(
            f"**{rupiah(subtotal)}**"
        )

        if c5.button(
            "✕",
            key=f"hapus_cart_{i}"
        ):

            st.session_state.cart.pop(i)
            st.rerun()

    st.divider()

    st.markdown(
        f"""
        <div style="
            background:white;
            border:1px solid #e9e2dc;
            border-radius:16px;
            padding:22px;
            text-align:right;
        ">
            <div style="
                color:#786b63;
                font-size:13px;
            ">
                Total Pembayaran
            </div>

            <div style="
                color:#2b1d15;
                font-size:30px;
                font-weight:800;
            ">
                {rupiah(total)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "💰 Simpan Transaksi",
        use_container_width=True
    ):

        conn = get_db()

        try:

            # Cek stok terbaru
            for item in st.session_state.cart:

                row = conn.execute("""
                    SELECT stok
                    FROM kayu
                    WHERE id_kayu = ?
                """, (item["id_kayu"],)).fetchone()

                if not row:
                    raise Exception(
                        f"Kayu {item['nama']} tidak ditemukan."
                    )

                if row["stok"] < item["jumlah"]:
                    raise Exception(
                        f"Stok {item['nama']} tidak mencukupi."
                    )

            tanggal = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            cur = conn.cursor()

            cur.execute("""
                INSERT INTO penjualan
                (tanggal, id_pelanggan, id_user, total)
                VALUES (?, ?, ?, ?)
            """, (
                tanggal,
                pelanggan_id,
                st.session_state.user_id,
                total
            ))

            id_penjualan = cur.lastrowid

            for item in st.session_state.cart:

                subtotal = (
                    item["harga"] *
                    item["jumlah"]
                )

                cur.execute("""
                    INSERT INTO detail_penjualan
                    (id_penjualan, id_kayu, jumlah, harga, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    id_penjualan,
                    item["id_kayu"],
                    item["jumlah"],
                    item["harga"],
                    subtotal
                ))

                cur.execute("""
                    UPDATE kayu
                    SET stok = stok - ?
                    WHERE id_kayu = ?
                """, (
                    item["jumlah"],
                    item["id_kayu"]
                ))

            conn.commit()

            st.session_state.cart = []

            st.success(
                f"Transaksi #{id_penjualan} berhasil disimpan."
            )

            st.session_state.page = "Riwayat Transaksi"

            st.rerun()

        except Exception as e:

            conn.rollback()
            st.error(str(e))

        finally:

            conn.close()


# =========================================================
# RIWAYAT TRANSAKSI
# =========================================================

def halaman_riwayat():

    header(
        "Riwayat Transaksi",
        "Daftar transaksi penjualan yang telah dilakukan."
    )

    df = query_df("""
        SELECT
            p.id_penjualan,
            p.tanggal,
            COALESCE(pl.nama_pelanggan, 'Umum')
                AS pelanggan,
            COALESCE(u.nama, 'Admin')
                AS admin,
            p.total
        FROM penjualan p
        LEFT JOIN pelanggan pl
            ON p.id_pelanggan = pl.id_pelanggan
        LEFT JOIN users u
            ON p.id_user = u.id_user
        ORDER BY p.id_penjualan DESC
    """)

    if df.empty:

        st.info("Belum ada transaksi.")
        return

    tampil = df.copy()
    tampil["total"] = tampil["total"].apply(rupiah)

    tampil.columns = [
        "ID",
        "Tanggal",
        "Pelanggan",
        "Admin",
        "Total"
    ]

    st.dataframe(
        tampil,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### Detail Transaksi")

    id_transaksi = st.selectbox(
        "Pilih transaksi",
        df["id_penjualan"].tolist()
    )

    detail = query_df("""
        SELECT
            k.nama_kayu,
            dp.jumlah,
            k.satuan,
            dp.harga,
            dp.subtotal
        FROM detail_penjualan dp
        JOIN kayu k
            ON dp.id_kayu = k.id_kayu
        WHERE dp.id_penjualan = ?
    """, (id_transaksi,))

    if not detail.empty:

        detail["harga"] = detail["harga"].apply(rupiah)
        detail["subtotal"] = detail["subtotal"].apply(rupiah)

        detail.columns = [
            "Kayu",
            "Jumlah",
            "Satuan",
            "Harga",
            "Subtotal"
        ]

        st.dataframe(
            detail,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# LAPORAN
# =========================================================

def halaman_laporan():

    header(
        "Laporan",
        "Laporan penjualan dan stok kayu."
    )

    tab1, tab2 = st.tabs(
        ["📊 Laporan Penjualan", "📦 Laporan Stok"]
    )

    with tab1:

        col1, col2 = st.columns(2)

        with col1:
            tanggal_awal = st.date_input(
                "Tanggal Awal"
            )

        with col2:
            tanggal_akhir = st.date_input(
                "Tanggal Akhir"
            )

        df = query_df("""
            SELECT
                p.id_penjualan,
                p.tanggal,
                COALESCE(
                    pl.nama_pelanggan,
                    'Umum'
                ) AS pelanggan,
                p.total
            FROM penjualan p
            LEFT JOIN pelanggan pl
                ON p.id_pelanggan =
                   pl.id_pelanggan
            ORDER BY p.id_penjualan DESC
        """)

        if not df.empty:

            df["tanggal_only"] = pd.to_datetime(
                df["tanggal"]
            ).dt.date

            df = df[
                (df["tanggal_only"] >= tanggal_awal) &
                (df["tanggal_only"] <= tanggal_akhir)
            ]

        total_transaksi = len(df)

        total = (
            df["total"].sum()
            if not df.empty
            else 0
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "Jumlah Transaksi",
            total_transaksi
        )

        c2.metric(
            "Total Penjualan",
            rupiah(total)
        )

        if not df.empty:

            tampil = df[
                [
                    "id_penjualan",
                    "tanggal",
                    "pelanggan",
                    "total"
                ]
            ].copy()

            tampil["total"] = tampil[
                "total"
            ].apply(rupiah)

            tampil.columns = [
                "ID",
                "Tanggal",
                "Pelanggan",
                "Total"
            ]

            st.dataframe(
                tampil,
                use_container_width=True,
                hide_index=True
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download CSV",
                csv,
                "laporan_penjualan.csv",
                "text/csv",
                use_container_width=True
            )

        else:

            st.info(
                "Tidak ada transaksi pada periode tersebut."
            )

    with tab2:

        df = query_df("""
            SELECT
                id_kayu,
                nama_kayu,
                satuan,
                harga,
                stok
            FROM kayu
            ORDER BY nama_kayu
        """)

        if not df.empty:

            tampil = df.copy()

            tampil["harga"] = tampil[
                "harga"
            ].apply(rupiah)

            tampil["status"] = tampil["stok"].apply(
                lambda x:
                    "Sangat Rendah"
                    if x <= 5
                    else (
                        "Rendah"
                        if x <= 10
                        else "Aman"
                    )
            )

            tampil.columns = [
                "ID",
                "Nama Kayu",
                "Satuan",
                "Harga",
                "Stok",
                "Status"
            ]

            st.dataframe(
                tampil,
                use_container_width=True,
                hide_index=True
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Stok CSV",
                csv,
                "laporan_stok.csv",
                "text/csv",
                use_container_width=True
            )


# =========================================================
# MAIN
# =========================================================

init_db()

if not st.session_state.login:

    login_page()

else:

    sidebar()

    if st.session_state.page == "Dashboard":

        halaman_dashboard()

    elif st.session_state.page == "Data Kayu":

        halaman_data_kayu()

    elif st.session_state.page == "Stok Kayu":

        halaman_stok()

    elif st.session_state.page == "Pelanggan":

        halaman_pelanggan()

    elif st.session_state.page == "Penjualan":

        halaman_penjualan()

    elif st.session_state.page == "Riwayat Transaksi":

        halaman_riwayat()

    elif st.session_state.page == "Laporan":

        halaman_laporan()
