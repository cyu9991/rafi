import hashlib
import hmac
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import pandas as pd
import streamlit as st

# =========================================================
# KONFIGURASI
# =========================================================

st.set_page_config(
    page_title="Sistem Informasi Penjualan Kayu",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_NAME = "kayu.db"

# Ambang batas status stok (dipakai di semua halaman)
STOK_SANGAT_RENDAH = 5
STOK_RENDAH = 10

DAFTAR_SATUAN = ["Batang", "Kubik", "Papan", "Balok", "Lembar"]

DAFTAR_MENU = [
    "Dashboard",
    "Data Kayu",
    "Stok Kayu",
    "Pelanggan",
    "Penjualan",
    "Riwayat Transaksi",
    "Laporan",
]

st.markdown(
    """
    <style>
    .main { padding-top: 1rem; }
    [data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 10px;
        padding: 12px;
    }
    .stButton > button { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# KEAMANAN PASSWORD
# =========================================================

def hash_password(password, salt=None):
    """Hash password dengan PBKDF2-SHA256. Format: pbkdf2$salt$hash"""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000,
    )
    return f"pbkdf2${salt}${digest.hex()}"


def verify_password(password, stored):
    try:
        _, salt, _ = stored.split("$")
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db():
    """Koneksi otomatis commit / rollback / close."""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def query_df(sql, params=()):
    with db() as conn:
        return pd.read_sql_query(sql, conn, params=params)


@st.cache_resource
def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id_user INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nama TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS kayu (
                id_kayu INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_kayu TEXT NOT NULL,
                satuan TEXT NOT NULL,
                harga REAL NOT NULL,
                stok INTEGER NOT NULL DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS pelanggan (
                id_pelanggan INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pelanggan TEXT NOT NULL,
                no_telepon TEXT,
                alamat TEXT
            )
        """)

        conn.execute("""
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

        conn.execute("""
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

        # Akun admin default (password di-hash)
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password, nama) "
            "VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "Administrator"),
        )

        # Migrasi: hash password lama yang masih teks biasa
        for user in conn.execute(
            "SELECT id_user, password FROM users"
        ).fetchall():
            if not user["password"].startswith("pbkdf2$"):
                conn.execute(
                    "UPDATE users SET password = ? WHERE id_user = ?",
                    (hash_password(user["password"]), user["id_user"]),
                )

        jumlah_kayu = conn.execute(
            "SELECT COUNT(*) AS jumlah FROM kayu"
        ).fetchone()["jumlah"]

        if jumlah_kayu == 0:
            conn.executemany(
                "INSERT INTO kayu (nama_kayu, satuan, harga, stok) "
                "VALUES (?, ?, ?, ?)",
                [
                    ("Kayu Jati", "Batang", 150000, 50),
                    ("Kayu Meranti", "Batang", 100000, 40),
                    ("Kayu Sengon", "Batang", 75000, 60),
                    ("Kayu Mahoni", "Batang", 120000, 35),
                    ("Kayu Ulin", "Batang", 200000, 25),
                ],
            )

    return True


# =========================================================
# UTILITAS
# =========================================================

def rupiah(nilai):
    return "Rp {:,.0f}".format(float(nilai)).replace(",", ".")


def status_stok(nilai, emoji=True):
    if nilai <= STOK_SANGAT_RENDAH:
        return "🔴 Sangat Rendah" if emoji else "Sangat Rendah"
    if nilai <= STOK_RENDAH:
        return "🟠 Rendah" if emoji else "Rendah"
    return "🟢 Aman" if emoji else "Aman"


def set_flash(pesan, level="success"):
    """Simpan pesan agar tetap tampil setelah st.rerun()."""
    st.session_state.flash = (level, pesan)


def show_flash():
    flash = st.session_state.pop("flash", None)
    if flash:
        level, pesan = flash
        getattr(st, level)(pesan)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "is_logged_in": False,
    "current_user_id": None,
    "current_user_name": None,
    "cart_items": [],
}

for _key, _value in DEFAULT_STATE.items():
    if _key not in st.session_state:
        st.session_state[_key] = _value


# =========================================================
# LOGIN
# =========================================================

