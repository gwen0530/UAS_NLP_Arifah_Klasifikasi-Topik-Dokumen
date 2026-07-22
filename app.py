import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from config import SECRET_KEY, UPLOAD_DIR, ALLOWED_EXTENSIONS, CATEGORIES, COLOR_PALETTE
from utils.helper import init_db, get_db, log_activity, export_predictions_to_excel
from src.preprocessing import get_preprocessing_stages
from src.training import train_model
from src.prediction import predict_text, is_model_available
from src.evaluation import evaluate_model, generate_pdf_report
from src.visualization import get_visualization_data

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM Dataset')
    total_dataset = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(DISTINCT label) as total FROM Dataset')
    total_categories = cursor.fetchone()['total']
    
    cursor.execute('SELECT accuracy FROM TrainingHistory ORDER BY id DESC LIMIT 1')
    row_train = cursor.fetchone()
    model_accuracy = round(row_train['accuracy'] * 100, 2) if row_train else 0.0
    
    cursor.execute('SELECT COUNT(*) as total FROM PredictionHistory')
    total_predictions = cursor.fetchone()['total']
    
    cursor.execute('SELECT label, COUNT(*) as count FROM Dataset GROUP BY label')
    dist_rows = cursor.fetchall()
    class_distribution = {r['label']: r['count'] for r in dist_rows}
    
    cursor.execute('SELECT id, text, predicted_label, confidence, execution_time, created_at FROM PredictionHistory ORDER BY id DESC LIMIT 5')
    recent_predictions = cursor.fetchall()
    
    eval_metrics = evaluate_model()
    
    conn.close()
    
    model_status = "Tersedia" if is_model_available() else "Belum Dilatih"
    
    return render_template(
        'dashboard.html',
        total_dataset=total_dataset,
        total_categories=total_categories,
        model_accuracy=model_accuracy,
        total_predictions=total_predictions,
        class_distribution=class_distribution,
        recent_predictions=recent_predictions,
        eval_metrics=eval_metrics,
        model_status=model_status,
        palette=COLOR_PALETTE
    )

@app.route('/dataset')
def dataset_page():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Dataset ORDER BY id DESC')
    items = cursor.fetchall()
    
    cursor.execute('SELECT COUNT(*) as total FROM Dataset')
    total_dataset = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(DISTINCT label) as total FROM Dataset')
    total_categories = cursor.fetchone()['total']
    
    cursor.execute('SELECT label, COUNT(*) as count FROM Dataset GROUP BY label')
    label_dist = {r['label']: r['count'] for r in cursor.fetchall()}
    
    cursor.execute('SELECT AVG(length) as avg_len FROM Dataset')
    avg_len_row = cursor.fetchone()
    avg_length = round(avg_len_row['avg_len'] or 0, 1)
    
    conn.close()
    
    model_status = "Tersedia" if is_model_available() else "Belum Dilatih"
    
    return render_template(
        'dataset.html',
        dataset=items,
        total_dataset=total_dataset,
        total_categories=total_categories,
        label_dist=label_dist,
        avg_length=avg_length,
        categories=CATEGORIES,
        model_status=model_status
    )

@app.route('/api/dataset/upload', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "File tidak ditemukan dalam request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Pilih file CSV terlebih dahulu"}), 400
        
    if file and allowed_file(file.filename):
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
            
        filepath = os.path.join(UPLOAD_DIR, file.filename)
        file.save(filepath)
        
        try:
            df = pd.read_csv(filepath)
            if 'text' not in df.columns or 'label' not in df.columns:
                return jsonify({"status": "error", "message": "CSV harus memiliki kolom 'text' dan 'label'"}), 400
                
            conn = get_db()
            cursor = conn.cursor()
            inserted_count = 0
            for _, r in df.iterrows():
                txt = str(r['text']).strip()
                lbl = str(r['label']).strip()
                if txt and lbl:
                    cursor.execute(
                        'INSERT INTO Dataset (text, label, length, word_count) VALUES (?, ?, ?, ?)',
                        (txt, lbl, len(txt), len(txt.split()))
                    )
                    inserted_count += 1
            conn.commit()
            conn.close()
            
            log_activity("Upload Dataset", f"Mengunggah {inserted_count} baris data dari {file.filename}")
            return jsonify({"status": "success", "message": f"Berhasil mengimpor {inserted_count} data baru."})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Gagal membaca CSV: {str(e)}"}), 500
            
    return jsonify({"status": "error", "message": "Ekstensi file harus .csv"}), 400

