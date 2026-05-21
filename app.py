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
    page_title="Cafe Analytics AI",
    page_icon="☕",
    layout="wide"
)

st.title("☕ Cafe Visitor Predictor & Analytics")

st.write(
    "Sistem Analisis & Prediksi Kepadatan Pengunjung Kafe Berbasis Random Forest"
)

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.header("📝 Identitas Mahasiswa")

st.sidebar.write("Nama : Isi Nama")
st.sidebar.write("NIM : Isi NIM")

# ======================================================
# API CUACA LIVE
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
# GENERATE DATASET
# ======================================================
np.random.seed(42)

n_data = 500

df_simulasi = pd.DataFrame({

    'Suhu': np.random.uniform(
        23,
        34,
        n_data
    ),

    'Hujan': np.random.uniform(
        0,
        15,
        n_data
    ),

    'Hari_Libur': np.random.choice(
        [0, 1],
        size=n_data,
        p=[0.7, 0.3]
    ),

    'Ada_Promo': np.random.choice(
        [0, 1],
        size=n_data,
        p=[0.6, 0.4]
    ),

    'Jam_Operasional': np.random.choice(
        [1, 2, 3],
        size=n_data,
        p=[0.2, 0.5, 0.3]
    )

})

# ======================================================
# TARGET RAMAI / SEPI
# ======================================================
df_simulasi['Target_Ramai'] = (

    (df_simulasi['Ada_Promo'] == 1)

    |

    (df_simulasi['Hari_Libur'] == 1)

    |

    (
        (df_simulasi['Hujan'] < 2)

        &

        (df_simulasi['Jam_Operasional'] == 2)
    )

).astype(int)

# ======================================================
# NOISE DATA
# ======================================================
noise = np.random.choice(
    [0, 1],
    size=n_data,
    p=[0.9, 0.1]
)

df_simulasi['Target_Ramai'] = np.where(
    noise == 1,
    1 - df_simulasi['Target_Ramai'],
    df_simulasi['Target_Ramai']
)

# ======================================================
# TANGGAL HARIAN
# ======================================================
df_simulasi['Tanggal'] = pd.date_range(
    start='2025-01-01',
    periods=n_data,
    freq='D'
)

# ======================================================
# NAMA BULAN
# ======================================================
nama_bulan = {

    1: 'Januari',
    2: 'Februari',
    3: 'Maret',
    4: 'April',
    5: 'Mei',
    6: 'Juni',
    7: 'Juli',
    8: 'Agustus',
    9: 'September',
    10: 'Oktober',
    11: 'November',
    12: 'Desember'

}

df_simulasi['No_Bulan'] = df_simulasi[
    'Tanggal'
].dt.month

df_simulasi['Bulan'] = df_simulasi[
    'No_Bulan'
].map(nama_bulan)