def halaman_login():
    st.markdown(
        """
        <style>
        .login-title {
            text-align: center; font-size: 36px;
            font-weight: bold; margin-top: 70px;
        }
        .login-subtitle {
            text-align: center; color: #666; margin-bottom: 30px;
        }
        </style>
        <div class="login-title">🪵 Sistem Informasi Penjualan Kayu</div>
        <div class="login-subtitle">
            Penjualan dan Pengelolaan Stok Kayu Berbasis Web
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, col2, _ = st.columns([1, 2, 1])

    with col2:
        with st.form("form_login_admin"):
            st.subheader("🔐 Login Admin")

            username = st.text_input(
                "Username", placeholder="Masukkan username"
            )
            password = st.text_input(
                "Password", type="password",
                placeholder="Masukkan password",
            )

            tombol_login = st.form_submit_button(
                "🔑 Login", use_container_width=True
            )

        if tombol_login:
            if not username.strip():
                st.error("Username wajib diisi.")
            elif not password:
                st.error("Password wajib diisi.")
            else:
                with db() as conn:
                    user = conn.execute(
                        "SELECT * FROM users WHERE username = ?",
                        (username.strip(),),
                    ).fetchone()

                if user and verify_password(password, user["password"]):
                    st.session_state.is_logged_in = True
                    st.session_state.current_user_id = user["id_user"]
                    st.session_state.current_user_name = user["nama"]
                    st.rerun()
                else:
                    st.error("Username atau password salah.")

        st.info("Login demo: **admin** / **admin123**")


# =========================================================
# SIDEBAR
# =========================================================

def logout():
    st.session_state.is_logged_in = False
    st.session_state.current_user_id = None
    st.session_state.current_user_name = None
    st.session_state.cart_items = []
    st.session_state.pop("pending_page", None)
    st.session_state.pop("flash", None)


def tampilkan_sidebar():
    # Pindah halaman terjadwal (harus diterapkan sebelum radio dibuat)
    if "pending_page" in st.session_state:
        st.session_state.navigation_menu = st.session_state.pop(
            "pending_page"
        )

    with st.sidebar:
        st.markdown("# 🪵 Sistem Kayu")
        st.caption("Penjualan dan Pengelolaan Stok Kayu")
        st.divider()
        st.write(f"👤 **{st.session_state.current_user_name}**")
        st.divider()

        menu = st.radio(
            "MENU UTAMA", DAFTAR_MENU, key="navigation_menu"
        )

        st.divider()
        st.button(
            "🚪 Logout",
            use_container_width=True,
            on_click=logout,
            key="button_logout",
        )

    return menu


# =========================================================
# DASHBOARD
# =========================================================

def halaman_dashboard():
    st.title("📊 Dashboard")
    st.write(f"Selamat datang, **{st.session_state.current_user_name}**.")

    with db() as conn:
        jumlah_kayu = conn.execute(
            "SELECT COUNT(*) AS n FROM kayu"
        ).fetchone()["n"]
        total_stok = conn.execute(
            "SELECT COALESCE(SUM(stok), 0) AS n FROM kayu"
        ).fetchone()["n"]
        jumlah_pelanggan = conn.execute(
            "SELECT COUNT(*) AS n FROM pelanggan"
        ).fetchone()["n"]
        jumlah_transaksi = conn.execute(
            "SELECT COUNT(*) AS n FROM penjualan"
        ).fetchone()["n"]
        total_penjualan = conn.execute(
            "SELECT COALESCE(SUM(total), 0) AS n FROM penjualan"
        ).fetchone()["n"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🪵 Jenis Kayu", jumlah_kayu)
    c2.metric("📦 Total Stok", total_stok)
    c3.metric("👥 Pelanggan", jumlah_pelanggan)
    c4.metric("🧾 Transaksi", jumlah_transaksi)
    c5.metric("💰 Penjualan", rupiah(total_penjualan))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Kondisi Stok")

        df_stok = query_df("""
            SELECT nama_kayu AS 'Nama Kayu', satuan AS 'Satuan',
                   stok AS 'Stok', harga AS 'Harga'
            FROM kayu
            ORDER BY stok ASC
        """)

        if df_stok.empty:
            st.info("Belum ada data kayu.")
        else:
            df_stok["Harga"] = df_stok["Harga"].apply(rupiah)
            st.dataframe(
                df_stok, use_container_width=True, hide_index=True
            )

    with col2:
        st.subheader("🧾 Transaksi Terbaru")

        df_transaksi = query_df("""
            SELECT p.id_penjualan AS 'ID Transaksi',
                   p.tanggal AS 'Tanggal',
                   COALESCE(pl.nama_pelanggan, '-') AS 'Pelanggan',
                   p.total AS 'Total'
            FROM penjualan p
            LEFT JOIN pelanggan pl ON p.id_pelanggan = pl.id_pelanggan
            ORDER BY p.id_penjualan DESC
            LIMIT 5
        """)

        if df_transaksi.empty:
            st.info("Belum ada transaksi.")
        else:
            df_transaksi["Total"] = df_transaksi["Total"].apply(rupiah)
            st.dataframe(
                df_transaksi, use_container_width=True, hide_index=True
            )


# =========================================================
# DATA KAYU
# =========================================================

def halaman_data_kayu():
    st.title("🪵 Data Kayu")

    tab_data, tab_tambah = st.tabs(["📋 Data Kayu", "➕ Tambah Kayu"])

    with tab_data:
        df = query_df("""
            SELECT id_kayu AS 'ID', nama_kayu AS 'Nama Kayu',
                   satuan AS 'Satuan', harga AS 'Harga', stok AS 'Stok'
            FROM kayu
            ORDER BY id_kayu DESC
        """)

        if df.empty:
            st.info("Belum ada data kayu.")
        else:
            tabel = df.copy()
            tabel["Harga"] = tabel["Harga"].apply(rupiah)
            st.dataframe(tabel, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("✏️ Edit Data Kayu")

            nama_map = dict(zip(df["ID"].tolist(), df["Nama Kayu"]))

            pilihan_id = int(
                st.selectbox(
                    "Pilih kayu",
                    df["ID"].tolist(),
                    format_func=lambda x: f"ID {x} - {nama_map[x]}",
                    key="select_edit_kayu",
                )
            )

            with db() as conn:
                data = conn.execute(
                    "SELECT * FROM kayu WHERE id_kayu = ?", (pilihan_id,)
                ).fetchone()

            with st.form(f"form_edit_kayu_{pilihan_id}"):
                nama = st.text_input("Nama Kayu", value=data["nama_kayu"])

                index_satuan = (
                    DAFTAR_SATUAN.index(data["satuan"])
                    if data["satuan"] in DAFTAR_SATUAN
                    else 0
                )
                satuan = st.selectbox(
                    "Satuan", DAFTAR_SATUAN, index=index_satuan
                )
                harga = st.number_input(
                    "Harga", min_value=0,
                    value=int(data["harga"]), step=1000,
                )
                stok = st.number_input(
                    "Stok", min_value=0,
                    value=int(data["stok"]), step=1,
                )
                simpan = st.form_submit_button(
                    "💾 Simpan Perubahan", use_container_width=True
                )

            if simpan:
                if not nama.strip():
                    st.error("Nama kayu wajib diisi.")
                elif harga <= 0:
                    st.error("Harga harus lebih dari 0.")
                else:
                    with db() as conn:
                        conn.execute(
                            "UPDATE kayu SET nama_kayu = ?, satuan = ?, "
                            "harga = ?, stok = ? WHERE id_kayu = ?",
                            (nama.strip(), satuan, harga, stok, pilihan_id),
                        )
                    set_flash("Data kayu berhasil diperbarui.")
                    st.rerun()

            st.divider()
            st.subheader("🗑️ Hapus Data Kayu")
            st.warning(
                "Kayu yang sudah digunakan dalam transaksi "
                "tidak dapat dihapus."
            )

            yakin = st.checkbox(
                "Saya yakin ingin menghapus kayu ini",
                key=f"konfirmasi_hapus_kayu_{pilihan_id}",
            )

            if st.button(
                "🗑️ Hapus Data Kayu",
                use_container_width=True,
                disabled=not yakin,
                key="button_hapus_kayu",
            ):
                try:
                    with db() as conn:
                        conn.execute(
                            "DELETE FROM kayu WHERE id_kayu = ?",
                            (pilihan_id,),
                        )
                except sqlite3.IntegrityError:
                    st.error(
                        "Data tidak dapat dihapus karena sudah "
                        "digunakan dalam transaksi."
                    )
                else:
                    set_flash("Data kayu berhasil dihapus.")
                    st.rerun()

    with tab_tambah:
        st.subheader("➕ Tambah Data Kayu")

        with st.form("form_tambah_data_kayu", clear_on_submit=True):
            nama = st.text_input("Nama Kayu", placeholder="Contoh: Kayu Jati")
            satuan = st.selectbox("Satuan", DAFTAR_SATUAN)
            harga = st.number_input("Harga", min_value=0, value=0, step=1000)
            stok = st.number_input("Stok Awal", min_value=0, value=0, step=1)
            tambah = st.form_submit_button(
                "➕ Tambahkan Kayu", use_container_width=True
            )

        if tambah:
            if not nama.strip():
                st.error("Nama kayu wajib diisi.")
            elif harga <= 0:
                st.error("Harga harus lebih dari 0.")
            else:
                with db() as conn:
                    conn.execute(
                        "INSERT INTO kayu (nama_kayu, satuan, harga, stok) "
                        "VALUES (?, ?, ?, ?)",
                        (nama.strip(), satuan, harga, stok),
                    )
                set_flash("Data kayu berhasil ditambahkan.")
                st.rerun()


# =========================================================
# STOK
# =========================================================

def halaman_stok():
    st.title("📦 Stok Kayu")

    df = query_df("""
        SELECT id_kayu AS 'ID', nama_kayu AS 'Nama Kayu',
               satuan AS 'Satuan', stok AS 'Stok', harga AS 'Harga'
        FROM kayu
        ORDER BY stok ASC
    """)

    if df.empty:
        st.info("Belum ada data stok.")
        return

    tabel = df.copy()
    tabel["Status"] = tabel["Stok"].apply(status_stok)
    tabel["Harga"] = tabel["Harga"].apply(rupiah)
    st.dataframe(tabel, use_container_width=True, hide_index=True)

    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 Sangat Rendah", int((df["Stok"] <= STOK_SANGAT_RENDAH).sum()))
    c2.metric(
        "🟠 Rendah",
        int(
            (
                (df["Stok"] > STOK_SANGAT_RENDAH)
                & (df["Stok"] <= STOK_RENDAH)
            ).sum()
        ),
    )
    c3.metric("🟢 Aman", int((df["Stok"] > STOK_RENDAH).sum()))


# =========================================================
# PELANGGAN
# =========================================================

def halaman_pelanggan():
    st.title("👥 Data Pelanggan")

    tab_data, tab_tambah = st.tabs(
        ["📋 Data Pelanggan", "➕ Tambah Pelanggan"]
    )

    with tab_data:
        df = query_df("""
            SELECT id_pelanggan AS 'ID',
                   nama_pelanggan AS 'Nama Pelanggan',
                   no_telepon AS 'No. Telepon',
                   alamat AS 'Alamat'
            FROM pelanggan
            ORDER BY id_pelanggan DESC
        """)

        if df.empty:
            st.info("Belum ada data pelanggan.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("✏️ Edit Pelanggan")

            nama_map = dict(zip(df["ID"].tolist(), df["Nama Pelanggan"]))

            pilihan_id = int(
                st.selectbox(
                    "Pilih pelanggan",
                    df["ID"].tolist(),
                    format_func=lambda x: f"ID {x} - {nama_map[x]}",
                    key="select_edit_pelanggan",
                )
            )

            with db() as conn:
                data = conn.execute(
                    "SELECT * FROM pelanggan WHERE id_pelanggan = ?",
                    (pilihan_id,),
                ).fetchone()
                jumlah_transaksi = conn.execute(
                    "SELECT COUNT(*) AS n FROM penjualan "
                    "WHERE id_pelanggan = ?",
                    (pilihan_id,),
                ).fetchone()["n"]

            with st.form(f"form_edit_pelanggan_{pilihan_id}"):
                nama = st.text_input(
                    "Nama Pelanggan", value=data["nama_pelanggan"]
                )
                telepon = st.text_input(
                    "No. Telepon", value=data["no_telepon"] or ""
                )
                alamat = st.text_area("Alamat", value=data["alamat"] or "")
                simpan = st.form_submit_button(
                    "💾 Simpan Perubahan", use_container_width=True
                )

            if simpan:
                if not nama.strip():
                    st.error("Nama pelanggan wajib diisi.")
                else:
                    with db() as conn:
                        conn.execute(
                            "UPDATE pelanggan SET nama_pelanggan = ?, "
                            "no_telepon = ?, alamat = ? "
                            "WHERE id_pelanggan = ?",
                            (
                                nama.strip(),
                                telepon.strip(),
                                alamat.strip(),
                                pilihan_id,
                            ),
                        )
                    set_flash("Data pelanggan berhasil diperbarui.")
                    st.rerun()

            st.divider()
            st.subheader("🗑️ Hapus Pelanggan")

            if jumlah_transaksi > 0:
                st.warning(
                    f"Pelanggan ini memiliki {jumlah_transaksi} transaksi. "
                    "Jika dihapus, transaksi tetap ada tetapi nama "
                    "pelanggannya tampil sebagai '-'."
                )

            yakin = st.checkbox(
                "Saya yakin ingin menghapus pelanggan ini",
                key=f"konfirmasi_hapus_pelanggan_{pilihan_id}",
            )

            if st.button(
                "🗑️ Hapus Pelanggan",
                use_container_width=True,
                disabled=not yakin,
                key="button_hapus_pelanggan",
            ):
                with db() as conn:
                    conn.execute(
                        "DELETE FROM pelanggan WHERE id_pelanggan = ?",
                        (pilihan_id,),
                    )
                set_flash("Pelanggan berhasil dihapus.")
                st.rerun()

    with tab_tambah:
        with st.form("form_tambah_pelanggan", clear_on_submit=True):
            nama = st.text_input("Nama Pelanggan")
            telepon = st.text_input("No. Telepon")
            alamat = st.text_area("Alamat")
            tambah = st.form_submit_button(
                "➕ Tambahkan Pelanggan", use_container_width=True
            )

        if tambah:
            if not nama.strip():
                st.error("Nama pelanggan wajib diisi.")
            else:
                with db() as conn:
                    conn.execute(
                        "INSERT INTO pelanggan "
                        "(nama_pelanggan, no_telepon, alamat) "
                        "VALUES (?, ?, ?)",
                        (nama.strip(), telepon.strip(), alamat.strip()),
                    )
                set_flash("Pelanggan berhasil ditambahkan.")
                st.rerun()


# =========================================================
# PENJUALAN
# =========================================================

def simpan_transaksi(id_pelanggan, total):
    """Simpan transaksi + kurangi stok secara atomik. Return ID transaksi."""
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")

        # Cek stok terbaru dari database
        for item in st.session_state.cart_items:
            row = conn.execute(
                "SELECT stok FROM kayu WHERE id_kayu = ?",
                (item["id_kayu"],),
            ).fetchone()

            if row is None:
                raise ValueError(
                    f"Kayu {item['nama_kayu']} tidak ditemukan."
                )
            if int(row["stok"]) < int(item["jumlah"]):
                raise ValueError(
                    f"Stok {item['nama_kayu']} tidak mencukupi."
                )

        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.execute(
            "INSERT INTO penjualan (tanggal, id_pelanggan, id_user, total) "
            "VALUES (?, ?, ?, ?)",
            (
                tanggal,
                id_pelanggan,
                st.session_state.current_user_id,
                total,
            ),
        )
        id_transaksi = cursor.lastrowid

        for item in st.session_state.cart_items:
            conn.execute(
                "INSERT INTO detail_penjualan "
                "(id_penjualan, id_kayu, jumlah, harga, subtotal) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    id_transaksi,
                    item["id_kayu"],
                    item["jumlah"],
                    item["harga"],
                    item["subtotal"],
                ),
            )
            conn.execute(
                "UPDATE kayu SET stok = stok - ? WHERE id_kayu = ?",
                (item["jumlah"], item["id_kayu"]),
            )

    return id_transaksi


def halaman_penjualan():
    st.title("🛒 Transaksi Penjualan")

    pelanggan_df = query_df(
        "SELECT id_pelanggan, nama_pelanggan FROM pelanggan "
        "ORDER BY nama_pelanggan"
    )
    kayu_df = query_df(
        "SELECT id_kayu, nama_kayu, satuan, harga, stok FROM kayu "
        "ORDER BY nama_kayu"
    )

    if pelanggan_df.empty:
        st.warning("Belum ada pelanggan. Tambahkan pelanggan terlebih dahulu.")
        return

    if kayu_df.empty:
        st.warning("Belum ada data kayu.")
        return

    # ---------------- 1. Pelanggan ----------------
    st.subheader("1. Data Pelanggan")

    pelanggan_dict = dict(
        zip(
            pelanggan_df["id_pelanggan"].tolist(),
            pelanggan_df["nama_pelanggan"],
        )
    )

    id_pelanggan = int(
        st.selectbox(
            "Pilih Pelanggan",
            list(pelanggan_dict.keys()),
            format_func=lambda x: pelanggan_dict[x],
            key="select_pelanggan_transaksi",
        )
    )

    st.divider()

    # ---------------- 2. Tambah barang ----------------
    st.subheader("2. Tambahkan Barang")

    kayu_label = {
        int(r.id_kayu): f"{r.nama_kayu} | Stok: {r.stok}"
        for r in kayu_df.itertuples()
    }

    col1, col2, col3 = st.columns([3, 2, 2])

    with col1:
        id_kayu = int(
            st.selectbox(
                "Pilih Kayu",
                list(kayu_label.keys()),
                format_func=lambda x: kayu_label[x],
                key="select_kayu_transaksi",
            )
        )

    data_kayu = kayu_df[kayu_df["id_kayu"] == id_kayu].iloc[0]
    harga_kayu = float(data_kayu["harga"])
    stok_tersedia = int(data_kayu["stok"])

    with col2:
        st.text_input(
            "Harga",
            value=rupiah(harga_kayu),
            disabled=True,
            key=f"display_harga_{id_kayu}",
        )

    with col3:
        if stok_tersedia > 0:
            # key memuat id_kayu agar tidak error saat max_value berubah
            jumlah = st.number_input(
                "Jumlah",
                min_value=1,
                max_value=stok_tersedia,
                value=1,
                step=1,
                key=f"jumlah_transaksi_{id_kayu}",
            )
        else:
            st.warning("Stok habis.")
            jumlah = 0

    st.info(f"Subtotal: **{rupiah(harga_kayu * int(jumlah))}**")

    if st.button(
        "➕ Masukkan ke Keranjang",
        use_container_width=True,
        key="button_tambah_keranjang",
    ):
        if stok_tersedia <= 0 or jumlah <= 0:
            st.error("Stok kayu habis.")
        else:
            jumlah = int(jumlah)
            item = next(
                (
                    i for i in st.session_state.cart_items
                    if i["id_kayu"] == id_kayu
                ),
                None,
            )

            if item is None:
                st.session_state.cart_items.append({
                    "id_kayu": id_kayu,
                    "nama_kayu": data_kayu["nama_kayu"],
                    "satuan": data_kayu["satuan"],
                    "harga": harga_kayu,
                    "jumlah": jumlah,
                    "subtotal": harga_kayu * jumlah,
                })
                set_flash("Barang berhasil dimasukkan ke keranjang.")
            else:
                jumlah_baru = item["jumlah"] + jumlah
                if jumlah_baru > stok_tersedia:
                    set_flash(
                        "Jumlah di keranjang melebihi stok tersedia.",
                        "error",
                    )
                else:
                    item["jumlah"] = jumlah_baru
                    item["subtotal"] = jumlah_baru * item["harga"]
                    set_flash("Jumlah barang diperbarui.")

            st.rerun()

    st.divider()

    # ---------------- 3. Keranjang ----------------
    st.subheader("3. Keranjang Penjualan")

    cart = st.session_state.cart_items

    if not cart:
        st.info("Keranjang masih kosong.")
        return

    st.dataframe(
        pd.DataFrame([
            {
                "No": no,
                "Kayu": item["nama_kayu"],
                "Satuan": item["satuan"],
                "Harga": rupiah(item["harga"]),
                "Jumlah": item["jumlah"],
                "Subtotal": rupiah(item["subtotal"]),
            }
            for no, item in enumerate(cart, start=1)
        ]),
        use_container_width=True,
        hide_index=True,
    )

    total = sum(item["subtotal"] for item in cart)
    st.markdown(f"## 💰 Total: {rupiah(total)}")

    pilihan_hapus = st.selectbox(
        "Pilih barang untuk dihapus",
        range(len(cart)),
        format_func=lambda x: cart[x]["nama_kayu"],
        key="select_hapus_keranjang",
    )

    if st.button(
        "🗑️ Hapus Barang",
        use_container_width=True,
        key="button_hapus_keranjang",
    ):
        cart.pop(pilihan_hapus)
        set_flash("Barang dihapus dari keranjang.")
        st.rerun()

    st.divider()

    # ---------------- 4. Simpan ----------------
    st.subheader("4. Simpan Transaksi")

    if st.button(
        "💾 SIMPAN TRANSAKSI",
        type="primary",
        use_container_width=True,
        key="button_simpan_transaksi",
    ):
        try:
            id_transaksi = simpan_transaksi(id_pelanggan, total)
        except ValueError as error:
            st.error(f"Transaksi gagal: {error}")
        except Exception as error:
            st.error(f"Transaksi gagal: {error}")
        else:
            st.session_state.cart_items = []
            set_flash(
                f"Transaksi berhasil disimpan. ID Transaksi: {id_transaksi}"
            )
            st.session_state.pending_page = "Riwayat Transaksi"
            st.rerun()


# =========================================================
# RIWAYAT TRANSAKSI
# =========================================================

def halaman_riwayat():
    st.title("📜 Riwayat Transaksi")

    df = query_df("""
        SELECT p.id_penjualan AS 'ID Transaksi',
               p.tanggal AS 'Tanggal',
               COALESCE(pl.nama_pelanggan, '-') AS 'Pelanggan',
               COALESCE(u.nama, '-') AS 'Admin',
               p.total AS 'Total'
        FROM penjualan p
        LEFT JOIN pelanggan pl ON p.id_pelanggan = pl.id_pelanggan
        LEFT JOIN users u ON p.id_user = u.id_user
        ORDER BY p.id_penjualan DESC
    """)

    if df.empty:
        st.info("Belum ada transaksi.")
        return

    tabel = df.copy()
    tabel["Total"] = tabel["Total"].apply(rupiah)
    st.dataframe(tabel, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🧾 Detail Transaksi")

    id_transaksi = int(
        st.selectbox(
            "Pilih ID Transaksi",
            df["ID Transaksi"].tolist(),
            key="select_detail_transaksi",
        )
    )

    tampilkan_detail_transaksi(id_transaksi)


def tampilkan_detail_transaksi(id_transaksi):
    with db() as conn:
        transaksi = conn.execute(
            """
            SELECT p.*,
                   COALESCE(pl.nama_pelanggan, '-') AS nama_pelanggan,
                   COALESCE(pl.no_telepon, '-') AS no_telepon,
                   COALESCE(pl.alamat, '-') AS alamat,
                   COALESCE(u.nama, '-') AS nama_admin
            FROM penjualan p
            LEFT JOIN pelanggan pl ON p.id_pelanggan = pl.id_pelanggan
            LEFT JOIN users u ON p.id_user = u.id_user
            WHERE p.id_penjualan = ?
            """,
            (id_transaksi,),
        ).fetchone()

        detail = conn.execute(
            """
            SELECT d.*, k.nama_kayu, k.satuan
            FROM detail_penjualan d
            JOIN kayu k ON d.id_kayu = k.id_kayu
            WHERE d.id_penjualan = ?
            ORDER BY d.id_detail
            """,
            (id_transaksi,),
        ).fetchall()

    if transaksi is None:
        st.error("Transaksi tidak ditemukan.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**ID Transaksi:** {transaksi['id_penjualan']}")
        st.write(f"**Tanggal:** {transaksi['tanggal']}")

    with col2:
        st.write(f"**Pelanggan:** {transaksi['nama_pelanggan']}")
        st.write(f"**Admin:** {transaksi['nama_admin']}")

    st.dataframe(
        pd.DataFrame([
            {
                "Kayu": item["nama_kayu"],
                "Satuan": item["satuan"],
                "Jumlah": item["jumlah"],
                "Harga": rupiah(item["harga"]),
                "Subtotal": rupiah(item["subtotal"]),
            }
            for item in detail
        ]),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(f"## 💰 Total: {rupiah(transaksi['total'])}")

    garis = "=" * 40
    strip = "-" * 40

    nota = [
        garis,
        "          NOTA PENJUALAN KAYU",
        garis,
        f"ID Transaksi : {transaksi['id_penjualan']}",
        f"Tanggal      : {transaksi['tanggal']}",
        f"Pelanggan    : {transaksi['nama_pelanggan']}",
        f"No. Telepon  : {transaksi['no_telepon']}",
        strip,
    ]

    for item in detail:
        nota.append(
            f"{item['nama_kayu']} ({item['jumlah']} {item['satuan']})"
        )
        nota.append(
            f"{rupiah(item['harga'])} x {item['jumlah']} = "
            f"{rupiah(item['subtotal'])}"
        )

    nota += [
        strip,
        f"TOTAL: {rupiah(transaksi['total'])}",
        garis,
        f"Admin: {transaksi['nama_admin']}",
        garis,
    ]

    st.download_button(
        "⬇️ Download Nota",
        data="\n".join(nota) + "\n",
        file_name=f"nota_{id_transaksi}.txt",
        mime="text/plain",
        use_container_width=True,
        key=f"button_download_nota_{id_transaksi}",
    )


# =========================================================
# LAPORAN
# =========================================================

def halaman_laporan():
    st.title("📑 Laporan")

    tab_penjualan, tab_stok = st.tabs(
        ["💰 Laporan Penjualan", "📦 Laporan Stok"]
    )

    # ---------------- Laporan penjualan ----------------
    with tab_penjualan:
        st.subheader("💰 Laporan Penjualan")

        df = query_df("""
            SELECT p.id_penjualan AS 'ID Transaksi',
                   p.tanggal AS 'Tanggal',
                   COALESCE(pl.nama_pelanggan, '-') AS 'Pelanggan',
                   p.total AS 'Total'
            FROM penjualan p
            LEFT JOIN pelanggan pl ON p.id_pelanggan = pl.id_pelanggan
            ORDER BY p.id_penjualan DESC
        """)

        if df.empty:
            st.info("Belum ada data penjualan.")
        else:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])

            # Tanpa key: default ikut berubah saat ada transaksi baru
            tanggal_awal = st.date_input(
                "Tanggal Awal", value=df["Tanggal"].min().date()
            )
            tanggal_akhir = st.date_input(
                "Tanggal Akhir", value=df["Tanggal"].max().date()
            )

            if tanggal_awal > tanggal_akhir:
                st.error(
                    "Tanggal awal tidak boleh lebih besar dari "
                    "tanggal akhir."
                )
            else:
                hasil = df[
                    (df["Tanggal"].dt.date >= tanggal_awal)
                    & (df["Tanggal"].dt.date <= tanggal_akhir)
                ].copy()

                hasil["Tanggal"] = hasil["Tanggal"].dt.strftime(
                    "%d-%m-%Y %H:%M"
                )

                c1, c2 = st.columns(2)
                c1.metric("Jumlah Transaksi", len(hasil))
                c2.metric("Total Penjualan", rupiah(hasil["Total"].sum()))

                tampil = hasil.copy()
                tampil["Total"] = tampil["Total"].apply(rupiah)
                st.dataframe(
                    tampil, use_container_width=True, hide_index=True
                )

                # CSV memakai Total numerik agar bisa dihitung di Excel
                st.download_button(
                    "⬇️ Download Laporan Penjualan",
                    data=hasil.to_csv(index=False).encode("utf-8"),
                    file_name="laporan_penjualan.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="button_download_laporan_penjualan",
                )

    # ---------------- Laporan stok ----------------
    with tab_stok:
        st.subheader("📦 Laporan Stok Kayu")

        df = query_df("""
            SELECT id_kayu AS 'ID', nama_kayu AS 'Nama Kayu',
                   satuan AS 'Satuan', stok AS 'Stok', harga AS 'Harga'
            FROM kayu
            ORDER BY stok ASC
        """)

        if df.empty:
            st.info("Belum ada data stok.")
        else:
            hasil = df.copy()
            hasil["Status"] = hasil["Stok"].apply(
                lambda n: status_stok(n, emoji=False)
            )

            tampil = hasil.copy()
            tampil["Harga"] = tampil["Harga"].apply(rupiah)
            st.dataframe(tampil, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇️ Download Laporan Stok",
                data=hasil.to_csv(index=False).encode("utf-8"),
                file_name="laporan_stok.csv",
                mime="text/csv",
                use_container_width=True,
                key="button_download_laporan_stok",
            )


# =========================================================
# MAIN PROGRAM
# =========================================================

init_db()

HALAMAN = {
    "Dashboard": halaman_dashboard,
    "Data Kayu": halaman_data_kayu,
    "Stok Kayu": halaman_stok,
    "Pelanggan": halaman_pelanggan,
    "Penjualan": halaman_penjualan,
    "Riwayat Transaksi": halaman_riwayat,
    "Laporan": halaman_laporan,
}

if not st.session_state.is_logged_in:
    halaman_login()
else:
    menu_aktif = tampilkan_sidebar()
    show_flash()
    HALAMAN[menu_aktif]()
