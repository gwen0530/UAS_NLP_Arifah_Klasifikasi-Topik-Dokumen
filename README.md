# Document Topic Classification System

Aplikasi web berbasis Machine Learning untuk mengklasifikasikan topik dokumen teks Bahasa Indonesia menggunakan Logistic Regression, TF-IDF, dan Sastrawi NLP.

## Cara Menjalankan

```bash
pip install -r requirements.txt
python app.py
```

Buka browser: http://localhost:5000

## Struktur Folder

```
document-topic-classification/
├── app.py
├── requirements.txt
├── config.py
├── database.db
├── model/
│   ├── model.pkl
│   └── tfidf.pkl
├── dataset/
│   └── dataset.csv
├── uploads/
├── static/
│   ├── css/style.css
│   └── js/app.js
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── dataset.html
│   ├── training.html
│   ├── testing.html
│   ├── evaluation.html
│   ├── visualization.html
│   └── documentation.html
├── src/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── training.py
│   ├── prediction.py
│   ├── evaluation.py
│   └── visualization.py
└── utils/
    ├── __init__.py
    └── helper.py
```

## Alur Penggunaan

1. Jalankan aplikasi: `python app.py`
2. Buka halaman **Dataset** → upload file CSV (kolom: `text`, `label`)
3. Buka halaman **Training Model** → klik "Mulai Training Model"
4. Buka halaman **Testing** → masukkan teks Bahasa Indonesia → klik "Prediksi"
5. Lihat performa di halaman **Evaluasi** (Accuracy, Precision, Recall, F1, Confusion Matrix)
6. Eksplorasi grafik di halaman **Visualisasi**
7. Export laporan ke **PDF** atau **Excel**

## Kategori Topik

| Kategori   | Keterangan                     |
|------------|-------------------------------|
| Teknologi  | Berita teknologi & inovasi    |
| Pendidikan | Sistem dan kebijakan edukasi  |
| Kesehatan  | Kesehatan masyarakat & medis  |
| Politik    | Pemerintahan & demokrasi      |
| Ekonomi    | Keuangan, pasar & perdagangan |
| Olahraga   | Turnamen & kompetisi olahraga |
| Hiburan    | Film, musik & seni budaya     |

## NLP Pipeline

```
Input Teks
   → Text Cleaning (lowercase, remove HTML/angka/simbol/tanda baca)
   → Tokenizing
   → Stopword Removal (Sastrawi)
   → Stemming Bahasa Indonesia (Sastrawi ECS)
   → TF-IDF Vectorization (max_features=2500, ngram_range=(1,2))
   → Logistic Regression Prediction
   → Probabilitas & Confidence Score
```

## Library

- Flask 3.0.2
- Pandas 2.2.1
- NumPy 1.26.4
- Scikit-learn 1.4.1
- Sastrawi 1.0.1
- NLTK 3.8.1
- Joblib 1.3.2
- Matplotlib 3.8.3
- Seaborn 0.13.2
- Plotly 5.19.0
- Chart.js (CDN)
- Bootstrap 5.3.2 (CDN)
- OpenPyXL 3.1.2
- ReportLab 4.1.0

## Fitur Aplikasi

- Dashboard dengan 4 KPI Card dan chart interaktif
- DataTable dataset dengan search, sort, pagination
- Upload CSV dataset langsung dari UI
- Pipeline NLP visualisasi Before vs After preprocessing
- Progress training step-by-step
- Prediksi single-document dengan confidence score & probability bar
- Evaluasi model: Accuracy, Precision, Recall, F1, Confusion Matrix, Classification Report
- 7 jenis chart visualisasi menggunakan Chart.js
- Export laporan evaluasi ke PDF (ReportLab)
- Export riwayat prediksi ke Excel (OpenPyXL)
- Dark Mode toggle
- Toast notifications & loading animation
- Breadcrumb navigasi
- Scroll to top button
- Responsive mobile layout

## Teknologi

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML5, Bootstrap 5, Chart.js, Bootstrap Icons
- **Machine Learning**: Scikit-learn (Logistic Regression, TF-IDF)
- **NLP**: Sastrawi (Indonesian Stemmer & Stopword Remover)
- **Model Serialization**: Joblib

---

Proyek UAS Mata Kuliah Natural Language Processing (NLP)