# ======================================================
# PENDAPATAN HARIAN
# ======================================================
df_simulasi['Pendapatan_Harian'] = np.random.randint(
    1000000,
    5000000,
    n_data
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
# RANDOM FOREST
# ======================================================
model = RandomForestClassifier(
    n_estimators=150,
    max_depth=8,
    random_state=42
)

model.fit(X_train, y_train)

# ======================================================
# PREDIKSI TEST
# ======================================================
y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

# ======================================================
# AKURASI
# ======================================================
st.subheader("🎯 Performa Akurasi Otak AI")

st.success(
    f"""
    Akurasi Model Random Forest:
    {accuracy * 100:.2f}%
    """
)

# ======================================================
# INPUT USER
# ======================================================
st.subheader("📍 Input Parameter Kondisi Kafe")

col1, col2, col3 = st.columns(3)

# ======================================================
# INPUT 1
# ======================================================
with col1:

    st.info(
        f"""
        🌡️ Suhu Live : {live_temp} °C
        
        🌧️ Hujan Live : {live_rain} mm
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

# ======================================================
# INPUT 2
# ======================================================
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
        "Promo Cafe",
        [0, 1],
        format_func=lambda x:
        "Tidak Ada Promo"
        if x == 0
        else "Ada Promo"
    )

# ======================================================
# INPUT 3
# ======================================================
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
# DATA BARU
# ======================================================
current_data = pd.DataFrame([[
    input_suhu,
    input_hujan,
    input_libur,
    input_promo,
    input_jam
]], columns=feature_cols)

# ======================================================
# HASIL PREDIKSI
# ======================================================
prediction = model.predict(
    current_data
)[0]

st.subheader("🤖 Hasil Prediksi")

if prediction == 1:

    st.error("""
    🔥 AI Memprediksi Kafe Akan Ramai

    ✅ Tambah stok
    ✅ Tambah pegawai
    ✅ Siapkan meja tambahan
    """)

else:

    st.success("""
    😌 AI Memprediksi Kafe Normal / Sepi

    ✅ Hemat operasional
    ✅ Fokus promosi
    """)

# ======================================================
# VISUALISASI
# ======================================================
st.markdown("---")

st.subheader("📊 Analisis Operasional Kafe")

g1, g2 = st.columns(2)

# ======================================================
# FEATURE IMPORTANCE
# ======================================================
with g1:

    importance_df = pd.DataFrame({

        'Faktor Pengaruh': [
            'Suhu',
            'Curah Hujan',
            'Hari Libur',
            'Promo',
            'Jam Operasional'
        ],

        'Tingkat Pengaruh':
        model.feature_importances_

    })

    importance_df = importance_df.sort_values(
        by='Tingkat Pengaruh',
        ascending=False
    )

    fig_bar = px.bar(

        importance_df,

        x='Faktor Pengaruh',

        y='Tingkat Pengaruh',

        color='Tingkat Pengaruh',

        title='🔥 Faktor Paling Berpengaruh'

    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

# ======================================================
# CONFUSION MATRIX
# ======================================================
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

        colorscale='Cividis'

    )

    fig_cm.update_layout(
        title='🧠 Confusion Matrix'
    )

    st.plotly_chart(
        fig_cm,
        use_container_width=True
    )

# ======================================================
# REKAP BULANAN
# ======================================================
laporan_bulanan = df_simulasi.groupby(
    ['No_Bulan', 'Bulan'],
    as_index=False
).agg({

    'Pendapatan_Harian': 'sum',

    'Target_Ramai': 'sum',

    'Suhu': 'mean',

    'Hujan': 'mean'

})

# ======================================================
# SORT BULAN
# ======================================================
laporan_bulanan = laporan_bulanan.sort_values(
    by='No_Bulan'
)

# ======================================================
# UBAH NAMA KOLOM
# ======================================================
laporan_bulanan.columns = [

    'No_Bulan',

    'Bulan',

    'Total_Pendapatan',

    'Total_Hari_Ramai',

    'Rata_Rata_Suhu',

    'Rata_Rata_Hujan'

]

# ======================================================
# TABS
# ======================================================
st.markdown("---")

st.subheader("📋 Laporan Statistik Bulanan")

tab1, tab2, tab3 = st.tabs([

    "📅 Tabel Bulanan",

    "📈 Grafik Bulanan",

    "📄 Detail Harian"

])

# ======================================================
# TAB 1
# ======================================================
with tab1:

    st.dataframe(
        laporan_bulanan,
        use_container_width=True
    )

# ======================================================
# TAB 2
# ======================================================
with tab2:

    fig_bulanan = px.bar(

        laporan_bulanan,

        x='Bulan',

        y='Total_Pendapatan',

        color='Total_Pendapatan',

        text_auto=True,

        title='💰 Total Pendapatan Per Bulan'

    )

    st.plotly_chart(
        fig_bulanan,
        use_container_width=True
    )

# ======================================================
# TAB 3 DETAIL HARIAN
# ======================================================
with tab3:

    pilih_bulan = st.selectbox(

        "Pilih Bulan",

        laporan_bulanan['Bulan']

    )

    # FILTER DATA
    data_harian = df_simulasi[
        df_simulasi['Bulan'] == pilih_bulan
    ]

    st.subheader(
        f"📅 Data Harian Bulan {pilih_bulan}"
    )

    # TABEL DETAIL
    st.dataframe(

        data_harian[[

            'Tanggal',

            'Suhu',

            'Hujan',

            'Hari_Libur',

            'Ada_Promo',

            'Jam_Operasional',

            'Pendapatan_Harian',

            'Target_Ramai'

        ]],

        use_container_width=True

    )

    # GRAFIK HARIAN
    fig_harian = px.line(

        data_harian,

        x='Tanggal',

        y='Pendapatan_Harian',

        markers=True,

        title=f'📈 Pendapatan Harian Bulan {pilih_bulan}'

    )

    st.plotly_chart(
        fig_harian,
        use_container_width=True
    )

# ======================================================
# LAPORAN AI
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
st.markdown("<br><br>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 4])

with col_left:

    st.markdown(
        """
        <p style='
        text-align:left;
        color:#777;
        font-size:10px;
        margin:0;'>
        made with ❤️ by temennya Rafi
        </p>
        """,
        unsafe_allow_html=True
    )
