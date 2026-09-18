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
    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nama TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kayu (
            id_kayu INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kayu TEXT NOT NULL,
            satuan TEXT NOT NULL,
            harga REAL NOT NULL,
            stok INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pelanggan (
            id_pelanggan INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pelanggan TEXT NOT NULL,
            no_telepon TEXT,
            alamat TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS penjualan (
            id_penjualan INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            id_pelanggan INTEGER,
            id_user INTEGER,
            total REAL NOT NULL DEFAULT 0,
            FOREIGN KEY(id_pelanggan)
                REFERENCES pelanggan(id_pelanggan)
                ON DELETE SET NULL,
            FOREIGN KEY(id_user)
                REFERENCES users(id_user)
                ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detail_penjualan (
            id_detail INTEGER PRIMARY KEY AUTOINCREMENT,
            id_penjualan INTEGER NOT NULL,
            id_kayu INTEGER NOT NULL,
            jumlah INTEGER NOT NULL,
            harga REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY(id_penjualan)
                REFERENCES penjualan(id_penjualan)
                ON DELETE CASCADE,
            FOREIGN KEY(id_kayu)
                REFERENCES kayu(id_kayu)
                ON DELETE RESTRICT
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (username, password, nama)
        VALUES (?, ?, ?)
    """, (
        "admin",
        "admin123",
        "Administrator"
    ))

    jumlah_kayu = cursor.execute(
        "SELECT COUNT(*) AS jumlah FROM kayu"
    ).fetchone()["jumlah"]

    if jumlah_kayu == 0:
        data_kayu = [
            ("Kayu Jati", "Batang", 150000, 50),
            ("Kayu Meranti", "Batang", 100000, 40),
            ("Kayu Sengon", "Batang", 75000, 60),
            ("Kayu Mahoni", "Batang", 120000, 35),
            ("Kayu Ulin", "Batang", 200000, 25)
        ]

        cursor.executemany("""
            INSERT INTO kayu
            (nama_kayu, satuan, harga, stok)
            VALUES (?, ?, ?, ?)
        """, data_kayu)

    conn.commit()
    conn.close()


# =========================================================
# FORMAT RUPIAH
# =========================================================

def rupiah(nilai):
    return "Rp {:,.0f}".format(
        float(nilai)
    ).replace(",", ".")


# =========================================================
# SESSION STATE
# =========================================================

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None

if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

if "cart_items" not in st.session_state:
    st.session_state.cart_items = []


# =========================================================
# LOGIN
# =========================================================

def halaman_login():

    st.markdown("""
        <style>
        .login-title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            margin-top: 70px;
        }

        .login-subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="login-title">🪵 Sistem Informasi Penjualan Kayu</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Penjualan dan Pengelolaan Stok Kayu Berbasis Web</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        with st.form("form_login_admin"):

            st.subheader("🔐 Login Admin")

            username = st.text_input(
                "Username",
                placeholder="Masukkan username",
                key="field_login_username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password",
                key="field_login_password"
            )

            tombol_login = st.form_submit_button(
                "🔑 Login",
                use_container_width=True
            )

            if tombol_login:

                if not username.strip():
                    st.error("Username wajib diisi.")

                elif not password:
                    st.error("Password wajib diisi.")

                else:

                    conn = get_db()

                    user = conn.execute("""
                        SELECT *
                        FROM users
                        WHERE username = ?
                        AND password = ?
                    """, (
                        username.strip(),
                        password
                    )).fetchone()

                    conn.close()

                    if user:

                        st.session_state.is_logged_in = True
                        st.session_state.current_user_id = user["id_user"]
                        st.session_state.current_user_name = user["nama"]
                        st.session_state.current_page = "Dashboard"

                        st.rerun()

                    else:
                        st.error(
                            "Username atau password salah."
                        )

        st.info(
            "Login demo: **admin** / **admin123**"
        )


# =========================================================
# SIDEBAR
# =========================================================

def tampilkan_sidebar():

    with st.sidebar:

        st.markdown("# 🪵 Sistem Kayu")

        st.caption(
            "Penjualan dan Pengelolaan Stok Kayu"
        )

        st.divider()

        st.write(
            f"👤 **{st.session_state.current_user_name}**"
        )

        st.divider()

        daftar_menu = [
            "Dashboard",
            "Data Kayu",
            "Stok Kayu",
            "Pelanggan",
            "Penjualan",
            "Riwayat Transaksi",
            "Laporan"
        ]

        menu = st.radio(
            "MENU UTAMA",
            daftar_menu,
            index=daftar_menu.index(
                st.session_state.current_page
            ),
            key="navigation_menu"
        )

        st.session_state.current_page = menu

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="button_logout"
        ):

            st.session_state.is_logged_in = False
            st.session_state.current_user_id = None
            st.session_state.current_user_name = None
            st.session_state.cart_items = []
            st.session_state.current_page = "Dashboard"

            st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

def halaman_dashboard():

    st.title("📊 Dashboard")

    st.write(
        f"Selamat datang, **{st.session_state.current_user_name}**."
    )

    conn = get_db()

    jumlah_kayu = conn.execute(
        "SELECT COUNT(*) AS jumlah FROM kayu"
    ).fetchone()["jumlah"]

    total_stok = conn.execute(
        "SELECT COALESCE(SUM(stok), 0) AS jumlah FROM kayu"
    ).fetchone()["jumlah"]

    jumlah_pelanggan = conn.execute(
        "SELECT COUNT(*) AS jumlah FROM pelanggan"
    ).fetchone()["jumlah"]

    jumlah_transaksi = conn.execute(
        "SELECT COUNT(*) AS jumlah FROM penjualan"
    ).fetchone()["jumlah"]

    total_penjualan = conn.execute(
        "SELECT COALESCE(SUM(total), 0) AS total FROM penjualan"
    ).fetchone()["total"]

    conn.close()

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "🪵 Jenis Kayu",
        jumlah_kayu
    )

    col2.metric(
        "📦 Total Stok",
        total_stok
    )

    col3.metric(
        "👥 Pelanggan",
        jumlah_pelanggan
    )

    col4.metric(
        "🧾 Transaksi",
        jumlah_transaksi
    )

    col5.metric(
        "💰 Penjualan",
        rupiah(total_penjualan)
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📦 Kondisi Stok")

        conn = get_db()

        df_stok = pd.read_sql_query("""
            SELECT
                nama_kayu AS 'Nama Kayu',
                satuan AS 'Satuan',
                stok AS 'Stok',
                harga AS 'Harga'
            FROM kayu
            ORDER BY stok ASC
        """, conn)

        conn.close()

        if not df_stok.empty:

            df_stok["Harga"] = (
                df_stok["Harga"].apply(rupiah)
            )

            st.dataframe(
                df_stok,
                use_container_width=True,
                hide_index=True
            )

    with col2:

        st.subheader("🧾 Transaksi Terbaru")

        conn = get_db()

        df_transaksi = pd.read_sql_query("""
            SELECT
                p.id_penjualan AS 'ID Transaksi',
                p.tanggal AS 'Tanggal',
                COALESCE(
                    pl.nama_pelanggan,
                    '-'
                ) AS 'Pelanggan',
                p.total AS 'Total'
            FROM penjualan p
            LEFT JOIN pelanggan pl
                ON p.id_pelanggan = pl.id_pelanggan
            ORDER BY p.id_penjualan DESC
            LIMIT 5
        """, conn)

        conn.close()

        if not df_transaksi.empty:

            df_transaksi["Total"] = (
                df_transaksi["Total"].apply(rupiah)
            )

            st.dataframe(
                df_transaksi,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("Belum ada transaksi.")


# =========================================================
# DATA KAYU
# =========================================================

def halaman_data_kayu():

    st.title("🪵 Data Kayu")

    tab_data, tab_tambah = st.tabs([
        "📋 Data Kayu",
        "➕ Tambah Kayu"
    ])

    with tab_data:

        conn = get_db()

        df = pd.read_sql_query("""
            SELECT
                id_kayu AS 'ID',
                nama_kayu AS 'Nama Kayu',
                satuan AS 'Satuan',
                harga AS 'Harga',
                stok AS 'Stok'
            FROM kayu
            ORDER BY id_kayu DESC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "Belum ada data kayu."
            )

        else:

            tabel = df.copy()

            tabel["Harga"] = (
                tabel["Harga"].apply(rupiah)
            )

            st.dataframe(
                tabel,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader(
                "✏️ Edit Data Kayu"
            )

            pilihan_id = st.selectbox(
                "Pilih kayu",
                df["ID"].tolist(),
                format_func=lambda x:
                    f"ID {x} - {df.loc[df['ID'] == x, 'Nama Kayu'].iloc[0]}",
                key="select_edit_kayu"
            )

            conn = get_db()

            data = conn.execute("""
                SELECT *
                FROM kayu
                WHERE id_kayu = ?
            """, (pilihan_id,)).fetchone()

            conn.close()

            with st.form("form_edit_data_kayu"):

                nama = st.text_input(
                    "Nama Kayu",
                    value=data["nama_kayu"]
                )

                daftar_satuan = [
                    "Batang",
                    "Kubik",
                    "Papan",
                    "Balok",
                    "Lembar"
                ]

                if data["satuan"] in daftar_satuan:
                    index_satuan = daftar_satuan.index(
                        data["satuan"]
                    )
                else:
                    index_satuan = 0

                satuan = st.selectbox(
                    "Satuan",
                    daftar_satuan,
                    index=index_satuan
                )

                harga = st.number_input(
                    "Harga",
                    min_value=0,
                    value=int(data["harga"]),
                    step=1000
                )

                stok = st.number_input(
                    "Stok",
                    min_value=0,
                    value=int(data["stok"]),
                    step=1
                )

                simpan = st.form_submit_button(
                    "💾 Simpan Perubahan",
                    use_container_width=True
                )

                if simpan:

                    if not nama.strip():

                        st.error(
                            "Nama kayu wajib diisi."
                        )

                    elif harga <= 0:

                        st.error(
                            "Harga harus lebih dari 0."
                        )

                    else:

                        conn = get_db()

                        conn.execute("""
                            UPDATE kayu
                            SET nama_kayu = ?,
                                satuan = ?,
                                harga = ?,
                                stok = ?
                            WHERE id_kayu = ?
                        """, (
                            nama.strip(),
                            satuan,
                            harga,
                            stok,
                            pilihan_id
                        ))

                        conn.commit()
                        conn.close()

                        st.success(
                            "Data kayu berhasil diperbarui."
                        )

                        st.rerun()

            st.divider()

            st.subheader(
                "🗑️ Hapus Data Kayu"
            )

            st.warning(
                "Kayu yang sudah digunakan dalam transaksi "
                "tidak dapat dihapus."
            )

            if st.button(
                "🗑️ Hapus Data Kayu",
                use_container_width=True,
                key="button_hapus_kayu"
            ):

                conn = get_db()

                try:

                    conn.execute("""
                        DELETE FROM kayu
                        WHERE id_kayu = ?
                    """, (pilihan_id,))

                    conn.commit()
                    conn.close()

                    st.success(
                        "Data kayu berhasil dihapus."
                    )

                    st.rerun()

                except sqlite3.IntegrityError:

                    conn.close()

                    st.error(
                        "Data tidak dapat dihapus "
                        "karena sudah digunakan dalam transaksi."
                    )

    with tab_tambah:

        st.subheader(
            "➕ Tambah Data Kayu"
        )

        with st.form("form_tambah_data_kayu"):

            nama = st.text_input(
                "Nama Kayu",
                placeholder="Contoh: Kayu Jati"
            )

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
                min_value=0,
                value=0,
                step=1000
            )

            stok = st.number_input(
                "Stok Awal",
                min_value=0,
                value=0,
                step=1
            )

            tambah = st.form_submit_button(
                "➕ Tambahkan Kayu",
                use_container_width=True
            )

            if tambah:

                if not nama.strip():

                    st.error(
                        "Nama kayu wajib diisi."
                    )

                elif harga <= 0:

                    st.error(
                        "Harga harus lebih dari 0."
                    )

                else:

                    conn = get_db()

                    conn.execute("""
                        INSERT INTO kayu
                        (nama_kayu, satuan, harga, stok)
                        VALUES (?, ?, ?, ?)
                    """, (
                        nama.strip(),
                        satuan,
                        harga,
                        stok
                    ))

                    conn.commit()
                    conn.close()

                    st.success(
                        "Data kayu berhasil ditambahkan."
                    )

                    st.rerun()


# =========================================================
# STOK
# =========================================================

def halaman_stok():

    st.title("📦 Stok Kayu")

    conn = get_db()

    df = pd.read_sql_query("""
        SELECT
            id_kayu AS 'ID',
            nama_kayu AS 'Nama Kayu',
            satuan AS 'Satuan',
            stok AS 'Stok',
            harga AS 'Harga'
        FROM kayu
        ORDER BY stok ASC
    """, conn)

    conn.close()

    if df.empty:

        st.info(
            "Belum ada data stok."
        )

        return

    def status_stok(nilai):

        if nilai <= 5:
            return "🔴 Sangat Rendah"

        elif nilai <= 10:
            return "🟠 Rendah"

        return "🟢 Aman"

    tabel = df.copy()

    tabel["Status"] = (
        tabel["Stok"].apply(status_stok)
    )

    tabel["Harga"] = (
        tabel["Harga"].apply(rupiah)
    )

    st.dataframe(
        tabel,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🔴 Sangat Rendah",
        len(df[df["Stok"] <= 5])
    )

    col2.metric(
        "🟠 Rendah",
        len(
            df[
                (df["Stok"] > 5) &
                (df["Stok"] <= 10)
            ]
        )
    )

    col3.metric(
        "🟢 Aman",
        len(df[df["Stok"] > 10])
    )


# =========================================================
# PELANGGAN
# =========================================================

def halaman_pelanggan():

    st.title("👥 Data Pelanggan")

    tab_data, tab_tambah = st.tabs([
        "📋 Data Pelanggan",
        "➕ Tambah Pelanggan"
    ])

    with tab_data:

        conn = get_db()

        df = pd.read_sql_query("""
            SELECT
                id_pelanggan AS 'ID',
                nama_pelanggan AS 'Nama Pelanggan',
                no_telepon AS 'No. Telepon',
                alamat AS 'Alamat'
            FROM pelanggan
            ORDER BY id_pelanggan DESC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "Belum ada data pelanggan."
            )

        else:

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            pilihan_id = st.selectbox(
                "Pilih pelanggan",
                df["ID"].tolist(),
                format_func=lambda x:
                    f"ID {x} - {df.loc[df['ID'] == x, 'Nama Pelanggan'].iloc[0]}",
                key="select_edit_pelanggan"
            )

            conn = get_db()

            data = conn.execute("""
                SELECT *
                FROM pelanggan
                WHERE id_pelanggan = ?
            """, (pilihan_id,)).fetchone()

            conn.close()

            with st.form("form_edit_pelanggan"):

                nama = st.text_input(
                    "Nama Pelanggan",
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

                simpan = st.form_submit_button(
                    "💾 Simpan Perubahan",
                    use_container_width=True
                )

                if simpan:

                    if not nama.strip():

                        st.error(
                            "Nama pelanggan wajib diisi."
                        )

                    else:

                        conn = get_db()

                        conn.execute("""
                            UPDATE pelanggan
                            SET nama_pelanggan = ?,
                                no_telepon = ?,
                                alamat = ?
                            WHERE id_pelanggan = ?
                        """, (
                            nama.strip(),
                            telepon.strip(),
                            alamat.strip(),
                            pilihan_id
                        ))

                        conn.commit()
                        conn.close()

                        st.success(
                            "Data pelanggan berhasil diperbarui."
                        )

                        st.rerun()

            st.divider()

            if st.button(
                "🗑️ Hapus Pelanggan",
                use_container_width=True,
                key="button_hapus_pelanggan"
            ):

                conn = get_db()

                conn.execute("""
                    DELETE FROM pelanggan
                    WHERE id_pelanggan = ?
                """, (pilihan_id,))

                conn.commit()
                conn.close()

                st.success(
                    "Pelanggan berhasil dihapus."
                )

                st.rerun()

    with tab_tambah:

        with st.form("form_tambah_pelanggan"):

            nama = st.text_input(
                "Nama Pelanggan"
            )

            telepon = st.text_input(
                "No. Telepon"
            )

            alamat = st.text_area(
                "Alamat"
            )

            tambah = st.form_submit_button(
                "➕ Tambahkan Pelanggan",
                use_container_width=True
            )

            if tambah:

                if not nama.strip():

                    st.error(
                        "Nama pelanggan wajib diisi."
                    )

                else:

                    conn = get_db()

                    conn.execute("""
                        INSERT INTO pelanggan
                        (nama_pelanggan, no_telepon, alamat)
                        VALUES (?, ?, ?)
                    """, (
                        nama.strip(),
                        telepon.strip(),
                        alamat.strip()
                    ))

                    conn.commit()
                    conn.close()

                    st.success(
                        "Pelanggan berhasil ditambahkan."
                    )

                    st.rerun()


# =========================================================
# PENJUALAN
# =========================================================

def halaman_penjualan():

    st.title("🛒 Transaksi Penjualan")

    conn = get_db()

    pelanggan_df = pd.read_sql_query("""
        SELECT
            id_pelanggan,
            nama_pelanggan
        FROM pelanggan
        ORDER BY nama_pelanggan
    """, conn)

    kayu_df = pd.read_sql_query("""
        SELECT
            id_kayu,
            nama_kayu,
            satuan,
            harga,
            stok
        FROM kayu
        ORDER BY nama_kayu
    """, conn)

    conn.close()

    if pelanggan_df.empty:

        st.warning(
            "Belum ada pelanggan. "
            "Tambahkan pelanggan terlebih dahulu."
        )

        return

    if kayu_df.empty:

        st.warning(
            "Belum ada data kayu."
        )

        return

    st.subheader("1. Data Pelanggan")

    pelanggan_dict = dict(
        zip(
            pelanggan_df["id_pelanggan"],
            pelanggan_df["nama_pelanggan"]
        )
    )

    id_pelanggan = st.selectbox(
        "Pilih Pelanggan",
        list(pelanggan_dict.keys()),
        format_func=lambda x:
            pelanggan_dict[x],
        key="select_pelanggan_transaksi"
    )

    st.divider()

    st.subheader("2. Tambahkan Barang")

    col1, col2, col3 = st.columns(
        [3, 2, 2]
    )

    with col1:

        id_kayu = st.selectbox(
            "Pilih Kayu",
            kayu_df["id_kayu"].tolist(),
            format_func=lambda x:
                f"{kayu_df.loc[kayu_df['id_kayu'] == x, 'nama_kayu'].iloc[0]} | Stok: {kayu_df.loc[kayu_df['id_kayu'] == x, 'stok'].iloc[0]}",
            key="select_kayu_transaksi"
        )

    data_kayu = kayu_df[
        kayu_df["id_kayu"] == id_kayu
    ].iloc[0]

    with col2:

        st.text_input(
            "Harga",
            value=rupiah(
                data_kayu["harga"]
            ),
            disabled=True,
            key="display_harga_transaksi"
        )

    stok_tersedia = int(
        data_kayu["stok"]
    )

    with col3:

        if stok_tersedia > 0:

            jumlah = st.number_input(
                "Jumlah",
                min_value=1,
                max_value=stok_tersedia,
                value=1,
                step=1,
                key="jumlah_transaksi"
            )

        else:

            st.warning(
                "Stok habis."
            )

            jumlah = 0

    subtotal = (
        float(data_kayu["harga"]) *
        int(jumlah)
    )

    st.info(
        f"Subtotal: **{rupiah(subtotal)}**"
    )

    if st.button(
        "➕ Masukkan ke Keranjang",
        use_container_width=True,
        key="button_tambah_keranjang"
    ):

        if stok_tersedia <= 0:

            st.error(
                "Stok kayu habis."
            )

        elif jumlah <= 0:

            st.error(
                "Jumlah harus lebih dari 0."
            )

        else:

            ditemukan = False

            for item in st.session_state.cart_items:

                if item["id_kayu"] == int(id_kayu):

                    jumlah_baru = (
                        item["jumlah"] +
                        int(jumlah)
                    )

                    if jumlah_baru > stok_tersedia:

                        st.error(
                            "Jumlah melebihi stok tersedia."
                        )

                    else:

                        item["jumlah"] = jumlah_baru

                        item["subtotal"] = (
                            jumlah_baru *
                            float(data_kayu["harga"])
                        )

                        st.success(
                            "Jumlah barang diperbarui."
                        )

                    ditemukan = True
                    break

            if not ditemukan:

                st.session_state.cart_items.append({
                    "id_kayu": int(id_kayu),
                    "nama_kayu": data_kayu["nama_kayu"],
                    "satuan": data_kayu["satuan"],
                    "harga": float(data_kayu["harga"]),
                    "jumlah": int(jumlah),
                    "subtotal": float(subtotal)
                })

                st.success(
                    "Barang berhasil dimasukkan ke keranjang."
                )

            st.rerun()

    st.divider()

    st.subheader("3. Keranjang Penjualan")

    if not st.session_state.cart_items:

        st.info(
            "Keranjang masih kosong."
        )

        return

    tabel = []

    for nomor, item in enumerate(
        st.session_state.cart_items,
        start=1
    ):

        tabel.append({
            "No": nomor,
            "Kayu": item["nama_kayu"],
            "Satuan": item["satuan"],
            "Harga": rupiah(item["harga"]),
            "Jumlah": item["jumlah"],
            "Subtotal": rupiah(item["subtotal"])
        })

    st.dataframe(
        pd.DataFrame(tabel),
        use_container_width=True,
        hide_index=True
    )

    total = sum(
        item["subtotal"]
        for item in st.session_state.cart_items
    )

    st.markdown(
        f"## 💰 Total: {rupiah(total)}"
    )

    pilihan_hapus = st.selectbox(
        "Pilih barang untuk dihapus",
        range(
            len(
                st.session_state.cart_items
            )
        ),
        format_func=lambda x:
            st.session_state.cart_items[x]["nama_kayu"],
        key="select_hapus_keranjang"
    )

    if st.button(
        "🗑️ Hapus Barang",
        use_container_width=True,
        key="button_hapus_keranjang"
    ):

        st.session_state.cart_items.pop(
            pilihan_hapus
        )

        st.rerun()

    st.divider()

    st.subheader(
        "4. Simpan Transaksi"
    )

    if st.button(
        "💾 SIMPAN TRANSAKSI",
        type="primary",
        use_container_width=True,
        key="button_simpan_transaksi"
    ):

        conn = get_db()

        try:

            # Cek stok terbaru
            for item in st.session_state.cart_items:

                stok_db = conn.execute("""
                    SELECT stok
                    FROM kayu
                    WHERE id_kayu = ?
                """, (
                    item["id_kayu"],
                )).fetchone()

                if stok_db is None:

                    raise Exception(
                        f"Kayu {item['nama_kayu']} tidak ditemukan."
                    )

                if int(stok_db["stok"]) < int(
                    item["jumlah"]
                ):

                    raise Exception(
                        f"Stok {item['nama_kayu']} tidak mencukupi."
                    )

            tanggal = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            cursor = conn.execute("""
                INSERT INTO penjualan
                (tanggal, id_pelanggan, id_user, total)
                VALUES (?, ?, ?, ?)
            """, (
                tanggal,
                id_pelanggan,
                st.session_state.current_user_id,
                total
            ))

            id_transaksi = cursor.lastrowid

            for item in st.session_state.cart_items:

                conn.execute("""
                    INSERT INTO detail_penjualan
                    (
                        id_penjualan,
                        id_kayu,
                        jumlah,
                        harga,
                        subtotal
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    id_transaksi,
                    item["id_kayu"],
                    item["jumlah"],
                    item["harga"],
                    item["subtotal"]
                ))

                conn.execute("""
                    UPDATE kayu
                    SET stok = stok - ?
                    WHERE id_kayu = ?
                """, (
                    item["jumlah"],
                    item["id_kayu"]
                ))

            conn.commit()

            st.session_state.cart_items = []

            st.success(
                f"Transaksi berhasil disimpan. "
                f"ID Transaksi: {id_transaksi}"
            )

            st.session_state.current_page = (
                "Riwayat Transaksi"
            )

            st.rerun()

        except Exception as error:

            conn.rollback()

            st.error(
                f"Transaksi gagal: {error}"
            )

        finally:

            conn.close()


# =========================================================
# RIWAYAT TRANSAKSI
# =========================================================

def halaman_riwayat():

    st.title("📜 Riwayat Transaksi")

    conn = get_db()

    df = pd.read_sql_query("""
        SELECT
            p.id_penjualan AS 'ID Transaksi',
            p.tanggal AS 'Tanggal',
            COALESCE(
                pl.nama_pelanggan,
                '-'
            ) AS 'Pelanggan',
            COALESCE(
                u.nama,
                '-'
            ) AS 'Admin',
            p.total AS 'Total'
        FROM penjualan p

        LEFT JOIN pelanggan pl
            ON p.id_pelanggan = pl.id_pelanggan

        LEFT JOIN users u
            ON p.id_user = u.id_user

        ORDER BY p.id_penjualan DESC
    """, conn)

    conn.close()

    if df.empty:

        st.info(
            "Belum ada transaksi."
        )

        return

    tabel = df.copy()

    tabel["Total"] = (
        tabel["Total"].apply(rupiah)
    )

    st.dataframe(
        tabel,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🧾 Detail Transaksi"
    )

    id_transaksi = st.selectbox(
        "Pilih ID Transaksi",
        df["ID Transaksi"].tolist(),
        key="select_detail_transaksi"
    )

    tampilkan_detail_transaksi(
        id_transaksi
    )


# =========================================================
# DETAIL TRANSAKSI
# =========================================================

def tampilkan_detail_transaksi(
    id_transaksi
):

    conn = get_db()

    transaksi = conn.execute("""
        SELECT
            p.*,
            COALESCE(
                pl.nama_pelanggan,
                '-'
            ) AS nama_pelanggan,
            COALESCE(
                pl.no_telepon,
                '-'
            ) AS no_telepon,
            COALESCE(
                pl.alamat,
                '-'
            ) AS alamat,
            COALESCE(
                u.nama,
                '-'
            ) AS nama_admin
        FROM penjualan p

        LEFT JOIN pelanggan pl
            ON p.id_pelanggan =
               pl.id_pelanggan

        LEFT JOIN users u
            ON p.id_user =
               u.id_user

        WHERE p.id_penjualan = ?
    """, (
        id_transaksi,
    )).fetchone()

    detail = conn.execute("""
        SELECT
            d.*,
            k.nama_kayu,
            k.satuan
        FROM detail_penjualan d

        JOIN kayu k
            ON d.id_kayu = k.id_kayu

        WHERE d.id_penjualan = ?

        ORDER BY d.id_detail
    """, (
        id_transaksi,
    )).fetchall()

    conn.close()

    if transaksi is None:

        st.error(
            "Transaksi tidak ditemukan."
        )

        return

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**ID Transaksi:** "
            f"{transaksi['id_penjualan']}"
        )

        st.write(
            f"**Tanggal:** "
            f"{transaksi['tanggal']}"
        )

    with col2:

        st.write(
            f"**Pelanggan:** "
            f"{transaksi['nama_pelanggan']}"
        )

        st.write(
            f"**Admin:** "
            f"{transaksi['nama_admin']}"
        )

    data = []

    for item in detail:

        data.append({
            "Kayu": item["nama_kayu"],
            "Satuan": item["satuan"],
            "Jumlah": item["jumlah"],
            "Harga": rupiah(item["harga"]),
            "Subtotal": rupiah(item["subtotal"])
        })

    st.dataframe(
        pd.DataFrame(data),
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        f"## 💰 Total: {rupiah(transaksi['total'])}"
    )

    nota = ""

    nota += "========================================\n"
    nota += "          NOTA PENJUALAN KAYU\n"
    nota += "========================================\n"
    nota += (
        f"ID Transaksi : "
        f"{transaksi['id_penjualan']}\n"
    )
    nota += (
        f"Tanggal      : "
        f"{transaksi['tanggal']}\n"
    )
    nota += (
        f"Pelanggan    : "
        f"{transaksi['nama_pelanggan']}\n"
    )
    nota += (
        f"No. Telepon  : "
        f"{transaksi['no_telepon']}\n"
    )
    nota += "----------------------------------------\n"

    for item in detail:

        nota += (
            f"{item['nama_kayu']} "
            f"({item['jumlah']} {item['satuan']})\n"
        )

        nota += (
            f"{rupiah(item['harga'])} x "
            f"{item['jumlah']} = "
            f"{rupiah(item['subtotal'])}\n"
        )

    nota += "----------------------------------------\n"

    nota += (
        f"TOTAL: "
        f"{rupiah(transaksi['total'])}\n"
    )

    nota += "========================================\n"
    nota += (
        f"Admin: "
        f"{transaksi['nama_admin']}\n"
    )
    nota += "========================================\n"

    st.download_button(
        "⬇️ Download Nota",
        data=nota,
        file_name=f"nota_{id_transaksi}.txt",
        mime="text/plain",
        use_container_width=True,
        key="button_download_nota"
    )


# =========================================================
# LAPORAN
# =========================================================

def halaman_laporan():

    st.title("📑 Laporan")

    tab_penjualan, tab_stok = st.tabs([
        "💰 Laporan Penjualan",
        "📦 Laporan Stok"
    ])

    # =====================================================
    # LAPORAN PENJUALAN
    # =====================================================

    with tab_penjualan:

        st.subheader(
            "💰 Laporan Penjualan"
        )

        conn = get_db()

        df = pd.read_sql_query("""
            SELECT
                p.id_penjualan AS 'ID Transaksi',
                p.tanggal AS 'Tanggal',
                COALESCE(
                    pl.nama_pelanggan,
                    '-'
                ) AS 'Pelanggan',
                p.total AS 'Total'
            FROM penjualan p

            LEFT JOIN pelanggan pl
                ON p.id_pelanggan =
                   pl.id_pelanggan

            ORDER BY p.id_penjualan DESC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "Belum ada data penjualan."
            )

        else:

            df["Tanggal"] = pd.to_datetime(
                df["Tanggal"]
            )

            tanggal_awal = st.date_input(
                "Tanggal Awal",
                value=df["Tanggal"].min().date(),
                key="filter_tanggal_awal"
            )

            tanggal_akhir = st.date_input(
                "Tanggal Akhir",
                value=df["Tanggal"].max().date(),
                key="filter_tanggal_akhir"
            )

            if tanggal_awal > tanggal_akhir:

                st.error(
                    "Tanggal awal tidak boleh "
                    "lebih besar dari tanggal akhir."
                )

            else:

                hasil = df[
                    (df["Tanggal"].dt.date >= tanggal_awal) &
                    (df["Tanggal"].dt.date <= tanggal_akhir)
                ].copy()

                total_laporan = hasil[
                    "Total"
                ].sum()

                col1, col2 = st.columns(2)

                col1.metric(
                    "Jumlah Transaksi",
                    len(hasil)
                )

                col2.metric(
                    "Total Penjualan",
                    rupiah(total_laporan)
                )

                hasil["Tanggal"] = hasil[
                    "Tanggal"
                ].dt.strftime(
                    "%d-%m-%Y %H:%M"
                )

                hasil["Total"] = hasil[
                    "Total"
                ].apply(rupiah)

                st.dataframe(
                    hasil,
                    use_container_width=True,
                    hide_index=True
                )

                csv = hasil.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "⬇️ Download Laporan Penjualan",
                    data=csv,
                    file_name="laporan_penjualan.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="button_download_laporan_penjualan"
                )

    # =====================================================
    # LAPORAN STOK
    # =====================================================

    with tab_stok:

        st.subheader(
            "📦 Laporan Stok Kayu"
        )

        conn = get_db()

        df = pd.read_sql_query("""
            SELECT
                id_kayu AS 'ID',
                nama_kayu AS 'Nama Kayu',
                satuan AS 'Satuan',
                stok AS 'Stok',
                harga AS 'Harga'
            FROM kayu
            ORDER BY stok ASC
        """, conn)

        conn.close()

        if df.empty:

            st.info(
                "Belum ada data stok."
            )

        else:

            def status_laporan(nilai):

                if nilai <= 5:
                    return "Sangat Rendah"

                elif nilai <= 10:
                    return "Rendah"

                return "Aman"

            hasil = df.copy()

            hasil["Status"] = (
                hasil["Stok"].apply(
                    status_laporan
                )
            )

            tampil = hasil.copy()

            tampil["Harga"] = (
                tampil["Harga"].apply(rupiah)
            )

            st.dataframe(
                tampil,
                use_container_width=True,
                hide_index=True
            )

            csv = hasil.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Laporan Stok",
                data=csv,
                file_name="laporan_stok.csv",
                mime="text/csv",
                use_container_width=True,
                key="button_download_laporan_stok"
            )


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 10px;
    padding: 12px;
}

.stButton > button {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# JALANKAN DATABASE
# =========================================================

init_db()


# =========================================================
# MAIN PROGRAM
# =========================================================

if not st.session_state.is_logged_in:

    halaman_login()

else:

    tampilkan_sidebar()

    if st.session_state.current_page == "Dashboard":

        halaman_dashboard()

    elif st.session_state.current_page == "Data Kayu":

        halaman_data_kayu()

    elif st.session_state.current_page == "Stok Kayu":

        halaman_stok()

    elif st.session_state.current_page == "Pelanggan":

        halaman_pelanggan()

    elif st.session_state.current_page == "Penjualan":

        halaman_penjualan
    elif st.session_state.current_page == "Riwayat Transaksi":

        halaman_riwayat()

    elif st.session_state.current_page == "Laporan":

        halaman_laporan()
