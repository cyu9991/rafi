import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import html

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Sistem Informasi Penjualan Kayu",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded",
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
            FOREIGN KEY (id_pelanggan) REFERENCES pelanggan(id_pelanggan) ON DELETE SET NULL,
            FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE SET NULL
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
            FOREIGN KEY (id_penjualan) REFERENCES penjualan(id_penjualan) ON DELETE CASCADE,
            FOREIGN KEY (id_kayu) REFERENCES kayu(id_kayu) ON DELETE RESTRICT
        )
    """)

    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username, password, nama) VALUES (?, ?, ?)",
            ("admin", "admin123", "Administrator"),
        )

    if cur.execute("SELECT COUNT(*) FROM kayu").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO kayu (nama_kayu, satuan, harga, stok) VALUES (?, ?, ?, ?)",
            [
                ("Kayu Jati", "Batang", 150000, 50),
                ("Kayu Meranti", "Batang", 100000, 40),
                ("Kayu Sengon", "Batang", 75000, 60),
                ("Kayu Mahoni", "Batang", 120000, 35),
                ("Kayu Ulin", "Batang", 200000, 25),
            ],
        )

    conn.commit()
    conn.close()


def qdf(sql, params=()):
    conn = get_db()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def execute(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    result = cur.lastrowid
    conn.close()
    return result


def rupiah(value):
    return "Rp {:,.0f}".format(float(value)).replace(",", ".")


def esc(value):
    return html.escape("" if value is None else str(value))

# =========================================================
# SESSION
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
# DESIGN SYSTEM - mengikuti HTML UI asli
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root{
 --primary:#250f03;
 --primary-container:#3d2314;
 --secondary:#904d00;
 --secondary-container:#fe932c;
 --surface:#f9f9ff;
 --surface-low:#f0f3ff;
 --surface-lowest:#ffffff;
 --surface-high:#dee8ff;
 --surface-container:#e7eeff;
 --on-surface:#111c2d;
 --on-variant:#50443f;
 --outline:#82746e;
 --outline-variant:#d4c3bc;
 --error:#ba1a1a;
}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif;}
.stApp{background:var(--surface);color:var(--on-surface);}
#MainMenu,footer{visibility:hidden;}
header[data-testid="stHeader"]{background:rgba(249,249,255,.92);}
section[data-testid="stSidebar"]{background:var(--primary-container);}
section[data-testid="stSidebar"] > div{background:var(--primary-container);}
section[data-testid="stSidebar"] *{color:#fff;}
section[data-testid="stSidebar"] .stButton > button{
 width:100%; text-align:left; justify-content:flex-start; border:0;
 background:transparent; color:#d4c3bc; border-radius:9px;
 padding:12px 16px; margin:2px 0; font-weight:600;
}
section[data-testid="stSidebar"] .stButton > button:hover{
 background:#250f02; color:#fff;
}
.sidebar-brand{padding:4px 8px 22px;border-bottom:1px solid rgba(212,195,188,.22);margin-bottom:18px;}
.sidebar-logo{display:flex;gap:10px;align-items:center;}
.sidebar-icon{width:40px;height:40px;border-radius:9px;background:#fe932c;color:#2d1608;display:flex;align-items:center;justify-content:center;font-size:22px;}
.sidebar-name{font-size:16px;font-weight:700;letter-spacing:.04em;}
.sidebar-sub{font-size:10px;color:#af8874!important;text-transform:uppercase;letter-spacing:.12em;}
.sidebar-version{font-size:10px;color:#af8874!important;margin-top:20px;padding:0 10px;}
.page-wrap{padding:8px 8px 35px;}
.topbar{display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.92);padding:10px 20px;border-radius:12px;box-shadow:0 1px 8px rgba(0,0,0,.04);margin-bottom:22px;}
.breadcrumb{font-size:12px;color:var(--on-variant);display:flex;align-items:center;gap:7px;}
.userbox{display:flex;align-items:center;gap:10px;}
.usertext{text-align:right;line-height:1.2;}.usertext b{font-size:12px;}.usertext span{font-size:10px;color:#82746e;}
.avatar{width:34px;height:34px;border-radius:50%;background:#250f03;color:#fff;display:flex;align-items:center;justify-content:center;font-size:17px;}
.page-head{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:22px;}
.page-head h1{font-size:28px;line-height:36px;margin:0;font-weight:700;letter-spacing:-.02em;}
.page-head p{font-size:13px;color:var(--on-variant);margin:4px 0 0;}
.card{background:#fff;border-radius:12px;padding:20px;box-shadow:0 1px 8px rgba(0,0,0,.04);}
.card-title{font-size:16px;font-weight:700;margin-bottom:4px;}.card-sub{font-size:12px;color:#82746e;}
.metric{background:#fff;border-radius:12px;padding:17px;min-height:110px;box-shadow:0 1px 8px rgba(0,0,0,.04);display:flex;justify-content:space-between;align-items:center;}
.metric-label{font-size:10px;color:#50443f;text-transform:uppercase;letter-spacing:.08em;font-weight:700;}.metric-value{font-size:27px;font-weight:700;margin-top:5px;}.metric-unit{font-size:11px;color:#82746e;margin-left:4px;}.metric-icon{width:46px;height:46px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:23px;}
.icon-orange{background:#fe932c;color:#2d1608}.icon-cream{background:#ffdbca;color:#2d1608}.icon-soft{background:#fff0e4;color:#904d00}.icon-brown{background:#ffdbc7;color:#3d2314}
.section-head{display:flex;justify-content:space-between;align-items:center;margin:24px 0 12px;}.section-head h2{font-size:17px;margin:0;font-weight:700;}.muted{color:#82746e;font-size:12px;}
.html-table{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 8px rgba(0,0,0,.04);font-size:12px;}.html-table th{background:#f0f3ff;color:#50443f;text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.06em;padding:12px 14px;border-bottom:1px solid #d4c3bc;}.html-table td{padding:13px 14px;border-bottom:1px solid #eee8e3;}.html-table tr:last-child td{border-bottom:0;}.html-table tr:hover td{background:#faf8f6;}
.badge{display:inline-block;border-radius:999px;padding:4px 9px;font-size:10px;font-weight:700;}.badge-green{background:#e8f5e9;color:#2e7d32}.badge-orange{background:#fff1df;color:#a65300}.badge-red{background:#ffebee;color:#ba1a1a}.badge-brown{background:#ffdbca;color:#5e402f}
.alert{padding:14px 16px;border-radius:10px;background:#eef6ff;color:#2485df;font-size:13px;}.notice{padding:14px 16px;border-radius:10px;background:#fff4e8;color:#8b4e00;font-size:13px;}
.chart{height:245px;display:flex;align-items:flex-end;gap:13px;padding:20px 10px 8px;border-bottom:1px solid #d4c3bc;}.bar-wrap{flex:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:6px;}.bar{width:min(42px,75%);background:#3d2314;border-radius:6px 6px 0 0;min-height:4px;}.bar.today{background:#fe932c;}.bar-label{font-size:10px;color:#82746e;}.bar-value{font-size:10px;color:#904d00;font-weight:700;}
.footer-note{background:#f0f3ff;padding:12px 16px;border-radius:0 0 12px 12px;font-size:11px;color:#50443f;display:flex;justify-content:space-between;}
.login-card{max-width:470px;margin:55px auto;background:#fff;border-radius:18px;padding:34px;box-shadow:0 12px 35px rgba(37,15,3,.10);border:1px solid #e7ddd6;}.login-logo{width:62px;height:62px;border-radius:16px;background:#fe932c;margin:0 auto 18px;display:flex;align-items:center;justify-content:center;font-size:33px;}.login-card h1{text-align:center;font-size:25px;margin:0;font-weight:700;}.login-card p{text-align:center;color:#82746e;font-size:12px;margin:6px 0 25px;}
.stTextInput input,.stNumberInput input,.stDateInput input,.stSelectbox div[data-baseweb="select"]>div,.stTextArea textarea{border-radius:8px!important;border-color:#d4c3bc!important;background:#fff!important;}
.stButton > button{border-radius:8px;font-weight:700;}
.primary-btn .stButton>button{background:#250f03;color:#fff;border-color:#250f03;}
.small-help{font-size:11px;color:#82746e;}
@media(max-width:900px){.page-head{flex-direction:column}.topbar{display:none}.metric{min-height:95px}}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGIN
# =========================================================
def login_page():
    st.markdown("""
    <div class="login-card">
      <div class="login-logo">🪵</div>
      <h1>Sistem Informasi Penjualan Kayu</h1>
      <p>Penjualan dan Pengelolaan Stok Kayu Berbasis Web</p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1])
    with center:
        with st.form("login_form"):
            st.markdown("### 🔐 Login Admin")
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            masuk = st.form_submit_button("Masuk", use_container_width=True)

            if masuk:
                if not username.strip() or not password:
                    st.error("Username dan password wajib diisi.")
                else:
                    conn = get_db()
                    user = conn.execute(
                        "SELECT * FROM users WHERE username=? AND password=?",
                        (username.strip(), password),
                    ).fetchone()
                    conn.close()
                    if user:
                        st.session_state.is_logged_in = True
                        st.session_state.current_user_id = user["id_user"]
                        st.session_state.current_user_name = user["nama"]
                        st.session_state.current_page = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Username atau password salah.")

        st.info("Login demo: **admin** / **admin123**")

