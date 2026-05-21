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

#======SETUP STREAMLIT===============
st.set_page_config(
    page_title="Cafe Analytics AI",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Cafe Visitor Predictor & Analytics")
st.write("Sistem Analisis & Prediksi Kepadatan Pengunjung Kafe Berbasis Random Forest")

#======SIDEBAR IDENTITAS=================
st.sidebar.header("📝 Identitas Mahasiswa")
st.sidebar.write("Nama: [Isi Nama Temen Lu]")
st.sidebar.write("NIM: [Isi NIM Temen Lu]")

#=======AMBIL DATA CUACA LIVE KOTA PALU (FAKTOR EKSTERNAL)==========
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

#=======GENERATE DATASET SIMULASI KAFE (500 DATA HISTORIS)==========
np.random.seed(42)
n_data = 500

df_simulasi = pd.DataFrame({
    'Suhu': np.random.uniform(23, 34, n_data),
    'Hujan': np.random.uniform(0, 15, n_data),
    'Hari_Libur': np.random.choice([0, 1], size=n_data, p=[0.7, 0.3]), 
    'Ada_Promo': np.random.choice([0, 1], size=n_data, p=[0.6, 0.4]),  
    'Jam_Operasional': np.random.choice([1, 2, 3], size=n_data, p=[0.2, 0.5, 0.3]) 
})

# Aturan target: 1 = Ramai, 0 = Sepi
df_simulasi['Target_Ramai'] = (
    (df_simulasi['Ada_Promo'] == 1) | 
    (df_simulasi['Hari_Libur'] == 1) | 
    ((df_simulasi['Hujan'] < 2) & (df_simulasi['Jam_Operasional'] == 2))
).astype(int)

noise = np.random.choice([0, 1], size=n_data, p=[0.9, 0.1])
df_simulasi['Target_Ramai'] = np.where(noise == 1, 1 - df_simulasi['Target_Ramai'], df_simulasi['Target_Ramai'])

#=======FEATURE & TARGET SELECTION==========
feature_cols = ['Suhu', 'Hujan', 'Hari_Libur', 'Ada_Promo', 'Jam_Operasional']
X = df_simulasi[feature_cols]
y = df_simulasi['Target_Ramai']

#====SPLIT DATA=========
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#=======RANDOM FOREST MODEL=========
model = RandomForestClassifier(n_estimators=150, max_depth=8, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

#======TAMPILAN METRIK AKURASI AI=========
st.subheader("🎯 Performa Akurasi Otak AI")
st.success(f"Akurasi Model Random Forest dalam Membaca Pola Pengunjung: {accuracy * 100:.2f}%")

#========INPUT SIMULASI KONDISI KAFE SAAT INI========
st.subheader("📍 Input Parameter Kondisi Kafe (Detik Ini)")
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    st.info(f"⛅ Cuaca Live Luar Ruangan: {live_temp} °C, Hujan: {live_rain} mm")
    input_suhu = st.number_input("Sesuaikan Suhu Ruangan/Luar (°C)", value=float(live_temp))
    input_hujan = st.number_input("Sesuaikan Tingkat Hujan (mm)", value=float(live_rain))

with col_in2:
    input_libur = st.selectbox("Status Hari", options=[0, 1], format_func=lambda x: "Hari Kerja (Ordinary Day)" if x==0 else "Hari Libur / Akhir Pekan (Weekend)")
    input_promo = st.selectbox("Program Diskon/Promo Kafe", options=[0, 1], format_func=lambda x: "Tidak Ada Promo" if x==0 else "Ada Promo Aktif (e.g. Buy 1 Get 1)")

with col_in3:
    input_jam = st.selectbox("Shift Jam Operasional", options=[1, 2, 3], format_func=lambda x: "Pagi - Siang (09:00 - 15:00)" if x==1 else "Sore - Maghrib / Prime Time (15:00 - 19:00)" if x==2 else "Malam (19:00 - 23:00)")

#=====PROSES PREDIKSI REALTIME======
current_data = pd.DataFrame([[
    input_suhu, input_hujan, input_libur, input_promo, input_jam
]], columns=feature_cols)

prediction = model.predict(current_data)[0]

st.subheader("🤖 Hasil Prediksi Kepadatan Pengunjung")
if prediction == 1:
    st.error("🔥 AI Memprediksi: KAFE BAKAL RAMAI! (Siapkan Bahan Baku & Server Tambahan)")
else:
    st.success("✅ AI Memprediksi: Kondisi Kafe Normal / Santai (Cocok untuk Efisiensi Staf)")

st.markdown("---")

#=======VISUALISASI GRAFIK TREN & EVALUASI==========
st.subheader("📊 Analisis Data Finansial & Operasional Kafe")
c_graph1, c_graph2 = st.columns(2)

with c_graph1:
    importance_df = pd.DataFrame({
        'Faktor Pengaruh': ['Suhu', 'Curah Hujan', 'Hari Libur', 'Promo Diskon', 'Jam Kerja'],
        'Tingkat Pengaruh': model.feature_importances_
    }).sort_values(by='Tingkat Pengaruh', ascending=False)
    
    fig_bar = px.bar(importance_df, x='Faktor Pengaruh', y='Tingkat Pengaruh', title='🔥 Faktor Paling Sensitif Bikin Kafe Ramai', color='Tingkat Pengaruh')
    st.plotly_chart(fig_bar, use_container_width=True)

with c_graph2:
    cm = confusion_matrix(y_test, y_pred)
    fig_cm = ff.create_annotated_heatmap(
        z=cm, x=['Prediksi Sepi', 'Prediksi Ramai'], y=['Asli Sepi', 'Asli Ramai'],
        annotation_text=cm.astype(str), colorscale='Cividis'
    )
    fig_cm.update_layout(title_text='🧠 Confusion Matrix (Uji Akurasi Tebakan AI)')
    st.plotly_chart(fig_cm, use_container_width=True)

st.markdown("---")

#====CLASSIFICATION REPORT & DATASET====
st.subheader("📋 Laporan Statistik & Basis Data Riwayat Kafe")
tab1, tab2 = st.tabs(["Tabel Data Riwayat", "Laporan Klasifikasi Formal"])

with tab1:
    st.dataframe(df_simulasi, use_container_width=True)
with tab2:
    st.text(classification_report(y_test, y_pred))

#======FOOTER POJOK KIRI=========
st.markdown("<br><br>", unsafe_allow_html=True)
col_left, col_right = st.columns([1, 4])
with col_left:
    st.markdown("<p style='text-align: left; color: #777; font-size: 10px; margin: 0;'>made with  by temennya Rafi</p>", unsafe_allow_html=True)
