# ======================================================
# DETAIL DATA HARIAN + FILTER SHIFT
# ======================================================
st.markdown("---")

st.subheader("📅 Detail Data Harian")

# ==========================================
# MEMBUAT DATA DETAIL SHIFT
# ==========================================
detail_shift = []

for i in range(len(df_simulasi)):

    tanggal = df_simulasi.loc[i, 'Tanggal']
    bulan = df_simulasi.loc[i, 'Bulan']
    suhu = df_simulasi.loc[i, 'Suhu']
    hujan = df_simulasi.loc[i, 'Hujan']
    libur = df_simulasi.loc[i, 'Hari_Libur']
    promo = df_simulasi.loc[i, 'Ada_Promo']

    for shift in [1, 2, 3]:

        # ==========================================
        # PENGUNJUNG BERBEDA TIAP SHIFT
        # ==========================================
        if shift == 1:
            pengunjung = np.random.randint(8, 25)

        elif shift == 2:
            pengunjung = np.random.randint(20, 45)

        else:
            pengunjung = np.random.randint(10, 30)

        # Hari libur tambah pengunjung
        if libur == 1:
            pengunjung += 8

        # Promo tambah pengunjung
        if promo == 1:
            pengunjung += 5

        # Hujan besar kurangi pengunjung
        if hujan > 7:
            pengunjung -= 5

        pengunjung = max(pengunjung, 5)

        # ==========================================
        # PENDAPATAN
        # ==========================================
        rata_belanja = np.random.randint(
            12000,
            18000
        )

        pendapatan = pengunjung * rata_belanja

        # ==========================================
        # SIMPAN DATA
        # ==========================================
        detail_shift.append({

            'Tanggal': tanggal,
            'Bulan': bulan,
            'Shift': f"Shift {shift}",
            'Suhu °C': suhu,
            'Hujan mm': hujan,
            'Hari Libur':
            "Ya" if libur == 1 else "Tidak",

            'Promo':
            "Ya" if promo == 1 else "Tidak",

            'Pengunjung': pengunjung,

            'Pendapatan':
            f"Rp {pendapatan:,}".replace(",", ".")

        })

# ==========================================
# DATAFRAME DETAIL
# ==========================================
df_detail_shift = pd.DataFrame(detail_shift)

# ==========================================
# FILTER BULAN
# ==========================================
bulan_pilih = st.selectbox(

    "Pilih Bulan",

    df_detail_shift['Bulan']
    .unique()

)

# ==========================================
# FILTER SHIFT
# ==========================================
shift_pilih = st.selectbox(

    "Pilih Shift",

    ['Shift 1', 'Shift 2', 'Shift 3']

)

# ==========================================
# FILTER DATA
# ==========================================
hasil_filter = df_detail_shift[

    (df_detail_shift['Bulan'] == bulan_pilih)

    &

    (df_detail_shift['Shift'] == shift_pilih)

]

# ==========================================
# TAMPILKAN DATA
# ==========================================
st.dataframe(

    hasil_filter,

    use_container_width=True,

    hide_index=True

)