# =========================================================
# SIDEBAR
# =========================================================
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
          <div class="sidebar-logo">
            <div class="sidebar-icon">🌲</div>
            <div><div class="sidebar-name">KAYU</div><div class="sidebar-sub">Sistem Informasi</div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        menus = [
            ("Dashboard", "▦"),
            ("Barang", "▤"),
            ("Pembelian", "🛍"),
            ("Penjualan", "▣"),
            ("Pelanggan & Pemasok", "♧"),
            ("Laporan", "▥"),
        ]
        for label, icon in menus:
            if st.button(f"{icon}   {label}", key="nav_" + label, use_container_width=True):
                st.session_state.current_page = label
                st.rerun()

        st.markdown("<div class='sidebar-version'>⚙ Pengaturan<br><br>v1.2.0 • Timber ERP</div>", unsafe_allow_html=True)
        st.divider()
        st.caption(f"👤 {st.session_state.current_user_name}")
        if st.button("Keluar", use_container_width=True):
            st.session_state.is_logged_in = False
            st.session_state.current_user_id = None
            st.session_state.current_user_name = None
            st.session_state.cart_items = []
            st.rerun()


def topbar():
    st.markdown(f"""
    <div class="topbar">
      <div class="breadcrumb">▣ <span>Gudang Utama Jati Mulya</span> › <b>Operasional Kayu</b></div>
      <div class="userbox"><div class="usertext"><b>{esc(st.session_state.current_user_name)}</b><br><span>Administrator</span></div><div class="avatar">♟</div></div>
    </div>
    """, unsafe_allow_html=True)


