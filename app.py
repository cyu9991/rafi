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
Sistem Analisis & Prediksi Kepadatan Pengunjung
Café Berbasis Artificial Intelligence
(Random Forest Machine Learning)
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

    live_temp = current_weather['temperature_2m']

    live_rain = current_weather['precipitation']

except:

    live_temp = 28.0

    live_rain = 0.0

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

    'Suhu': np.random.uniform(
        24,
        33,
        n_data
    ),

    'Hujan': np.random.uniform(
        0,
        12,
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
        p=[0.65, 0.35]
    ),

    'Jam_Operasional': np.random.choice(
        [1, 2, 3],
        size=n_data,
        p=[0.25, 0.5, 0.25]
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

df_simulasi['No_Bulan'] = df_simulasi[
    'Tanggal'
].dt.month

df_simulasi['Bulan'] = df_simulasi[
    'No_Bulan'
].map(nama_bulan)

# ======================================================
# TARGET RAMAI / SEPI
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
        (df_simulasi['Hujan'] < 2)

        &

        (df_simulasi['Jam_Operasional'] == 2)
    )

).astype(int)

# ======================================================
# JUMLAH PENGUNJUNG
# ======================================================
jumlah_pengunjung = []

for ramai in df_simulasi['Target_Ramai']:

    if ramai == 1:

        pengunjung = np.random.randint(
            70,
            140
        )

    else:

        pengunjung = np.random.randint(
            20,
            70
        )

    jumlah_pengunjung.append(
        pengunjung
    )

df_simulasi[
    'Jumlah_Pengunjung'
] = jumlah_pengunjung

# ======================================================
# PENDAPATAN HARIAN
# ======================================================
pendapatan = []

for pengunjung in df_simulasi[
    'Jumlah_Pengunjung'
]:

    rata_belanja = np.random.randint(
        25000,
        40000
    )

    total = pengunjung * rata_belanja

    pendapatan.append(total)

df_simulasi[
    'Pendapatan_Harian'
] = pendapatan

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
# RANDOM FOREST MODEL
# ======================================================
model = RandomForestClassifier(

    n_estimators=150,

    max_depth=8,

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
    Tingkat Akurasi Prediksi AI:
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
# INPUT KOLOM 1
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
        max_value=30.0,
        value=float(live_rain)
    )

# ======================================================
# INPUT KOLOM 2
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
# INPUT KOLOM 3
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
# TOMBOL ANALISIS
# ======================================================
st.markdown("")

analisis = st.button(
    "🔍 Analisis AI Sekarang",
    use_container_width=True
)

# ======================================================
# HASIL ANALISIS AI
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

    st.subheader("🤖 Hasil Analisis Artificial Intelligence")

    # ==================================================
    # JIKA RAMAI
    # ==================================================
    if prediction == 1:

        estimasi_pengunjung = np.random.randint(
            80,
            140
        )

        rata_belanja = np.random.randint(
            28000,
            40000
        )

        estimasi_pendapatan = (
            estimasi_pengunjung *
            rata_belanja
        )

        st.error(
            f"""
            🔥 Café Diprediksi Akan RAMAI
            
            📌 Keyakinan AI:
            {persen_ramai:.2f}%
            
            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang
            
            💰 Estimasi Pendapatan:
            Rp {estimasi_pendapatan:,.0f}
            """
        )

        st.success("""
        ✅ Rekomendasi AI
        
        • Tambah stok bahan baku
        
        • Tambah pegawai
        
        • Siapkan meja tambahan
        
        • Aktifkan promo media sosial
        """)

    # ==================================================
    # JIKA SEPI
    # ==================================================
    else:

        estimasi_pengunjung = np.random.randint(
            20,
            70
        )

        rata_belanja = np.random.randint(
            25000,
            35000
        )

        estimasi_pendapatan = (
            estimasi_pengunjung *
            rata_belanja
        )

        st.success(
            f"""
            😌 Café Diprediksi Normal / Sepi
            
            📌 Keyakinan AI:
            {persen_sepi:.2f}%
            
            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang
            
            💰 Estimasi Pendapatan:
            Rp {estimasi_pendapatan:,.0f}
            """
        )

        st.info("""
        📌 Rekomendasi AI
        
        • Fokus promosi
        
        • Hemat operasional
        
        • Tingkatkan pelayanan
        
        • Buat event kecil café
        """)

    # ==================================================
    # PROGRESS BAR
    # ==================================================
    st.markdown("### 📊 Persentase Prediksi AI")

    st.write(
        f"🔥 Ramai : {persen_ramai:.2f}%"
    )

    st.progress(
        int(persen_ramai)
    )

    st.write(
        f"😌 Sepi : {persen_sepi:.2f}%"
    )

    st.progress(
        int(persen_sepi)
    )

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
# REKAP BULANAN
# ======================================================
laporan_bulanan = df_simulasi.groupby(
    ['No_Bulan', 'Bulan'],
    as_index=False
).agg({

    'Jumlah_Pengunjung': 'sum',

    'Pendapatan_Harian': 'sum',

    'Target_Ramai': 'sum',

    'Suhu': 'mean',

    'Hujan': 'mean'

})

laporan_bulanan = laporan_bulanan.sort_values(
    by='No_Bulan'
)

laporan_bulanan.columns = [

    'No_Bulan',

    'Bulan',

    'Total_Pengunjung',

    'Total_Pendapatan',

    'Total_Hari_Ramai',

    'Rata_Rata_Suhu',

    'Rata_Rata_Hujan'

]

# ======================================================
# TABS LAPORAN
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

        laporan_bulanan.style.hide(axis="index"),

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

        title='💰 Pendapatan Café Januari - April'

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

            'Pendapatan_Harian',

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
