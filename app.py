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
Sistem Analisis & Prediksi Kepadatan Pengunjung Café
Menggunakan Machine Learning Random Forest
""")

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

    response = requests.get(url)

    data = response.json()

    current_weather = data['current']

    live_temp = current_weather['temperature_2m']

    live_rain = current_weather['precipitation']

except:

    live_temp = 28.0

    live_rain = 0.0

# ======================================================
# GENERATE DATASET REALISTIS
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

    'Suhu': np.random.uniform(
        25,
        33,
        n_data
    ),

    'Hujan': np.random.uniform(
        0,
        10,
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
# TARGET RAMAI
# ======================================================
df_simulasi['Target_Ramai'] = (

    (
        df_simulasi['Ada_Promo'] == 1
    )

    |

    (
        df_simulasi['Hari_Libur'] == 1
    )

    |

    (
        (
            df_simulasi['Hujan'] < 2
        )

        &

        (
            df_simulasi['Jam_Operasional'] == 2
        )
    )

).astype(int)

# ======================================================
# JUMLAH PENGUNJUNG
# ======================================================
jumlah_pengunjung = []

for i in range(n_data):

    ramai = df_simulasi.loc[
        i,
        'Target_Ramai'
    ]

    promo = df_simulasi.loc[
        i,
        'Ada_Promo'
    ]

    libur = df_simulasi.loc[
        i,
        'Hari_Libur'
    ]

    hujan = df_simulasi.loc[
        i,
        'Hujan'
    ]

    if ramai == 1:

        pengunjung = np.random.randint(
            80,
            140
        )

    else:

        pengunjung = np.random.randint(
            20,
            70
        )

    # Promo menambah pengunjung
    if promo == 1:

        pengunjung += np.random.randint(
            10,
            25
        )

    # Hari libur tambah pengunjung
    if libur == 1:

        pengunjung += np.random.randint(
            15,
            30
        )

    # Hujan deras kurangi pengunjung
    if hujan > 7:

        pengunjung -= np.random.randint(
            10,
            25
        )

    pengunjung = max(
        pengunjung,
        15
    )

    jumlah_pengunjung.append(
        pengunjung
    )

df_simulasi[
    'Jumlah_Pengunjung'
] = jumlah_pengunjung

# ======================================================
# PENDAPATAN REALISTIS INDONESIA
# ======================================================
pendapatan = []

for pengunjung in df_simulasi[
    'Jumlah_Pengunjung'
]:

    # Rata-rata orang belanja
    # 28rb - 45rb
    rata_belanja = np.random.randint(
        28000,
        45000
    )

    total = (
        pengunjung *
        rata_belanja
    )

    pendapatan.append(total)

df_simulasi[
    'Pendapatan_Harian'
] = pendapatan

# ======================================================
# FORMAT JUTA
# ======================================================
df_simulasi[
    'Pendapatan_Juta'
] = (
    df_simulasi[
        'Pendapatan_Harian'
    ] / 1000000
).round(2)

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
# RANDOM FOREST
# ======================================================
model = RandomForestClassifier(

    n_estimators=200,

    max_depth=10,

    random_state=42

)

model.fit(
    X_train,
    y_train
)

# ======================================================
# PREDIKSI TEST
# ======================================================
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
st.subheader("🎯 Akurasi Artificial Intelligence")

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

# ======================================================
# KOLOM 1
# ======================================================
with col1:

    st.info(
        f"""
        🌡️ Suhu Live : {live_temp} °C
        
        🌧️ Curah Hujan : {live_rain} mm
        """
    )

    input_suhu = st.number_input(

        "Input Suhu",

        min_value=20.0,

        max_value=40.0,

        value=float(live_temp)

    )

    input_hujan = st.number_input(

        "Input Curah Hujan",

        min_value=0.0,

        max_value=20.0,

        value=float(live_rain)

    )

# ======================================================
# KOLOM 2
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

        "Program Promo",

        [0, 1],

        format_func=lambda x:
        "Tidak Ada Promo"
        if x == 0
        else "Ada Promo"

    )

# ======================================================
# KOLOM 3
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
# BUTTON ANALISIS
# ======================================================
st.markdown("")

analisis = st.button(
    "🔍 Analisis AI Sekarang",
    use_container_width=True
)

# ======================================================
# HASIL PREDIKSI AI
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

    st.markdown("---")

    st.subheader("🤖 Hasil Analisis AI")

    # ==================================================
    # RAMAI
    # ==================================================
    if prediction == 1:

        estimasi_pengunjung = np.random.randint(
            90,
            160
        )

        rata_belanja = np.random.randint(
            30000,
            45000
        )

        estimasi_pendapatan = (
            estimasi_pengunjung *
            rata_belanja
        ) / 1000000

        st.error(
            f"""
            🔥 Café Diprediksi Akan RAMAI
            
            📌 Keyakinan AI:
            {persen_ramai:.2f}%
            
            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang
            
            💰 Estimasi Pendapatan:
            Rp {estimasi_pendapatan:.2f} Juta
            """
        )

    # ==================================================
    # SEPI
    # ==================================================
    else:

        estimasi_pengunjung = np.random.randint(
            20,
            70
        )

        rata_belanja = np.random.randint(
            25000,
            40000
        )

        estimasi_pendapatan = (
            estimasi_pengunjung *
            rata_belanja
        ) / 1000000

        st.success(
            f"""
            😌 Café Diprediksi Normal / Sepi
            
            📌 Keyakinan AI:
            {persen_sepi:.2f}%
            
            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang
            
            💰 Estimasi Pendapatan:
            Rp {estimasi_pendapatan:.2f} Juta
            """
        )

# ======================================================
# DASHBOARD
# ======================================================
st.markdown("---")

st.subheader("📊 Dashboard Analitik Café")

g1, g2 = st.columns(2)

# ======================================================
# FEATURE IMPORTANCE
# ======================================================
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
laporan_bulanan = df_simulasi.groupby(
    ['No_Bulan', 'Bulan'],
    as_index=False
).agg({

    'Jumlah_Pengunjung': 'sum',

    'Pendapatan_Juta': 'sum',

    'Target_Ramai': 'sum',

    'Suhu': 'mean',

    'Hujan': 'mean',

    'Ada_Promo': 'sum',

    'Hari_Libur': 'sum'

})

# ======================================================
# SORT BULAN
# ======================================================
laporan_bulanan = laporan_bulanan.sort_values(
    by='No_Bulan'
)

# ======================================================
# TAMBAHAN STATISTIK
# ======================================================
laporan_bulanan[
    'Rata2_Pengunjung_Harian'
] = (
    laporan_bulanan[
        'Jumlah_Pengunjung'
    ] / 30
).astype(int)

laporan_bulanan[
    'Rata2_Pendapatan_Juta'
] = (
    laporan_bulanan[
        'Pendapatan_Juta'
    ] / 30
).round(2)

laporan_bulanan[
    'Persentase_Ramai'
] = (
    (
        laporan_bulanan[
            'Target_Ramai'
        ] / 30
    ) * 100
).round(1)

# ======================================================
# UBAH NAMA KOLOM
# ======================================================
laporan_bulanan.columns = [

    'No_Bulan',

    'Bulan',

    'Total_Pengunjung',

    'Total_Pendapatan_Juta',

    'Total_Hari_Ramai',

    'Rata_Rata_Suhu',

    'Rata_Rata_Hujan',

    'Total_Hari_Promo',

    'Total_Hari_Libur',

    'Rata2_Pengunjung_Harian',

    'Rata2_Pendapatan_Juta',

    'Persentase_Ramai'

]

# ======================================================
# BULATKAN ANGKA
# ======================================================
laporan_bulanan[
    'Rata_Rata_Suhu'
] = laporan_bulanan[
    'Rata_Rata_Suhu'
].round(1)

laporan_bulanan[
    'Rata_Rata_Hujan'
] = laporan_bulanan[
    'Rata_Rata_Hujan'
].round(1)

laporan_bulanan[
    'Total_Pendapatan_Juta'
] = laporan_bulanan[
    'Total_Pendapatan_Juta'
].round(2)

# ======================================================
# TABS
# ======================================================
st.markdown("---")

st.subheader("📋 Laporan Statistik Januari - April")

tab1, tab2, tab3 = st.tabs([

    "📅 Statistik Bulanan",

    "📈 Grafik Pendapatan",

    "📄 Detail Harian"

])

# ======================================================
# TAB 1
# ======================================================
with tab1:

    st.dataframe(

        laporan_bulanan[[

            'Bulan',

            'Total_Pengunjung',

            'Rata2_Pengunjung_Harian',

            'Total_Pendapatan_Juta',

            'Rata2_Pendapatan_Juta',

            'Total_Hari_Ramai',

            'Persentase_Ramai',

            'Total_Hari_Promo',

            'Total_Hari_Libur',

            'Rata_Rata_Suhu',

            'Rata_Rata_Hujan'

        ]].style.hide(axis="index"),

        use_container_width=True

    )

# ======================================================
# TAB 2
# ======================================================
with tab2:

    fig_bulanan = px.bar(

        laporan_bulanan,

        x='Bulan',

        y='Total_Pendapatan_Juta',

        color='Total_Pendapatan_Juta',

        text_auto=True,

        title='💰 Pendapatan Café (Juta Rupiah)'

    )

    st.plotly_chart(
        fig_bulanan,
        use_container_width=True
    )

# ======================================================
# TAB 3
# ======================================================
with tab3:

    pilih_bulan = st.selectbox(

        "Pilih Bulan",

        laporan_bulanan['Bulan']

    )

    data_harian = df_simulasi[
        df_simulasi['Bulan'] == pilih_bulan
    ]

    st.subheader(
        f"📅 Data Harian Bulan {pilih_bulan}"
    )

    st.dataframe(

        data_harian[[

            'Tanggal',

            'Suhu',

            'Hujan',

            'Hari_Libur',

            'Ada_Promo',

            'Jam_Operasional',

            'Jumlah_Pengunjung',

            'Pendapatan_Juta',

            'Target_Ramai'

        ]].style.hide(axis="index"),

        use_container_width=True

    )

# ======================================================
# LAPORAN KLASIFIKASI
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

st.caption("made with ❤️ by temennya Rafi")