def page_head(title, desc):
    st.markdown(f"""
    <div class="page-head"><div><h1>{esc(title)}</h1><p>{esc(desc)}</p></div></div>
    """, unsafe_allow_html=True)

# =========================================================
# DASHBOARD
# =========================================================
def dashboard():
    page_head("Dashboard", f"Selamat datang, {st.session_state.current_user_name}. Berikut ringkasan data sistem penjualan dan stok kayu.")

    kayu = qdf("SELECT * FROM kayu")
    pelanggan = qdf("SELECT * FROM pelanggan")
    penjualan = qdf("SELECT * FROM penjualan")
    total_stok = int(kayu.stok.sum()) if not kayu.empty else 0
    total_transaksi = len(penjualan)
    total_nilai = float(penjualan.total.sum()) if not penjualan.empty else 0

    cols = st.columns(4)
    metrics = [
        ("Total Barang", len(kayu), "Jenis kayu", "🌲", "icon-cream"),
        ("Total Stok", total_stok, "Unit", "▤", "icon-cream"),
        ("Total Penjualan", total_transaksi, "Transaksi", "🛒", "icon-soft"),
        ("Nilai Penjualan", rupiah(total_nilai), "Total", "💰", "icon-brown"),
    ]
    for col, (label, value, unit, icon, iclass) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric"><div><div class="metric-label">{label}</div><div class="metric-value">{value} <span class="metric-unit">{unit}</span></div></div><div class="metric-icon {iclass}">{icon}</div></div>
            """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.7, 1])
    with c1:
        st.markdown("<div class='section-head'><div><h2>Grafik Penjualan</h2><span class='muted'>Aktivitas 7 Hari Terakhir</span></div></div>", unsafe_allow_html=True)
        rows = []
        today = date.today()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            n = int(qdf("SELECT COUNT(*) AS n FROM penjualan WHERE date(tanggal)=?", (d.isoformat(),)).iloc[0]["n"])
            rows.append((d, n))
        max_n = max([x[1] for x in rows] + [1])
        bars = "".join([f"<div class='bar-wrap'><div class='bar-value'>{n}</div><div class='bar {'today' if d==today else ''}' style='height:{max(4, int((n/max_n)*180))}px'></div><div class='bar-label'>{d.strftime('%d %b')}</div></div>" for d,n in rows])
        st.markdown(f"<div class='card'><div class='chart'>{bars}</div><div class='footer-note'><span>↗ Rata-rata {sum(x[1] for x in rows)/7:.1f} transaksi/hari</span><span>Data berdasarkan transaksi tersimpan</span></div></div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-head'><div><h2>Stok Terendah</h2><span class='muted'>Perlu diperhatikan</span></div></div>", unsafe_allow_html=True)
        low = kayu.sort_values("stok").head(6)
        if low.empty:
            st.markdown("<div class='alert'>Belum ada data stok.</div>", unsafe_allow_html=True)
        else:
            content = ""
            for _, r in low.iterrows():
                cls = "badge-red" if r.stok <= 5 else ("badge-orange" if r.stok <= 10 else "badge-green")
                status = "Sangat Rendah" if r.stok <= 5 else ("Rendah" if r.stok <= 10 else "Aman")
                content += f"<div style='display:flex;justify-content:space-between;align-items:center;padding:11px 0;border-bottom:1px solid #eee8e3'><span><b>{esc(r.nama_kayu)}</b><br><small class='muted'>{int(r.stok)} {esc(r.satuan)}</small></span><span class='badge {cls}'>{status}</span></div>"
            st.markdown(f"<div class='card'>{content}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-head'><div><h2>Transaksi Terbaru</h2><span class='muted'>5 transaksi terakhir</span></div></div>", unsafe_allow_html=True)
    recent = qdf("""
        SELECT p.id_penjualan, p.tanggal, COALESCE(pl.nama_pelanggan,'Umum') pelanggan, p.total
        FROM penjualan p LEFT JOIN pelanggan pl ON p.id_pelanggan=pl.id_pelanggan
        ORDER BY p.id_penjualan DESC LIMIT 5
    """)
    if recent.empty:
        st.markdown("<div class='alert'>Belum ada transaksi.</div>", unsafe_allow_html=True)
    else:
        body = "".join([f"<tr><td>#{int(r.id_penjualan)}</td><td>{esc(r.tanggal)}</td><td>{esc(r.pelanggan)}</td><td><b>{rupiah(r.total)}</b></td></tr>" for _,r in recent.iterrows()])
        st.markdown(f"<table class='html-table'><thead><tr><th>ID</th><th>Tanggal</th><th>Pelanggan</th><th>Total</th></tr></thead><tbody>{body}</tbody></table>", unsafe_allow_html=True)

# =========================================================
# BARANG
# =========================================================
def barang():
    page_head("Barang", "Kelola data barang kayu, harga, satuan, dan stok.")
    df = qdf("SELECT * FROM kayu ORDER BY id_kayu DESC")
    search = st.text_input("Cari barang", placeholder="Cari nama kayu...")
    if search:
        df = df[df.nama_kayu.str.contains(search, case=False, na=False)]

    st.markdown("<div class='section-head'><div><h2>Daftar Barang</h2><span class='muted'>Data barang terhubung langsung dengan database SQLite</span></div></div>", unsafe_allow_html=True)
    body = "".join([f"<tr><td>{int(r.id_kayu)}</td><td><b>{esc(r.nama_kayu)}</b></td><td>{esc(r.satuan)}</td><td>{rupiah(r.harga)}</td><td>{int(r.stok)}</td></tr>" for _,r in df.iterrows()])
    if body:
        st.markdown(f"<table class='html-table'><thead><tr><th>ID</th><th>Nama Barang</th><th>Satuan</th><th>Harga</th><th>Stok</th></tr></thead><tbody>{body}</tbody></table>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='alert'>Tidak ada data yang sesuai pencarian.</div>", unsafe_allow_html=True)

    with st.expander("+ Tambah Barang"):
        with st.form("add_barang"):
            c1,c2 = st.columns(2)
            with c1:
                nama = st.text_input("Nama Barang")
                satuan = st.selectbox("Satuan", ["Batang","Kubik","Papan","Balok","Lembar"])
            with c2:
                harga = st.number_input("Harga", min_value=0.0, step=1000.0)
                stok = st.number_input("Stok", min_value=0, step=1)
            submit = st.form_submit_button("Simpan Data", use_container_width=True)
            if submit:
                if not nama.strip():
                    st.error("Nama barang wajib diisi.")
                else:
                    execute("INSERT INTO kayu (nama_kayu,satuan,harga,stok) VALUES (?,?,?,?)", (nama.strip(),satuan,harga,stok))
                    st.success("Data barang berhasil ditambahkan.")
                    st.rerun()

    if not df.empty:
        with st.expander("Edit / Hapus Barang"):
            selected = st.selectbox("Pilih barang", df.id_kayu.tolist(), format_func=lambda x: df.loc[df.id_kayu==x,"nama_kayu"].iloc[0])
            r = df[df.id_kayu==selected].iloc[0]
            c1,c2=st.columns(2)
            with c1:
                nama2=st.text_input("Nama", value=r.nama_kayu)
                satuan2=st.selectbox("Satuan", ["Batang","Kubik","Papan","Balok","Lembar"], index=["Batang","Kubik","Papan","Balok","Lembar"].index(r.satuan) if r.satuan in ["Batang","Kubik","Papan","Balok","Lembar"] else 0)
            with c2:
                harga2=st.number_input("Harga", min_value=0.0, value=float(r.harga), step=1000.0)
                stok2=st.number_input("Stok", min_value=0, value=int(r.stok), step=1)
            a,b=st.columns(2)
            with a:
                if st.button("Simpan Perubahan", use_container_width=True):
                    execute("UPDATE kayu SET nama_kayu=?,satuan=?,harga=?,stok=? WHERE id_kayu=?", (nama2,satuan2,harga2,stok2,int(selected)))
                    st.success("Data diperbarui."); st.rerun()
            with b:
                if st.button("Hapus Barang", use_container_width=True):
                    try:
                        execute("DELETE FROM kayu WHERE id_kayu=?", (int(selected),))
                        st.success("Data dihapus."); st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Barang tidak dapat dihapus karena sudah digunakan dalam transaksi.")

# =========================================================
# PEMBELIAN PLACEHOLDER - schema user tidak memiliki tabel pembelian
# =========================================================
def pembelian():
    page_head("Pembelian", "Modul pembelian mengikuti navigasi UI, tetapi database yang diberikan belum memiliki tabel pembelian.")
    st.markdown("<div class='notice'><b>Belum terhubung ke database.</b><br>Database saat ini hanya menyediakan users, kayu, pelanggan, penjualan, dan detail_penjualan. Tabel pembelian/pemasok belum tersedia.</div>", unsafe_allow_html=True)

# =========================================================
# PENJUALAN
# =========================================================
def penjualan():
    page_head("Penjualan", "Buat transaksi baru dengan tampilan dan alur yang mengikuti UI HTML.")
    pelanggan = qdf("SELECT * FROM pelanggan ORDER BY nama_pelanggan")
    kayu = qdf("SELECT * FROM kayu WHERE stok>0 ORDER BY nama_kayu")
    if kayu.empty:
        st.markdown("<div class='alert'>Tidak ada stok kayu yang tersedia.</div>", unsafe_allow_html=True)
        return

    c1,c2 = st.columns([1.2,1])
    with c1:
        if pelanggan.empty:
            pelanggan_id=None
            st.warning("Belum ada pelanggan. Transaksi akan dicatat sebagai Umum.")
        else:
            pelanggan_id=st.selectbox("Pelanggan", [None]+pelanggan.id_pelanggan.tolist(), format_func=lambda x: "Umum" if x is None else pelanggan.loc[pelanggan.id_pelanggan==x,"nama_pelanggan"].iloc[0])
    with c2:
        tanggal=st.date_input("Tanggal Transaksi", value=date.today())

    st.markdown("<div class='section-head'><div><h2>Tambah Item</h2><span class='muted'>Pilih barang, jumlah, lalu masukkan ke keranjang</span></div></div>", unsafe_allow_html=True)
    a,b,c=st.columns([2,1,1])
    with a:
        kayu_id=st.selectbox("Barang", kayu.id_kayu.tolist(), format_func=lambda x: f"{kayu.loc[kayu.id_kayu==x,'nama_kayu'].iloc[0]} • Stok {int(kayu.loc[kayu.id_kayu==x,'stok'].iloc[0])}")
    r=kayu[kayu.id_kayu==kayu_id].iloc[0]
    with b:
        st.text_input("Harga", rupiah(r.harga), disabled=True)
    with c:
        jumlah=st.number_input("Jumlah", min_value=1, max_value=max(1,int(r.stok)), value=1, step=1)
    st.markdown(f"<div class='notice'>Subtotal: <b>{rupiah(float(r.harga)*int(jumlah))}</b></div>", unsafe_allow_html=True)
    if st.button("Masukkan ke Keranjang", use_container_width=True):
        existing=next((x for x in st.session_state.cart_items if x["id_kayu"]==int(kayu_id)),None)
        if existing:
            new_qty=existing["jumlah"]+int(jumlah)
            if new_qty>int(r.stok): st.error("Jumlah keranjang melebihi stok.")
            else:
                existing["jumlah"]=new_qty; existing["subtotal"]=new_qty*float(r.harga); st.rerun()
        else:
            st.session_state.cart_items.append({"id_kayu":int(kayu_id),"nama_kayu":r.nama_kayu,"satuan":r.satuan,"harga":float(r.harga),"jumlah":int(jumlah),"subtotal":float(r.harga)*int(jumlah)})
            st.rerun()

    st.markdown("<div class='section-head'><div><h2>Keranjang Penjualan</h2></div></div>", unsafe_allow_html=True)
    if not st.session_state.cart_items:
        st.markdown("<div class='alert'>Keranjang masih kosong.</div>", unsafe_allow_html=True)
        return
    body="".join([f"<tr><td>{i+1}</td><td><b>{esc(x['nama_kayu'])}</b></td><td>{x['jumlah']} {esc(x['satuan'])}</td><td>{rupiah(x['harga'])}</td><td><b>{rupiah(x['subtotal'])}</b></td></tr>" for i,x in enumerate(st.session_state.cart_items)])
    st.markdown(f"<table class='html-table'><thead><tr><th>No</th><th>Barang</th><th>Jumlah</th><th>Harga</th><th>Subtotal</th></tr></thead><tbody>{body}</tbody></table>", unsafe_allow_html=True)
    total=sum(x["subtotal"] for x in st.session_state.cart_items)
    st.markdown(f"<div class='card' style='margin-top:12px;text-align:right'><span class='muted'>Total Pembayaran</span><div style='font-size:27px;font-weight:700'>{rupiah(total)}</div></div>", unsafe_allow_html=True)
    remove=st.selectbox("Pilih item untuk dihapus", range(len(st.session_state.cart_items)), format_func=lambda i: st.session_state.cart_items[i]["nama_kayu"])
    a,b=st.columns(2)
    with a:
        if st.button("Hapus dari Keranjang", use_container_width=True):
            st.session_state.cart_items.pop(remove); st.rerun()
    with b:
        if st.button("Simpan Transaksi", use_container_width=True):
            conn=get_db()
            try:
                for x in st.session_state.cart_items:
                    latest=conn.execute("SELECT stok FROM kayu WHERE id_kayu=?",(x["id_kayu"],)).fetchone()
                    if not latest or latest["stok"]<x["jumlah"]: raise Exception(f"Stok {x['nama_kayu']} tidak mencukupi.")
                cur=conn.cursor()
                cur.execute("INSERT INTO penjualan (tanggal,id_pelanggan,id_user,total) VALUES (?,?,?,?)",(datetime.combine(tanggal,datetime.min.time()).strftime("%Y-%m-%d %H:%M:%S"),pelanggan_id,st.session_state.current_user_id,total))
                pid=cur.lastrowid
                for x in st.session_state.cart_items:
                    cur.execute("INSERT INTO detail_penjualan (id_penjualan,id_kayu,jumlah,harga,subtotal) VALUES (?,?,?,?,?)",(pid,x["id_kayu"],x["jumlah"],x["harga"],x["subtotal"]))
                    cur.execute("UPDATE kayu SET stok=stok-? WHERE id_kayu=?",(x["jumlah"],x["id_kayu"]))
                conn.commit(); st.session_state.cart_items=[]; st.session_state.current_page="Penjualan"; st.success(f"Transaksi #{pid} berhasil disimpan."); st.rerun()
            except Exception as e:
                conn.rollback(); st.error(str(e))
            finally:
                conn.close()

# =========================================================
# PELANGGAN & PEMASOK
# =========================================================
def pelanggan_pemasok():
    page_head("Pelanggan & Pemasok", "Kelola data rekanan sesuai struktur database yang tersedia.")
    tab1,tab2=st.tabs(["Pelanggan","Pemasok"])
    with tab1:
        df=qdf("SELECT * FROM pelanggan ORDER BY id_pelanggan DESC")
        search=st.text_input("Cari pelanggan", key="search_pelanggan")
        if search: df=df[df.nama_pelanggan.str.contains(search,case=False,na=False)]
        body="".join([f"<tr><td>{int(r.id_pelanggan)}</td><td><b>{esc(r.nama_pelanggan)}</b></td><td>{esc(r.no_telepon)}</td><td>{esc(r.alamat)}</td></tr>" for _,r in df.iterrows()])
        if body: st.markdown(f"<table class='html-table'><thead><tr><th>ID</th><th>Nama</th><th>Kontak</th><th>Alamat</th></tr></thead><tbody>{body}</tbody></table>",unsafe_allow_html=True)
        else: st.markdown("<div class='alert'>Belum ada data pelanggan.</div>",unsafe_allow_html=True)
        with st.expander("+ Tambah Pelanggan"):
            with st.form("add_pelanggan"):
                nama=st.text_input("Nama Pelanggan"); tel=st.text_input("No. Telepon"); alamat=st.text_area("Alamat")
                if st.form_submit_button("Simpan Data",use_container_width=True):
                    if not nama.strip(): st.error("Nama pelanggan wajib diisi.")
                    else: execute("INSERT INTO pelanggan (nama_pelanggan,no_telepon,alamat) VALUES (?,?,?)",(nama,tel,alamat)); st.success("Pelanggan ditambahkan."); st.rerun()
    with tab2:
        st.markdown("<div class='notice'><b>Pemasok belum tersedia di database.</b><br>HTML asli memiliki tab pemasok, tetapi schema SQLite yang diberikan belum mempunyai tabel pemasok.</div>",unsafe_allow_html=True)

# =========================================================
# LAPORAN
# =========================================================
def laporan():
    page_head("Laporan", "Laporan penjualan dan stok kayu.")
    tab1,tab2=st.tabs(["Laporan Penjualan","Laporan Stok"])
    with tab1:
        c1,c2=st.columns(2)
        with c1: awal=st.date_input("Tanggal Awal", value=date.today()-timedelta(days=30))
        with c2: akhir=st.date_input("Tanggal Akhir", value=date.today())
        df=qdf("""
            SELECT p.id_penjualan,p.tanggal,COALESCE(pl.nama_pelanggan,'Umum') pelanggan,p.total
            FROM penjualan p LEFT JOIN pelanggan pl ON p.id_pelanggan=pl.id_pelanggan
            WHERE date(p.tanggal) BETWEEN ? AND ? ORDER BY p.id_penjualan DESC
        """,(awal.isoformat(),akhir.isoformat()))
        total=float(df.total.sum()) if not df.empty else 0
        a,b=st.columns(2); a.metric("Jumlah Transaksi",len(df)); b.metric("Total Penjualan",rupiah(total))
        if not df.empty:
            body="".join([f"<tr><td>#{int(r.id_penjualan)}</td><td>{esc(r.tanggal)}</td><td>{esc(r.pelanggan)}</td><td>{rupiah(r.total)}</td></tr>" for _,r in df.iterrows()])
            st.markdown(f"<table class='html-table'><thead><tr><th>ID</th><th>Tanggal</th><th>Pelanggan</th><th>Total</th></tr></thead><tbody>{body}</tbody></table>",unsafe_allow_html=True)
            st.download_button("Download CSV",df.to_csv(index=False).encode("utf-8"),"laporan_penjualan.csv","text/csv",use_container_width=True)
        else: st.markdown("<div class='alert'>Tidak ada transaksi pada periode tersebut.</div>",unsafe_allow_html=True)
    with tab2:
        df=qdf("SELECT * FROM kayu ORDER BY nama_kayu")
        if not df.empty:
            body=""
            for _,r in df.iterrows():
                status="Sangat Rendah" if r.stok<=5 else ("Rendah" if r.stok<=10 else "Aman")
                cls="badge-red" if r.stok<=5 else ("badge-orange" if r.stok<=10 else "badge-green")
                body+=f"<tr><td>{int(r.id_kayu)}</td><td><b>{esc(r.nama_kayu)}</b></td><td>{int(r.stok)} {esc(r.satuan)}</td><td>{rupiah(r.harga)}</td><td><span class='badge {cls}'>{status}</span></td></tr>"
            st.markdown(f"<table class='html-table'><thead><tr><th>ID</th><th>Kayu</th><th>Stok</th><th>Harga</th><th>Status</th></tr></thead><tbody>{body}</tbody></table>",unsafe_allow_html=True)
            st.download_button("Download Stok CSV",df.to_csv(index=False).encode("utf-8"),"laporan_stok.csv","text/csv",use_container_width=True)

# =========================================================
# MAIN
# =========================================================
init_db()

if not st.session_state.is_logged_in:
    login_page()
else:
    sidebar()
    topbar()
    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    page=st.session_state.current_page
    if page=="Dashboard": dashboard()
    elif page=="Barang": barang()
    elif page=="Pembelian": pembelian()
    elif page=="Penjualan": penjualan()
    elif page=="Pelanggan & Pemasok": pelanggan_pemasok()
    elif page=="Laporan": laporan()
    else: dashboard()
    st.markdown("</div>", unsafe_allow_html=True)
