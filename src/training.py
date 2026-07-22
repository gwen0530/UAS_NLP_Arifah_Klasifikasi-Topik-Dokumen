import os
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from config import MODEL_DIR, MODEL_PATH, TFIDF_PATH
from src.preprocessing import preprocess_document
from utils.helper import get_db, log_activity

def train_model():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT text, label FROM Dataset')
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise ValueError("Dataset kosong. Silakan upload atau isi dataset terlebih dahulu.")
        
    df = pd.DataFrame(rows, columns=['text', 'label'])
    dataset_size = len(df)
    
    df['clean_text'] = df['text'].apply(preprocess_document)
    
    vectorizer = TfidfVectorizer(max_features=2500, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df['clean_text'])
    y = df['label']
    
    if len(df) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if len(y.unique()) > 1 else None
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y
        
    model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average='weighted', zero_division=0
    )
    
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, TFIDF_PATH)
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO TrainingHistory (accuracy, precision, recall, f1_score, dataset_size) VALUES (?, ?, ?, ?, ?)',
        (float(accuracy), float(precision), float(recall), float(f1), dataset_size)
    )
    conn.commit()
    conn.close()
    
    log_activity("Train Model", f"Akurasi: {accuracy:.4f}, Data: {dataset_size}")
    
    return {
        "status": "success",
        "dataset_size": dataset_size,
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "classes": list(model.classes_)
    }
