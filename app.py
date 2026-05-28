import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# =========================================================
# SETUP PAGE
# =========================================================
st.set_page_config(
    page_title="Smart Café Analytics AI",
    page_icon="☕",
    layout="wide"
)

# =========================================================
# HEADER
# =========================================================
st.title("☕ Smart Café Analytics AI Indonesia")
st.markdown("""
### Sistem Prediksi Kepadatan Pengunjung Café Berbasis Artificial Intelligence
Menggunakan Machine Learning Random Forest untuk analisis bisnis café pinggir jalan.
""")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("🧑‍🎓 Identitas Mahasiswa")

st.sidebar.write("Nama : Isi Nama")
st.sidebar.write("NIM : Isi NIM")
st.sidebar.write("Kampus : UNTAD")

st.sidebar.markdown("---")

st.sidebar.success("🔥 Smart Café AI Dashboard")

# =========================================================
# LIVE WEATHER API
# =========================================================
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=-0.8917"
    "&longitude=119.8707"
    "&current=temperature_2m,precipitation"
    "&timezone=Asia%2FMakassar"
)

try:

    response = requests.get(url)

    data = response.json()

    current_weather = data['current']

    live_temp = int(current_weather['temperature_2m'])

    live_rain = int(current_weather['precipitation'])

except:

    live_temp = 29
    live_rain = 0

# =========================================================
# MENU DATA
# =========================================================
menu_data = [

    ["Es Teh Manis", "Minuman", 5000],
    ["Teh Tarik", "Minuman", 12000],
    ["Kopi Hitam", "Minuman", 10000],
    ["Kopi Susu Gula Aren", "Minuman", 18000],
    ["Cappuccino", "Minuman", 20000],
    ["Latte", "Minuman", 22000],
    ["Matcha Latte", "Minuman", 23000],
    ["Chocolate Ice", "Minuman", 20000],
    ["Red Velvet", "Minuman", 22000],
    ["Air Mineral", "Minuman", 4000],

    ["Indomie Goreng Original", "Snack", 12000],
    ["Indomie Telur", "Snack", 15000],
    ["Roti Bakar Coklat", "Snack", 14000],
    ["Roti Bakar Keju", "Snack", 15000],
    ["Kentang Goreng", "Snack", 18000],
    ["Pisang Goreng", "Snack", 13000],
    ["Sosis Bakar", "Snack", 15000],
    ["Cireng Isi", "Snack", 12000],
    ["Tahu Crispy", "Snack", 10000],
    ["Mix Platter", "Snack", 25000],

    ["Nasi Goreng", "Makanan", 22000],
    ["Ayam Geprek", "Makanan", 20000],
    ["Rice Bowl Ayam", "Makanan", 25000],
    ["Mie Kuah Spesial", "Makanan", 18000],
    ["Chicken Katsu", "Makanan", 28000],
    ["Beef Teriyaki", "Makanan", 30000],
    ["Paket Hemat Kopi + Roti", "Makanan", 25000],
    ["Paket Nongkrong Berdua", "Makanan", 45000]

]

df_menu = pd.DataFrame(
    menu_data,
    columns=["Menu", "Kategori", "Harga"]
)

# =========================================================
# GENERATE DATASET
# =========================================================
np.random.seed(42)

n_data = 180

tanggal = pd.date_range(
    start='2025-01-01',
    periods=n_data,
    freq='D'
)

df = pd.DataFrame({

    'Tanggal': tanggal,

    'Suhu': np.random.randint(25, 35, n_data),

    'Hujan': np.random.randint(0, 11, n_data),

    'Hari_Libur': np.random.choice(
        [0, 1],
        size=n_data,
        p=[0.75, 0.25]
    ),

    'Promo': np.random.choice(
        [0, 1],
        size=n_data,
        p=[0.7, 0.3]
    ),

    'Shift': np.random.choice(
        [1, 2, 3],
        size=n_data,
        p=[0.3, 0.5, 0.2]
    )

})

# =========================================================
# BULAN
# =========================================================
nama_bulan = {

    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni"

}

df['Bulan'] = df['Tanggal'].dt.month.map(nama_bulan)

# =========================================================
# TARGET AI
# =========================================================
score = []

for i in range(n_data):

    nilai = 0

    if df.loc[i, 'Promo'] == 1:
        nilai += 30

    if df.loc[i, 'Hari_Libur'] == 1:
        nilai += 25

    if df.loc[i, 'Shift'] == 2:
        nilai += 20

    if df.loc[i, 'Hujan'] < 3:
        nilai += 15

    if 26 <= df.loc[i, 'Suhu'] <= 30:
        nilai += 10

    nilai += np.random.randint(-10, 15)

    score.append(nilai)

df['Score_Ramai'] = score

