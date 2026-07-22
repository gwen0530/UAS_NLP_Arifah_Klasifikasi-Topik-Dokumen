import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report
)
from config import MODEL_PATH, TFIDF_PATH, CATEGORIES
from src.preprocessing import preprocess_document
from utils.helper import get_db

def evaluate_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(TFIDF_PATH):
        return None
        
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(TFIDF_PATH)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT text, label FROM Dataset')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return None
        
    df = pd.DataFrame(rows, columns=['text', 'label'])
    df['clean_text'] = df['text'].apply(preprocess_document)
    
    X = vectorizer.transform(df['clean_text'])
    y_true = df['label']
    
    y_pred = model.predict(X)
    
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    
    report_dict = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    
    labels = list(model.classes_)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    return {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "labels": labels,
        "confusion_matrix": cm.tolist(),
        "classification_report": report_dict,
        "total_samples": len(df)
    }

def generate_pdf_report(output_path):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    metrics = evaluate_model()
    if not metrics:
        raise ValueError("Model belum dievaluasi atau dataset kosong.")
        
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#F59E0B'),
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#444444'),
        spaceBefore=10,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    story.append(Paragraph("Laporan Evaluasi Model NLP Document Topic Classification", title_style))
    story.append(Paragraph("Sistem Klasifikasi Topik Dokumen Bahasa Indonesia dengan Logistic Regression & TF-IDF", normal_style))
    story.append(Spacer(1, 15))
    
    summary_data = [
        ["Metrik", "Nilai"],
        ["Total Dataset", str(metrics["total_samples"])],
        ["Accuracy", f"{metrics['accuracy']*100:.2f}%"],
        ["Precision (Weighted)", f"{metrics['precision']*100:.2f}%"],
        ["Recall (Weighted)", f"{metrics['recall']*100:.2f}%"],
        ["F1-Score (Weighted)", f"{metrics['f1_score']*100:.2f}%"]
    ]
    
    t_summary = Table(summary_data, colWidths=[200, 200])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F59E0B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFF7ED')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#FED7AA'))
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Detail Classification Report", heading_style))
    report_table_data = [["Kategori / Metrik", "Precision", "Recall", "F1-Score", "Support"]]
    
    rep = metrics["classification_report"]
    for key, val in rep.items():
        if isinstance(val, dict):
            report_table_data.append([
                key,
                f"{val.get('precision', 0):.4f}",
                f"{val.get('recall', 0):.4f}",
                f"{val.get('f1-score', 0):.4f}",
                str(val.get('support', 0))
            ])
            
    t_report = Table(report_table_data, colWidths=[150, 80, 80, 80, 80])
    t_report.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FDBA74')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#444444')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#FED7AA'))
    ]))
    story.append(t_report)
    
    doc.build(story)
    return output_path
