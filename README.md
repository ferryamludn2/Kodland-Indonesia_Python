# Proyek Situs Web Kuis AI Dinamis

Sebuah aplikasi web interaktif yang dirancang untuk menguji pengetahuan pengguna tentang pengembangan Kecerdasan Buatan (AI) menggunakan Python. Proyek ini dibangun dengan Flask dan dirancang untuk audiens remaja, menggabungkan elemen gamifikasi seperti skor, papan peringkat, dan analisis performa.

Dibuat oleh: **Ferry Amaludin**

---

## Fitur Utama

*   **Sistem Autentikasi**: Pengguna dapat mendaftar, login, dan logout dengan aman. Kata sandi di-hash menggunakan bcrypt.
*   **Kuis Dinamis**: Pertanyaan disajikan secara acak dari database, memastikan pengalaman yang berbeda setiap kali bermain.
*   **Sistem Skor Sesi**: Skor dihitung per sesi kuis. Skor tertinggi yang pernah dicapai akan disimpan di papan peringkat.
*   **Mekanisme Streak**: Pengguna mendapatkan poin bonus untuk setiap jawaban benar yang beruntun, menambah elemen tantangan.
*   **Papan Peringkat (Leaderboard)**: Menampilkan peringkat pengguna berdasarkan skor tertinggi mereka.
*   **Halaman Hasil Interaktif**: Setelah menyelesaikan sesi, pengguna disajikan halaman hasil dengan skor akhir, total waktu, dan animasi perayaan.
*   **Widget Cuaca**: Halaman beranda dilengkapi dengan widget ramalan cuaca dinamis yang mengambil data dari API publik.

## Teknologi yang Digunakan

*   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login
*   **Database**: SQLite
*   **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
*   **API Eksternal**: Open-Meteo (untuk data cuaca)
*   **Library Lainnya**:
    *   `requests` untuk melakukan panggilan API.
    *   `bcrypt` untuk hashing kata sandi.
    *   `canvas-confetti` untuk animasi di halaman hasil.

## Panduan Instalasi dan Menjalankan Proyek Secara Lokal

Ikuti langkah-langkah berikut untuk menjalankan proyek ini di komputer Anda.

### 1. Clone Repositori

Buka terminal Anda dan clone repositori ini ke direktori lokal.

```bash
git clone https://github.com/ferryamludn2/Kodland-Indonesia_Python.git
```

### 2. Buat dan Aktifkan Virtual Environment

Sangat disarankan untuk menggunakan virtual environment untuk mengisolasi dependensi proyek.

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan di Windows
venv\Scripts\activate

# Aktifkan di macOS/Linux
source venv/bin/activate
```

### 3. Instal Dependensi

Instal semua library yang dibutuhkan menggunakan file `requirements.txt` yang telah disediakan.

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi

Setelah semua dependensi terinstal, jalankan aplikasi Flask.

```bash
python app.py
```

Aplikasi akan berjalan secara default di `http://127.0.0.1:5000`. Buka alamat tersebut di browser Anda.

**Catatan Penting**: Saat pertama kali menjalankan aplikasi, file database `instance/quiz.db` akan dibuat secara otomatis. Jika Anda melakukan perubahan pada model database (file `models.py`), Anda mungkin perlu menghapus file `instance/quiz.db` dan menjalankan ulang aplikasi agar skema baru dapat dibuat.

---

## Tentang Penulis

Proyek ini dikembangkan oleh **Ferry Amaludin** sebagai demonstrasi keahlian dalam pengembangan web full-stack menggunakan Python dan ekosistemnya.