df['Ramai'] = (
    df['Score_Ramai'] >= 40
).astype(int)

# =========================================================
# JUMLAH PENGUNJUNG
# =========================================================
pengunjung = []

for i in range(n_data):

    total = 15

    if df.loc[i, 'Promo'] == 1:
        total += 10

    if df.loc[i, 'Hari_Libur'] == 1:
        total += 15

    if df.loc[i, 'Shift'] == 2:
        total += 20

    if df.loc[i, 'Shift'] == 3:
        total += 5

    if df.loc[i, 'Hujan'] > 7:
        total -= 8

    total += np.random.randint(-3, 7)

    total = max(total, 5)

    pengunjung.append(total)

df['Jumlah_Pengunjung'] = pengunjung

# =========================================================
# PENDAPATAN
# =========================================================
pendapatan = []

for i in range(n_data):

    rata_belanja = np.random.randint(15000, 25000)

    total = (
        df.loc[i, 'Jumlah_Pengunjung']
        * rata_belanja
    )

    pendapatan.append(total)

df['Pendapatan'] = pendapatan

# =========================================================
# MACHINE LEARNING
# =========================================================
features = [
    'Suhu',
    'Hujan',
    'Hari_Libur',
    'Promo',
    'Shift'
]

X = df[features]
y = df['Ramai']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

# =========================================================
# KPI DASHBOARD
# =========================================================
total_pengunjung = int(df['Jumlah_Pengunjung'].sum())

total_pendapatan = int(df['Pendapatan'].sum())

hari_ramai = int(df['Ramai'].sum())

rata_pengunjung = int(df['Jumlah_Pengunjung'].mean())

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👥 Total Pengunjung",
    f"{total_pengunjung}"
)

col2.metric(
    "💰 Total Pendapatan",
    f"Rp {total_pendapatan:,}".replace(",", ".")
)

col3.metric(
    "🔥 Hari Ramai",
    f"{hari_ramai} Hari"
)

col4.metric(
    "📈 Rata-rata Pengunjung",
    f"{rata_pengunjung} Orang"
)

# =========================================================
# AKURASI MODEL
# =========================================================
st.markdown("---")

st.subheader("🎯 Akurasi Artificial Intelligence")

st.success(
    f"Akurasi Model AI : {accuracy * 100:.2f}%"
)

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([

    "🤖 Prediksi AI",
    "📊 Dashboard",
    "☕ Daftar Menu",
    "📄 Laporan AI"

])

# =========================================================
# TAB 1
# =========================================================
with tab1:

    st.subheader("📍 Simulasi Prediksi Café")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.info(f"""
        🌡️ Suhu Live : {live_temp}°C

        🌧️ Curah Hujan : {live_rain} mm
        """)

        input_suhu = st.slider(
            "Suhu",
            20,
            40,
            live_temp
        )

        input_hujan = st.slider(
            "Curah Hujan",
            0,
            20,
            live_rain
        )

    with c2:

        input_libur = st.selectbox(
            "Status Hari",
            [0, 1],
            format_func=lambda x:
            "Hari Kerja"
            if x == 0
            else "Hari Libur"
        )

        input_promo = st.selectbox(
            "Program Promo",
            [0, 1],
            format_func=lambda x:
            "Tidak Ada Promo"
            if x == 0
            else "Ada Promo"
        )

    with c3:

        input_shift = st.selectbox(
            "Shift Operasional",
            [1, 2, 3]
        )

    analisis = st.button(
        "🔍 Analisis AI",
        use_container_width=True
    )

    if analisis:

        current_data = pd.DataFrame([[
            input_suhu,
            input_hujan,
            input_libur,
            input_promo,
            input_shift
        ]], columns=features)

        prediction = model.predict(current_data)[0]

        probability = model.predict_proba(current_data)[0]

        persen_ramai = probability[1] * 100

        estimasi_pengunjung = 20

        if input_promo == 1:
            estimasi_pengunjung += 10

        if input_libur == 1:
            estimasi_pengunjung += 15

        if input_shift == 2:
            estimasi_pengunjung += 20

        if input_hujan > 7:
            estimasi_pengunjung -= 10

        estimasi_pengunjung = max(
            estimasi_pengunjung,
            5
        )

        rata_belanja = 18000

        estimasi_pendapatan = (
            estimasi_pengunjung
            * rata_belanja
        )

        pendapatan_format = (
            f"Rp {estimasi_pendapatan:,}"
            .replace(",", ".")
        )

        st.markdown("---")

        if prediction == 1:

            st.error(f"""
            🔥 Café Diprediksi RAMAI

            📌 Keyakinan AI :
            {persen_ramai:.2f}%

            👥 Estimasi Pengunjung :
            {estimasi_pengunjung} Orang

            💰 Estimasi Pendapatan :
            {pendapatan_format}
            """)

            st.warning("""
            📢 Rekomendasi AI:
            - Tambah stok kopi
            - Siapkan kursi tambahan
            - Tambahkan pegawai shift malam
            """)

        else:

            st.success(f"""
            😌 Café Diprediksi Normal / Sepi

            📌 Keyakinan AI :
            {100 - persen_ramai:.2f}%

            👥 Estimasi Pengunjung :
            {estimasi_pengunjung} Orang

            💰 Estimasi Pendapatan :
            {pendapatan_format}
            """)

            st.info("""
            📢 Rekomendasi AI:
            - Gunakan promo diskon
            - Kurangi stok berlebih
            - Fokus penjualan online
            """)

