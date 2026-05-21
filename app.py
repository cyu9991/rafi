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

    'Suhu': np.random.randint(
        25,
        34,
        n_data
    ),

    'Hujan': np.random.randint(
        0,
        11,
        n_data
    ),

    'Hari_Libur': np.random.choice(
        [0, 1],
        size=n_data,
        p=[0.75, 0.25]
    ),

    'Ada_Promo': np.random.choice(
        [0, 1],
        size=n_data,
        p=[0.7, 0.3]
    ),

    'Jam_Operasional': np.random.choice(
        [1, 2, 3],
        size=n_data,
        p=[0.3, 0.5, 0.2]
    )

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

df_simulasi['No_Bulan'] = (
    df_simulasi['Tanggal']
    .dt.month
)

df_simulasi['Bulan'] = (
    df_simulasi['No_Bulan']
    .map(nama_bulan)
)

# ======================================================
# TARGET RAMAI (LEBIH REALISTIS)
# ======================================================
score = []

for i in range(n_data):

    nilai = 0

    if df_simulasi.loc[i, 'Ada_Promo'] == 1:
        nilai += 30

    if df_simulasi.loc[i, 'Hari_Libur'] == 1:
        nilai += 25

    if df_simulasi.loc[i, 'Jam_Operasional'] == 2:
        nilai += 20

    if df_simulasi.loc[i, 'Hujan'] < 3:
        nilai += 15

    if 26 <= df_simulasi.loc[i, 'Suhu'] <= 30:
        nilai += 10

    # Noise random
    nilai += np.random.randint(-40, 40)

    score.append(nilai)

df_simulasi['Skor_Ramai'] = score

df_simulasi['Target_Ramai'] = (
    df_simulasi['Skor_Ramai'] >= 40
).astype(int)

# ======================================================
# JUMLAH PENGUNJUNG
# ======================================================
jumlah_pengunjung = []

for i in range(n_data):

    ramai = df_simulasi.loc[i, 'Target_Ramai']

    promo = df_simulasi.loc[i, 'Ada_Promo']

    libur = df_simulasi.loc[i, 'Hari_Libur']

    hujan = df_simulasi.loc[i, 'Hujan']

    jam = df_simulasi.loc[i, 'Jam_Operasional']

    pengunjung = 20

    if ramai == 1:
        pengunjung += 25

    if promo == 1:
        pengunjung += 10

    if libur == 1:
        pengunjung += 15

    if jam == 2:
        pengunjung += 15

    if hujan > 7:
        pengunjung -= 10

    pengunjung += np.random.randint(-5, 8)

    pengunjung = max(pengunjung, 5)

    jumlah_pengunjung.append(pengunjung)

df_simulasi['Jumlah_Pengunjung'] = jumlah_pengunjung

# ======================================================
# PENDAPATAN CAFE PINGGIR JALAN
# ======================================================
pendapatan = []

for i in range(n_data):

    pengunjung = df_simulasi.loc[
        i,
        'Jumlah_Pengunjung'
    ]

    promo = df_simulasi.loc[
        i,
        'Ada_Promo'
    ]

    rata_belanja = 15000

    if promo == 1:
        rata_belanja -= 2000

    rata_belanja += np.random.randint(
        -1000,
        2000
    )

    total = pengunjung * rata_belanja

    pendapatan.append(total)

df_simulasi[
    'Pendapatan_Harian'
] = pendapatan

# Format Rupiah
df_simulasi['Pendapatan_Rp'] = (
    'Rp ' +
    df_simulasi['Pendapatan_Harian']
    .astype(int)
    .apply(lambda x: f"{x:,}".replace(",", "."))
)

# ======================================================
# FEATURE & TARGET
# ======================================================
feature_cols = [

    'Suhu',
    'Hujan',
    'Hari_Libur',
    'Ada_Promo',
    'Jam_Operasional'

]

X = df_simulasi[
    feature_cols
]

y = df_simulasi[
    'Target_Ramai'
]

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

    n_estimators=100,

    max_depth=5,

    random_state=42

)

model.fit(
    X_train,
    y_train
)

y_pred = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    y_pred
)

# ======================================================
# AKURASI MODEL
# ======================================================
st.subheader("🎯 Akurasi AI")

st.success(
    f"""
    Tingkat Akurasi Model:
    {accuracy * 100:.2f}%
    """
)

# ======================================================
# INPUT USER
# ======================================================
st.markdown("---")

st.subheader("📍 Simulasi Kondisi Café")

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
        min_value=20,
        max_value=40,
        value=live_temp
    )

    input_hujan = st.number_input(
        "Input Curah Hujan",
        min_value=0,
        max_value=20,
        value=live_rain
    )

with col2:

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

with col3:

    input_jam = st.selectbox(
        "Jam Operasional",
        [1, 2, 3],
        format_func=lambda x:
        "Pagi"
        if x == 1
        else "Sore"
        if x == 2
        else "Malam"
    )

# ======================================================
# BUTTON ANALISIS
# ======================================================
analisis = st.button(
    "🔍 Analisis AI Sekarang",
    use_container_width=True
)