@app.route('/api/dataset/add', methods=['POST'])
def add_dataset_item():
    data = request.form
    txt = data.get('text', '').strip()
    lbl = data.get('label', '').strip()
    
    if not txt or not lbl:
        return jsonify({"status": "error", "message": "Teks dan label wajib diisi"}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Dataset (text, label, length, word_count) VALUES (?, ?, ?, ?)',
        (txt, lbl, len(txt), len(txt.split()))
    )
    conn.commit()
    conn.close()
    
    log_activity("Tambah Dataset Manual", f"Label: {lbl}")
    return jsonify({"status": "success", "message": "Data berhasil ditambahkan."})

@app.route('/api/dataset/delete/<int:item_id>', methods=['POST'])
def delete_dataset_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Dataset WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    log_activity("Hapus Dataset", f"ID: {item_id}")
    return jsonify({"status": "success", "message": "Data berhasil dihapus."})

@app.route('/training')
def training_page():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT text, label FROM Dataset LIMIT 3')
    sample_rows = cursor.fetchall()
    conn.close()
    
    preprocessing_samples = []
    for r in sample_rows:
        stages = get_preprocessing_stages(r['text'])
        stages['label'] = r['label']
        preprocessing_samples.append(stages)
        
    model_status = "Tersedia" if is_model_available() else "Belum Dilatih"
    
    return render_template(
        'training.html',
        samples=preprocessing_samples,
        model_status=model_status
    )

@app.route('/api/training/run', methods=['POST'])
def run_training():
    try:
        res = train_model()
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/testing')
def testing_page():
    model_status = "Tersedia" if is_model_available() else "Belum Dilatih"
    return render_template('testing.html', model_status=model_status)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.json or request.form
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({"status": "error", "message": "Silakan masukkan teks dokumen yang ingin diprediksi."}), 400
        
    if not is_model_available():
        return jsonify({"status": "error", "message": "Model belum tersedia. Silakan lakukan training terlebih dahulu."}), 400
        
    try:
        res = predict_text(text)
        res['status'] = 'success'
        return jsonify(res)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/evaluation')
def evaluation_page():
    eval_data = evaluate_model()
    model_status = "Tersedia" if is_model_available() else "Belum Dilatih"
    return render_template('evaluation.html', eval_data=eval_data, model_status=model_status)

@app.route('/visualization')
def visualization_page():
    model_status = "Tersedia" if is_model_available() else "Belum Dilatih"
    return render_template('visualization.html', model_status=model_status)

@app.route('/api/visualization/data')
def api_visualization_data():
    data = get_visualization_data()
    return jsonify(data)

@app.route('/documentation')
def documentation_page():
    import sys
    import flask
    model_status = "Tersedia" if is_model_available() else "Belum Dilatih"
    return render_template(
        'documentation.html',
        python_version=sys.version.split()[0],
        flask_version=flask.__version__,
        model_status=model_status
    )

@app.route('/api/export/pdf')
def export_pdf():
    try:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'laporan_evaluasi.pdf')
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        generate_pdf_report(pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name='Laporan_Evaluasi_Model.pdf')
    except Exception as e:
        flash(f"Gagal mengekspor PDF: {str(e)}", "danger")
        return redirect(url_for('evaluation_page'))

@app.route('/api/export/excel')
def export_excel():
    try:
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'riwayat_prediksi.xlsx')
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        export_predictions_to_excel(excel_path)
        return send_file(excel_path, as_attachment=True, download_name='Riwayat_Prediksi.xlsx')
    except Exception as e:
        flash(f"Gagal mengekspor Excel: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
