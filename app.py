import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.figure_factory as ff

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

# ======================================================
# SETUP STREAMLIT
# ======================================================
st.set_page_config(
    page_title="Cafe Analytics AI Pro",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Cafe Analytics AI Pro")
st.write("Sistem Prediksi Kepadatan Pengunjung Café")

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.header("📝 Identitas Mahasiswa")
st.sidebar.write("Nama : Isi Nama")
st.sidebar.write("NIM : Isi NIM")
st.sidebar.write("Kampus : UNTAD")

# ======================================================
# API CUACA LIVE
# ======================================================
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=-0.8917"
    "&longitude=119.8707"
    "&current=temperature_2m,precipitation"
    "&timezone=Asia%2FMakassar"
)

try:
    data = requests.get(url).json()

    live_temp = data['current']['temperature_2m']
    live_rain = data['current']['precipitation']

except:
    live_temp = 28.0
    live_rain = 0.0

# ======================================================
# DATASET CAFE
# ======================================================
df = pd.DataFrame({

    'Nama_Cafe': [
        'Cafe Senja',
        'Kopi Nusantara',
        'Urban Brew',
        'Cafe Tepi Laut',
        'Coffee Story',
        'Palu Coffee Hub',
        'Ngopi Santai',
        'Cafe Malam',
        'Kedai Kopi Kita',
        'Morning Beans',
        'Sky Coffee',
        'Laut Biru Cafe'
    ],

    'Suhu': [
        30, 28, 27, 31, 29,
        26, 32, 25, 30, 27,
        29, 28
    ],

    'Hujan': [
        0, 5, 1, 0, 3,
        10, 0, 12, 2, 1,
        0, 4
    ],

    'Hari_Libur': [
        1, 0, 0, 1, 0,
        1, 0, 1, 0, 0,
        1, 0
    ],

    'Ada_Promo': [
        1, 0, 1, 1, 0,
        1, 0, 1, 0, 1,
        1, 0
    ],

    'Jam_Operasional': [
        2, 1, 2, 3, 2,
        2, 1, 3, 2, 1,
        3, 2
    ],

    'Rating_Cafe': [
        4.8, 4.1, 4.5, 4.9, 4.2,
        4.7, 4.0, 4.8, 4.3, 4.6,
        4.9, 4.4
    ],

    'Live_Music': [
        1, 0, 0, 1, 0,
        1, 0, 1, 0, 0,
        1, 0
    ],

    'WiFi_Cepat': [
        1, 1, 1, 1, 0,
        1, 0, 1, 1, 1,
        1, 1
    ],

    'Jumlah_Pengunjung': [
        120, 45, 90, 150, 70,
        110, 40, 130, 65, 85,
        170, 75
    ],

    'Pendapatan_Harian': [
        3500000,
        1200000,
        2500000,
        4200000,
        1800000,
        3000000,
        1000000,
        3900000,
        1700000,
        2200000,
        5000000,
        2000000
    ],

    'Target_Ramai': [
        1, 0, 1, 1, 0,
        1, 0, 1, 0, 1,
        1, 0
    ]
})

# ======================================================
# FEATURE & TARGET
# ======================================================
fitur = [
    'Suhu',
    'Hujan',
    'Hari_Libur',
    'Ada_Promo',
    'Jam_Operasional',
    'Rating_Cafe',
    'Live_Music',
    'WiFi_Cepat'
]

X = df[fitur]
y = df['Target_Ramai']

# ======================================================
# TRAINING MODEL
# ======================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# ======================================================
# AKURASI MODEL
# ======================================================
y_pred = model.predict(X_test)

akurasi = accuracy_score(y_test, y_pred)

st.subheader("🎯 Akurasi AI")
st.success(f"Akurasi Model : {akurasi * 100:.2f}%")

# ======================================================
# INPUT USER
# ======================================================
st.subheader("📍 Simulasi Kondisi Café")

c1, c2, c3 = st.columns(3)

with c1:

    st.info(f"""
    🌡️ Suhu : {live_temp}°C
    🌧️ Hujan : {live_rain} mm
    """)

    suhu = st.number_input(
        "Input Suhu",
        value=float(live_temp)
    )

    hujan = st.number_input(
        "Input Curah Hujan",
        value=float(live_rain)
    )

with c2:

    libur = st.selectbox(
        "Status Hari",
        [0, 1],
        format_func=lambda x:
        "Hari Kerja" if x == 0 else "Hari Libur"
    )

    promo = st.selectbox(
        "Promo",
        [0, 1],
        format_func=lambda x:
        "Tidak Ada Promo" if x == 0 else "Ada Promo"
    )

    jam = st.selectbox(
        "Jam Operasional",
        [1, 2, 3],
        format_func=lambda x:
        "Pagi" if x == 1
        else "Sore" if x == 2
        else "Malam"
    )

