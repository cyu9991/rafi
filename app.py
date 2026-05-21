import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

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
st.write("Sistem Analisis & Prediksi Kepadatan Pengunjung Café Menggunakan Random Forest")

# ======================================================
# SIDEBAR IDENTITAS
# ======================================================
st.sidebar.header("📝 Identitas Mahasiswa")
st.sidebar.write("Nama : Isi Nama")
st.sidebar.write("NIM  : Isi NIM")
st.sidebar.write("Kampus : UNTAD")

# ======================================================
# API CUACA LIVE PALU
# ======================================================
url = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=-0.8917"
    "&longitude=119.8707"
    "&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
    "&timezone=Asia%2FMakassar"
)

try:
    response = requests.get(url)
    data = response.json()

    current_weather = data['current']

    live_temp = current_weather['temperature_2m']
    live_rain = current_weather['precipitation']

except:
    live_temp = 28.0
    live_rain = 0.0

# ======================================================
# DATASET HISTORIS CAFE
# ======================================================
df_simulasi = pd.DataFrame({

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
feature_cols = [
    'Suhu',
    'Hujan',
    'Hari_Libur',
    'Ada_Promo',
    'Jam_Operasional',
    'Rating_Cafe',
    'Live_Music',
    'WiFi_Cepat'
]

X = df_simulasi[feature_cols]
y = df_simulasi['Target_Ramai']

# ======================================================
# SPLIT DATA
# ======================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ======================================================
# MODEL RANDOM FOREST
# ======================================================
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# ======================================================
# PREDIKSI TEST
# ======================================================
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

# ======================================================
# METRIK AKURASI
# ======================================================
st.subheader("🎯 Akurasi AI")

st.success(
    f"Akurasi Model Random Forest: {accuracy * 100:.2f}%"
)

# ======================================================
# INPUT USER
# ======================================================
st.subheader("📍 Simulasi Kondisi Café Saat Ini")

col1, col2, col3 = st.columns(3)

with col1:

    st.info(
        f"""
        🌡️ Suhu Live : {live_temp} °C
        🌧️ Curah Hujan : {live_rain} mm
        """
    )

    input_suhu = st.number_input(
        "Input Suhu",
        value=float(live_temp)
    )

    input_hujan = st.number_input(
        "Input Curah Hujan",
        value=float(live_rain)
    )

with col2:

    input_libur = st.selectbox(
        "Status Hari",
        options=[0, 1],
        format_func=lambda x:
        "Hari Kerja" if x == 0 else "Hari Libur"
    )

    input_promo = st.selectbox(
        "Promo Café",
        options=[0, 1],
        format_func=lambda x:
        "Tidak Ada Promo" if x == 0 else "Ada Promo"
    )

    input_jam = st.selectbox(
        "Jam Operasional",
        options=[1, 2, 3],
        format_func=lambda x:
        "Pagi" if x == 1
        else "Sore"
        if x == 2
        else "Malam"
    )

with col3:

    input_rating = st.slider(
        "Rating Café",
        1.0,
        5.0,
        4.5
    )

    input_music = st.selectbox(
        "Live Music",
        options=[0, 1],
        format_func=lambda x:
        "Tidak Ada" if x == 0 else "Ada"
    )

    input_wifi = st.selectbox(
        "WiFi Cepat",
        options=[0, 1],
        format_func=lambda x:
        "Tidak" if x == 0 else "Ya"
    )

# ======================================================
# DATA PREDIKSI
# ======================================================
current_data = pd.DataFrame([[

    input_suhu,
    input_hujan,
    input_libur,
    input_promo,
    input_jam,
    input_rating,
    input_music,
    input_wifi

]], columns=feature_cols)

# ======================================================
# HASIL PREDIKSI
# ======================================================
prediction = model.predict(current_data)[0]

st.subheader("🤖 Hasil Prediksi AI")

if prediction == 1:

    st.error("""
    🔥 Café Diprediksi Akan RAMAI
    
    Rekomendasi:
    ✅ Tambah stok bahan
    ✅ Tambah pegawai
    ✅ Siapkan meja tambahan
    """)

else:

    st.success("""
    😌 Café Diprediksi Normal / Sepi
    
    Rekomendasi:
    ✅ Hemat operasional
    ✅ Fokus promosi
    ✅ Optimasi pelayanan
    """)

# ======================================================
# VISUALISASI
# ======================================================
st.markdown("---")

st.subheader("📊 Dashboard Analitik Café")

g1, g2 = st.columns(2)

# ======================================================
# FEATURE IMPORTANCE
# ======================================================
with g1:

    importance_df = pd.DataFrame({
        'Faktor': feature_cols,
        'Pengaruh': model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by='Pengaruh',
        ascending=False
    )

    fig_bar = px.bar(
        importance_df,
        x='Faktor',
        y='Pengaruh',
        color='Pengaruh',
        title='🔥 Faktor Paling Berpengaruh'
    )

    st.plotly_chart(fig_bar, use_container_width=True)

# ======================================================
# CONFUSION MATRIX
# ======================================================
with g2:

    cm = confusion_matrix(y_test, y_pred)

    fig_cm = ff.create_annotated_heatmap(
        z=cm,
        x=['Prediksi Sepi', 'Prediksi Ramai'],
        y=['Asli Sepi', 'Asli Ramai'],
        annotation_text=cm.astype(str),
        colorscale='Viridis'
    )

    fig_cm.update_layout(
        title='🧠 Confusion Matrix'
    )

    st.plotly_chart(fig_cm, use_container_width=True)

# ======================================================
# GRAFIK PENDAPATAN
# ======================================================
st.subheader("💰 Analisis Pendapatan Café")

fig_income = px.line(
    df_simulasi,
    x='Nama_Cafe',
    y='Pendapatan_Harian',
    markers=True,
    title='Pendapatan Harian Café'
)

st.plotly_chart(fig_income, use_container_width=True)

# ======================================================
# DATAFRAME
# ======================================================
st.subheader("📋 Data Historis Café")

st.dataframe(
    df_simulasi,
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