# ======================================================
# HASIL AI
# ======================================================
if analisis:

    current_data = pd.DataFrame([[
        input_suhu,
        input_hujan,
        input_libur,
        input_promo,
        input_jam
    ]], columns=feature_cols)

    prediction = model.predict(
        current_data
    )[0]

    probability = model.predict_proba(
        current_data
    )[0]

    persen_sepi = probability[0] * 100

    persen_ramai = probability[1] * 100

    estimasi_pengunjung = 20

    if input_promo == 1:
        estimasi_pengunjung += 10

    if input_libur == 1:
        estimasi_pengunjung += 15

    if input_jam == 2:
        estimasi_pengunjung += 15

    if input_hujan > 7:
        estimasi_pengunjung -= 10

    estimasi_pengunjung = max(
        estimasi_pengunjung,
        5
    )

    rata_belanja = 15000

    estimasi_pendapatan = (
        estimasi_pengunjung *
        rata_belanja
    )

    pendapatan_format = (
        f"Rp {estimasi_pendapatan:,}"
        .replace(",", ".")
    )

    st.markdown("---")

    st.subheader("🤖 Hasil Analisis AI")

    if prediction == 1:

        st.error(
            f"""
            🔥 Café Diprediksi Akan RAMAI

            📌 Keyakinan AI:
            {persen_ramai:.2f}%

            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang

            💰 Estimasi Pendapatan:
            {pendapatan_format}
            """
        )

    else:

        st.success(
            f"""
            😌 Café Diprediksi Normal / Sepi

            📌 Keyakinan AI:
            {persen_sepi:.2f}%

            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang

            💰 Estimasi Pendapatan:
            {pendapatan_format}
            """
        )

# ======================================================
# DASHBOARD ANALITIK
# ======================================================
st.markdown("---")

st.subheader("📊 Dashboard Analitik Café")

g1, g2 = st.columns(2)

with g1:

    importance_df = pd.DataFrame({

        'Faktor': [

            'Suhu',
            'Curah Hujan',
            'Hari Libur',
            'Promo',
            'Jam Operasional'

        ],

        'Pengaruh':
        model.feature_importances_

    })

    fig_bar = px.bar(

        importance_df,

        x='Faktor',

        y='Pengaruh',

        color='Pengaruh',

        title='🔥 Faktor Paling Berpengaruh'

    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

with g2:

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    fig_cm = ff.create_annotated_heatmap(

        z=cm,

        x=[
            'Prediksi Sepi',
            'Prediksi Ramai'
        ],

        y=[
            'Asli Sepi',
            'Asli Ramai'
        ],

        annotation_text=cm.astype(str),

        colorscale='Viridis'

    )

    fig_cm.update_layout(
        title='🧠 Confusion Matrix'
    )

    st.plotly_chart(
        fig_cm,
        use_container_width=True
    )

# ======================================================
# LAPORAN BULANAN
# ======================================================
st.markdown("---")

st.subheader("📈 Laporan Statistik Bulanan")

laporan_bulanan = df_simulasi.groupby(
    'Bulan',
    sort=False
).agg({

    'Jumlah_Pengunjung': 'sum',
    'Pendapatan_Harian': 'sum',
    'Suhu': 'mean',
    'Hujan': 'mean'

}).reset_index()

laporan_bulanan.columns = [

    'Bulan',
    'Total Pengunjung',
    'Total Pendapatan',
    'Rata-rata Suhu',
    'Rata-rata Hujan'

]

laporan_bulanan['Rata-rata Suhu'] = (
    laporan_bulanan['Rata-rata Suhu']
    .astype(int)
)

laporan_bulanan['Rata-rata Hujan'] = (
    laporan_bulanan['Rata-rata Hujan']
    .astype(int)
)

laporan_bulanan['Total Pendapatan'] = (
    laporan_bulanan['Total Pendapatan']
    .apply(
        lambda x:
        f"Rp {x:,}".replace(",", ".")
    )
)

st.dataframe(

    laporan_bulanan,

    use_container_width=True,

    hide_index=True

)

# ======================================================
# DETAIL HARIAN
# ======================================================
st.markdown("---")

st.subheader("📅 Detail Data Harian")

bulan_pilih = st.selectbox(

    "Pilih Bulan",

    laporan_bulanan['Bulan']

)

detail_harian = df_simulasi[
    df_simulasi['Bulan'] == bulan_pilih
][[
    'Tanggal',
    'Suhu',
    'Hujan',
    'Hari_Libur',
    'Ada_Promo',
    'Jam_Operasional',
    'Jumlah_Pengunjung',
    'Pendapatan_Rp'
]]

detail_harian = detail_harian.rename(columns={

    'Suhu': 'Suhu °C',
    'Hujan': 'Hujan mm',
    'Hari_Libur': 'Hari Libur',
    'Ada_Promo': 'Promo',
    'Jam_Operasional': 'Shift',
    'Jumlah_Pengunjung': 'Pengunjung',
    'Pendapatan_Rp': 'Pendapatan'

})

st.dataframe(

    detail_harian,

    use_container_width=True,

    hide_index=True

)

# ======================================================
# CLASSIFICATION REPORT
# ======================================================
st.markdown("---")

st.subheader("📄 Laporan Klasifikasi AI")

st.text(

    classification_report(
        y_test,
        y_pred
    )

)

# ======================================================
# FOOTER
# ======================================================
st.markdown("---")

st.caption(
    "made with ❤️ by temennya Rafi"
)