with c3:

    rating = st.slider(
        "Rating Café",
        1.0,
        5.0,
        4.5
    )

    music = st.selectbox(
        "Live Music",
        [0, 1],
        format_func=lambda x:
        "Tidak Ada" if x == 0 else "Ada"
    )

    wifi = st.selectbox(
        "WiFi Cepat",
        [0, 1],
        format_func=lambda x:
        "Tidak" if x == 0 else "Ya"
    )

# ======================================================
# PREDIKSI
# ======================================================
data_baru = pd.DataFrame([[
    suhu,
    hujan,
    libur,
    promo,
    jam,
    rating,
    music,
    wifi
]], columns=fitur)

prediksi = model.predict(data_baru)[0]

# ======================================================
# HASIL PREDIKSI
# ======================================================
st.subheader("🤖 Hasil Prediksi")

if prediksi == 1:

    st.error("""
    🔥 Café Diprediksi RAMAI

    ✅ Tambah stok
    ✅ Tambah pegawai
    ✅ Siapkan meja tambahan
    """)

else:

    st.success("""
    😌 Café Diprediksi SEPI

    ✅ Hemat operasional
    ✅ Fokus promosi
    """)

# ======================================================
# VISUALISASI
# ======================================================
st.markdown("---")
st.subheader("📊 Dashboard Analitik Café")

v1, v2 = st.columns(2)

# ======================================================
# FEATURE IMPORTANCE
# ======================================================
with v1:

    importance = pd.DataFrame({
        'Faktor': fitur,
        'Pengaruh': model.feature_importances_
    })

    importance = importance.sort_values(
        by='Pengaruh',
        ascending=False
    )

    fig1 = px.bar(
        importance,
        x='Faktor',
        y='Pengaruh',
        color='Pengaruh',
        title='🔥 Faktor Paling Berpengaruh'
    )

    st.plotly_chart(fig1, use_container_width=True)

# ======================================================
# CONFUSION MATRIX
# ======================================================
with v2:

    cm = confusion_matrix(y_test, y_pred)

    fig2 = ff.create_annotated_heatmap(
        z=cm,
        x=['Prediksi Sepi', 'Prediksi Ramai'],
        y=['Asli Sepi', 'Asli Ramai'],
        annotation_text=cm.astype(str),
        colorscale='Viridis'
    )

    fig2.update_layout(
        title='🧠 Confusion Matrix'
    )

    st.plotly_chart(fig2, use_container_width=True)

# ======================================================
# DATA HARIAN
# ======================================================
df_harian = pd.DataFrame({

    'Tanggal': pd.date_range(
        start='2025-01-01',
        periods=30,
        freq='D'
    ),

    'Pendapatan_Harian': [
        1200000, 1500000, 1700000, 2000000, 2100000,
        2500000, 3000000, 2800000, 2600000, 2200000,
        1900000, 2300000, 2400000, 2700000, 3200000,
        3500000, 3100000, 2900000, 2600000, 2400000,
        2100000, 1800000, 1700000, 2000000, 2300000,
        2500000, 2800000, 3000000, 3300000, 3600000
    ]
})

# ======================================================
# LAPORAN BULANAN
# ======================================================
df_harian['Bulan'] = df_harian['Tanggal'].dt.strftime('%B')

laporan_bulanan = df_harian.groupby(
    'Bulan',
    as_index=False
)['Pendapatan_Harian'].sum()

laporan_bulanan.columns = [
    'Bulan',
    'Total_Pendapatan'
]

# ======================================================
# GRAFIK BULANAN
# ======================================================
st.subheader("📅 Laporan Statistik Bulanan")

fig3 = px.bar(
    laporan_bulanan,
    x='Bulan',
    y='Total_Pendapatan',
    text_auto=True,
    title='💰 Total Pendapatan Per Bulan'
)

st.plotly_chart(fig3, use_container_width=True)

# ======================================================
# TABEL BULANAN
# ======================================================
st.dataframe(
    laporan_bulanan,
    use_container_width=True
)

# ======================================================
# DATA HISTORIS
# ======================================================
st.subheader("📋 Data Historis Café")

st.dataframe(
    df,
    use_container_width=True
)

# ======================================================
# CLASSIFICATION REPORT
# ======================================================
st.subheader("📄 Laporan Klasifikasi")

st.text(
    classification_report(y_test, y_pred)
)

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")
st.caption("made with ❤️ by temennya fuad")
