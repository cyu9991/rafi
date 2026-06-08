# ☕ Smart Café Analytics AI

## 📌 Deskripsi Proyek

Smart Café Analytics AI adalah aplikasi berbasis **Streamlit** yang digunakan untuk menganalisis dan memprediksi tingkat kepadatan pengunjung Café Hans menggunakan algoritma **Machine Learning Random Forest**.

Sistem ini memanfaatkan beberapa faktor seperti:

- Suhu
- Kondisi cuaca
- Hari libur
- Program promo
- Shift operasional

untuk memprediksi apakah café akan ramai atau sepi, serta memberikan estimasi jumlah pengunjung dan pendapatan.

---

## 🎯 Tujuan

Membantu pemilik café dalam:

- Memprediksi tingkat keramaian pengunjung.
- Menganalisis faktor yang memengaruhi jumlah pengunjung.
- Mengestimasi pendapatan harian.
- Mendukung pengambilan keputusan operasional berbasis data.

---

## 🚀 Fitur Utama

### 🤖 Prediksi AI
- Prediksi kondisi café (Ramai / Sepi).
- Menggunakan algoritma Random Forest Classifier.
- Menampilkan tingkat keyakinan prediksi.
- Estimasi jumlah pengunjung.
- Estimasi pendapatan.

### 📊 Dashboard Analytics
- Total pengunjung.
- Total pendapatan.
- Jumlah hari ramai.
- Rata-rata pengunjung.
- Grafik faktor paling berpengaruh.
- Grafik tren pendapatan bulanan.
- Diagram distribusi pengunjung per shift.

### ☕ Menu Café
- Menampilkan daftar menu.
- Kategori menu.
- Harga menu.

### 📄 Laporan AI
- Classification Report.
- Confusion Matrix.
- Detail dataset café.

#🌡️ Integrasi Cuaca Real-Time
Mengambil data suhu terkini menggunakan API Open-Meteo.

---

## 🛠️ Teknologi yang Digunakan

| Teknologi | Fungsi |
|------------|---------|
| Python | Bahasa Pemrograman |
| Streamlit | Web Dashboard |
| Pandas | Pengolahan Data |
| NumPy | Manipulasi Data Numerik |
| Scikit-Learn | Machine Learning |
| Plotly | Visualisasi Data |
| Requests | Pengambilan Data API |

---

# 📂 Struktur Dataset

Dataset simulasi terdiri dari 180 data dengan atribut:

| Kolom | Keterangan |
|---------|------------|
| Tanggal | Tanggal Pengamatan |
| Suhu | Suhu Harian |
| Cuaca | Kategori Cuaca |
| Hari_Libur | Status Hari Libur |
| Promo | Status Promo |
| Shift | Shift Operasional |
| Score_Ramai | Nilai Keramaian |
| Ramai | Label Target |
| Jumlah_Pengunjung | Total Pengunjung |
| Pendapatan | Pendapatan Harian |

---

# 🧠 Algoritma Machine Learning

Model yang digunakan:

**Random Forest Classifier**

Parameter:

```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42
)
```

### Feature Input

```python
[
    'Suhu',
    'Cuaca',
    'Hari_Libur',
    'Promo',
    'Shift'
]
```

### Target

```python
Ramai
```

Keterangan:

- 1 = Ramai
- 0 = Sepi / Normal

---

## 📦 Instalasi

### Clone Repository

```bash
git clone https://github.com/username/smart-cafe-ai.git
```

### Masuk Folder Project

```bash
cd smart-cafe-ai
```

### Install Dependency

```bash
pip install -r requirements.txt
```

---

## ▶️ Menjalankan Aplikasi

```bash
streamlit run app.py
```

---

## 📋 Requirements

Buat file `requirements.txt`

```txt
streamlit
pandas
numpy
requests
plotly
scikit-learn
```

Install:

```bash
pip install -r requirements.txt
```

---

## 📊 Output Sistem

Sistem akan menghasilkan:

- Tingkat akurasi AI.
- Prediksi ramai atau sepi.
- Persentase keyakinan model.
- Estimasi jumlah pengunjung.
- Estimasi pendapatan.
- Dashboard visual interaktif.

---

🌐 Sumber Data Cuaca

Menggunakan API gratis:

https://open-meteo.com/

Endpoint:

```url
https://api.open-meteo.com/v1/forecast
```

---

# Identitas Pengembang

Nama : Rafi_Ahmad

NIM : F5212530108

Program Studi : Teknik Informatika

Universitas : Universitas Tadulako

---

# Lisensi

Proyek ini dibuat untuk keperluan pembelajaran, penelitian, dan pengembangan sistem prediksi pengunjung café berbasis Artificial Intelligence menggunakan Streamlit dan Random Forest.
