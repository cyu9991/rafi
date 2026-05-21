# ======================================================
# INPUT USER
# ======================================================
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
# TOMBOL ANALISIS AI
# ======================================================
st.markdown("")

analisis = st.button(
    "🔍 Analisis AI Sekarang",
    use_container_width=True
)

# ======================================================
# JALANKAN ANALISIS
# ======================================================
if analisis:

    # ==================================================
    # DATA INPUT USER
    # ==================================================
    current_data = pd.DataFrame([[
        input_suhu,
        input_hujan,
        input_libur,
        input_promo,
        input_jam
    ]], columns=feature_cols)

    # ==================================================
    # PREDIKSI AI
    # ==================================================
    prediction = model.predict(
        current_data
    )[0]

    # ==================================================
    # PROBABILITAS AI
    # ==================================================
    probability = model.predict_proba(
        current_data
    )[0]

    persen_sepi = probability[0] * 100

    persen_ramai = probability[1] * 100

    # ==================================================
    # HEADER HASIL
    # ==================================================
    st.markdown("---")

    st.subheader("🤖 Hasil Analisis AI")

    # ==================================================
    # HASIL RAMAI
    # ==================================================
    if prediction == 1:

        estimasi_pengunjung = np.random.randint(
            80,
            140
        )

        estimasi_pendapatan = (
            estimasi_pengunjung *
            np.random.randint(28000, 40000)
        )

        st.error(
            f"""
            🔥 Café Diprediksi Akan RAMAI
            
            📌 Tingkat Keyakinan AI:
            {persen_ramai:.2f}%
            
            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang
            
            💰 Estimasi Pendapatan:
            Rp {estimasi_pendapatan:,.0f}
            """
        )

        st.success("""
        ✅ Rekomendasi AI:
        
        • Tambah stok bahan baku
        
        • Tambah pegawai shift
        
        • Siapkan meja tambahan
        
        • Aktifkan promo digital
        """)

    # ==================================================
    # HASIL SEPI
    # ==================================================
    else:

        estimasi_pengunjung = np.random.randint(
            20,
            70
        )

        estimasi_pendapatan = (
            estimasi_pengunjung *
            np.random.randint(25000, 35000)
        )

        st.success(
            f"""
            😌 Café Diprediksi Normal / Sepi
            
            📌 Tingkat Keyakinan AI:
            {persen_sepi:.2f}%
            
            👥 Estimasi Pengunjung:
            {estimasi_pengunjung} Orang
            
            💰 Estimasi Pendapatan:
            Rp {estimasi_pendapatan:,.0f}
            """
        )

        st.info("""
        📌 Rekomendasi AI:
        
        • Fokus promosi
        
        • Hemat operasional
        
        • Tingkatkan pelayanan
        
        • Buat event kecil café
        """)

    # ==================================================
    # PROGRESS BAR AI
    # ==================================================
    st.markdown("### 📊 Tingkat Prediksi AI")

    st.write(
        f"Ramai : {persen_ramai:.2f}%"
    )

    st.progress(
        int(persen_ramai)
    )

    st.write(
        f"Sepi : {persen_sepi:.2f}%"
    )

    st.progress(
        int(persen_sepi)
    )
