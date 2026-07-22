import pandas as pd
import numpy as np
import json
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from utils.helper import get_db
from src.preprocessing import clean_text, remove_stopwords, stem_text

def get_visualization_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT text, label FROM Dataset')
    rows = cursor.fetchall()
    
    df = pd.DataFrame(rows, columns=['text', 'label']) if rows else pd.DataFrame(columns=['text', 'label'])
    
    class_dist = {}
    if not df.empty:
        counts = df['label'].value_counts()
        class_dist = counts.to_dict()
        
    word_freq_by_category = {}
    all_words = []
    
    if not df.empty:
        for cat in df['label'].unique():
            cat_texts = df[df['label'] == cat]['text']
            combined = " ".join([stem_text(remove_stopwords(clean_text(t))) for t in cat_texts])
            words = combined.split()
            all_words.extend(words)
            counter = Counter(words)
            word_freq_by_category[cat] = dict(counter.most_common(10))
            
    overall_word_freq = dict(Counter(all_words).most_common(20))
    
    cursor.execute('SELECT id, predicted_label, confidence, created_at FROM PredictionHistory ORDER BY id DESC LIMIT 50')
    pred_rows = cursor.fetchall()
    
    pred_history = [
        {
            "id": r['id'],
            "label": r['predicted_label'],
            "confidence": round(r['confidence'] * 100, 2),
            "created_at": r['created_at']
        }
        for r in pred_rows
    ]
    
    cursor.execute('SELECT accuracy, precision, recall, f1_score, dataset_size, trained_at FROM TrainingHistory ORDER BY id DESC LIMIT 10')
    train_rows = cursor.fetchall()
    
    training_results = [
        {
            "accuracy": round(r['accuracy'] * 100, 2),
            "precision": round(r['precision'] * 100, 2),
            "recall": round(r['recall'] * 100, 2),
            "f1_score": round(r['f1_score'] * 100, 2),
            "dataset_size": r['dataset_size'],
            "trained_at": r['trained_at']
        }
        for r in train_rows
    ]
    
    conn.close()
    
    return {
        "class_distribution": class_dist,
        "word_freq_by_category": word_freq_by_category,
        "overall_word_freq": overall_word_freq,
        "prediction_history": pred_history,
        "training_results": training_results
    }