# =========================================================
# TAB 2 DASHBOARD
# =========================================================
with tab2:

    st.subheader("📊 Dashboard Analytics")

    # ==========================================
    # FEATURE IMPORTANCE
    # ==========================================
    importance_df = pd.DataFrame({

        'Faktor': features,

        'Pengaruh': model.feature_importances_

    })

    fig_importance = px.bar(
        importance_df,
        x='Faktor',
        y='Pengaruh',
        color='Pengaruh',
        title='🔥 Faktor Paling Berpengaruh'
    )

    st.plotly_chart(
        fig_importance,
        use_container_width=True
    )

    # ==========================================
    # PENDAPATAN BULANAN
    # ==========================================
    pendapatan_bulanan = df.groupby(
        'Bulan',
        sort=False
    )['Pendapatan'].sum().reset_index()

    pendapatan_bulanan[
        'Pendapatan_Juta'
    ] = (
        pendapatan_bulanan['Pendapatan']
        / 1_000_000
    ).round(2)

    fig_income = px.line(
        pendapatan_bulanan,
        x='Bulan',
        y='Pendapatan_Juta',
        markers=True,
        title='💰 Trend Pendapatan Bulanan'
    )

    st.plotly_chart(
        fig_income,
        use_container_width=True
    )

    # ==========================================
    # PIE CHART SHIFT
    # ==========================================
    shift_data = df.groupby(
        'Shift'
    )['Jumlah_Pengunjung'].sum().reset_index()

    fig_pie = px.pie(
        shift_data,
        names='Shift',
        values='Jumlah_Pengunjung',
        title='🌙 Distribusi Pengunjung per Shift'
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# =========================================================
# TAB 3 MENU
# =========================================================
with tab3:

    st.subheader("☕ Daftar Menu Café")

    df_menu['Harga_Rp'] = (
        'Rp ' +
        df_menu['Harga']
        .astype(str)
        .apply(lambda x:
               f"{int(x):,}"
               .replace(",", "."))
    )

    st.dataframe(

        df_menu[[
            'Menu',
            'Kategori',
            'Harga_Rp'
        ]],

        use_container_width=True,
        hide_index=True
    )

    # ==========================================
    # MENU FAVORIT SIMULASI
    # ==========================================
    st.markdown("---")

    st.subheader("🔥 Simulasi Menu Terlaris")

    menu_laris = pd.DataFrame({

        'Menu': [
            'Kopi Susu Gula Aren',
            'Indomie Telur',
            'Latte',
            'Nasi Goreng',
            'Kentang Goreng'
        ],

        'Terjual': [
            120,
            90,
            80,
            70,
            65
        ]

    })

    fig_menu = px.bar(
        menu_laris,
        x='Menu',
        y='Terjual',
        color='Terjual',
        title='☕ Menu Paling Laris'
    )

    st.plotly_chart(
        fig_menu,
        use_container_width=True
    )

# =========================================================
# TAB 4 REPORT
# =========================================================
with tab4:

    st.subheader("📄 Laporan Klasifikasi AI")

    st.text(
        classification_report(
            y_test,
            y_pred
        )
    )

    # ==========================================
    # CONFUSION MATRIX
    # ==========================================
    cm = confusion_matrix(
        y_test,
        y_pred
    )

    fig_cm = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=['Sepi', 'Ramai'],
            y=['Sepi', 'Ramai']
        )
    )

    fig_cm.update_layout(
        title='🔥 Confusion Matrix'
    )

    st.plotly_chart(
        fig_cm,
        use_container_width=True
    )

    # ==========================================
    # DATA DETAIL
    # ==========================================
    st.markdown("---")

    st.subheader("📅 Detail Dataset")

    tampil_df = df.copy()

    tampil_df['Pendapatan'] = (
        tampil_df['Pendapatan']
        .apply(
            lambda x:
            f"Rp {x:,}".replace(",", ".")
        )
    )

    st.dataframe(
        tampil_df,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.caption("""
☕ Smart Café Analytics AI Indonesia
Made with ❤️ using Streamlit & Machine Learning
""")
