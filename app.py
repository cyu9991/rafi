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
    page_title="Cafe Analytics AI Indonesia",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Cafe Analytics AI Indonesia")

st.write("""
Sistem Analisis & Prediksi Kepadatan Pengunjung Café Pinggir Jalan
Menggunakan Artificial Intelligence Random Forest
""")

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.header("📝 Identitas Mahasiswa")

st.sidebar.write("Nama : Isi Nama")
st.sidebar.write("NIM : Isi NIM")
st.sidebar.write("Kampus : UNTAD")

# ======================================================
# API CUACA LIVE PALU
# ======================================================
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
    live_temp = 28
    live_rain = 0

# ======================================================
# GENERATE DATASET
# ======================================================
np.random.seed(42)

n_data = 120

tanggal = pd.date_range(
    start='2025-01-01',
    periods=n_data,
    freq='D'
)

df_simulasi = pd.DataFrame({
    'Tanggal': tanggal,
    'Suhu': np.random.randint(25, 34, n_data),
    'Hujan': np.random.randint(0, 11, n_data),
    'Hari_Libur': np.random.choice([0, 1], size=n_data, p=[0.75, 0.25]),
    'Ada_Promo': np.random.choice([0, 1], size=n_data, p=[0.7, 0.3]),
    'Shift': np.random.choice([1, 2], size=n_data, p=[0.5, 0.5])  # 👈 FIX 2 SHIFT
})

# ======================================================
# BULAN
# ======================================================
nama_bulan = {
    1: 'Januari',
    2: 'Februari',
    3: 'Maret',
    4: 'April'
}

df_simulasi['No_Bulan'] = df_simulasi['Tanggal'].dt.month
df_simulasi['Bulan'] = df_simulasi['No_Bulan'].map(nama_bulan)

# ======================================================
# TARGET RAMAI
# ======================================================
score = []

for i in range(n_data):
    nilai = 0

    if df_simulasi.loc[i, 'Ada_Promo'] == 1:
        nilai += 30

    if df_simulasi.loc[i, 'Hari_Libur'] == 1:
        nilai += 25

    if df_simulasi.loc[i, 'Shift'] == 2:
        nilai += 20

    if df_simulasi.loc[i, 'Hujan'] < 3:
        nilai += 15

    if 26 <= df_simulasi.loc[i, 'Suhu'] <= 30:
        nilai += 10

    nilai += np.random.randint(-40, 40)
    score.append(nilai)

df_simulasi['Skor_Ramai'] = score
df_simulasi['Target_Ramai'] = (df_simulasi['Skor_Ramai'] >= 40).astype(int)

# ======================================================
# JUMLAH PENGUNJUNG
# ======================================================
jumlah_pengunjung = []

for i in range(n_data):
    ramai = df_simulasi.loc[i, 'Target_Ramai']
    promo = df_simulasi.loc[i, 'Ada_Promo']
    libur = df_simulasi.loc[i, 'Hari_Libur']
    hujan = df_simulasi.loc[i, 'Hujan']
    shift = df_simulasi.loc[i, 'Shift']

    pengunjung = 20

    if ramai == 1:
        pengunjung += 25
    if promo == 1:
        pengunjung += 10
    if libur == 1:
        pengunjung += 15
    if shift == 2:
        pengunjung += 15
    if hujan > 7:
        pengunjung -= 10

    pengunjung += np.random.randint(-5, 8)
    pengunjung = max(pengunjung, 5)

    jumlah_pengunjung.append(pengunjung)

df_simulasi['Jumlah_Pengunjung'] = jumlah_pengunjung

# ======================================================
# PENDAPATAN
# ======================================================
pendapatan = []

for i in range(n_data):
    pengunjung = df_simulasi.loc[i, 'Jumlah_Pengunjung']
    promo = df_simulasi.loc[i, 'Ada_Promo']

    rata_belanja = 15000

    if promo == 1:
        rata_belanja -= 2000

    rata_belanja += np.random.randint(-1000, 2000)

    pendapatan.append(pengunjung * rata_belanja)

df_simulasi['Pendapatan_Harian'] = pendapatan

# ======================================================
# FEATURE
# ======================================================
feature_cols = ['Suhu', 'Hujan', 'Hari_Libur', 'Ada_Promo', 'Shift']

X = df_simulasi[feature_cols]
y = df_simulasi['Target_Ramai']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

st.subheader("🎯 Akurasi AI")
st.success(f"Tingkat Akurasi Model: {accuracy * 100:.2f}%")

# ======================================================
# INPUT USER
# ======================================================
st.subheader("📍 Simulasi Kondisi Café")

col1, col2, col3 = st.columns(3)

with col1:
    input_suhu = st.number_input("Input Suhu", 20, 40, live_temp)
    input_hujan = st.number_input("Input Hujan", 0, 20, live_rain)

with col2:
    input_libur = st.selectbox("Hari", [0, 1],
        format_func=lambda x: "Kerja" if x == 0 else "Libur")

    input_promo = st.selectbox("Promo", [0, 1],
        format_func=lambda x: "Tidak" if x == 0 else "Ada")

with col3:
    input_shift = st.selectbox("Shift", [1, 2],
        format_func=lambda x: f"Shift {x}")

analisis = st.button("🔍 Analisis AI Sekarang")

# ======================================================
# HASIL
# ======================================================
if analisis:

    current_data = pd.DataFrame([[input_suhu, input_hujan, input_libur, input_promo, input_shift]],
                                columns=feature_cols)

    prediction = model.predict(current_data)[0]
    probability = model.predict_proba(current_data)[0]

    estimasi_pengunjung = 20

    if input_promo == 1:
        estimasi_pengunjung += 10
    if input_libur == 1:
        estimasi_pengunjung += 15
    if input_shift == 2:
        estimasi_pengunjung += 15
    if input_hujan > 7:
        estimasi_pengunjung -= 10

    estimasi_pengunjung = max(estimasi_pengunjung, 5)
    estimasi_pendapatan = estimasi_pengunjung * 15000

    st.subheader("🤖 Hasil Analisis")

    if prediction == 1:
        st.error("🔥 Café RAMAI")
    else:
        st.success("😌 Café SEPI / Normal")

# ======================================================
# SHIFT DETAIL (2 SHIFT)
# ======================================================
st.subheader("📅 Detail Shift")

detail_shift = []

for i in range(len(df_simulasi)):
    for shift in [1, 2]:  # 👈 FIX

        pengunjung = np.random.randint(10, 40)

        detail_shift.append({
            "Tanggal": df_simulasi.loc[i, "Tanggal"],
            "Bulan": df_simulasi.loc[i, "Bulan"],
            "Shift": f"Shift {shift}",
            "Pengunjung": pengunjung
        })

df_detail_shift = pd.DataFrame(detail_shift)

st.dataframe(df_detail_shift, use_container_width=True)
