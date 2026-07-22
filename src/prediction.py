import os
import time
import json
import joblib
from config import MODEL_PATH, TFIDF_PATH, CATEGORIES
from src.preprocessing import preprocess_document
from utils.helper import get_db, log_activity

def is_model_available():
    return os.path.exists(MODEL_PATH) and os.path.exists(TFIDF_PATH)

def predict_text(text):
    if not text or not str(text).strip():
        raise ValueError("Teks input tidak boleh kosong.")
        
    if not is_model_available():
        raise FileNotFoundError("Model belum tersedia. Silakan lakukan training terlebih dahulu.")
        
    start_time = time.time()
    
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(TFIDF_PATH)
    
    processed_text = preprocess_document(text)
    vectorized_text = vectorizer.transform([processed_text])
    
    probabilities = model.predict_proba(vectorized_text)[0]
    classes = model.classes_
    
    prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
    for cat in CATEGORIES:
        if cat not in prob_dict:
            prob_dict[cat] = 0.0
            
    top_pred = max(prob_dict, key=prob_dict.get)
    confidence = float(prob_dict[top_pred])
    
    exec_time = time.time() - start_time
    
    prob_json = json.dumps(prob_dict)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO PredictionHistory (text, predicted_label, confidence, probability_json, execution_time) VALUES (?, ?, ?, ?, ?)',
        (text, top_pred, confidence, prob_json, exec_time)
    )
    conn.commit()
    conn.close()
    
    log_activity("Prediction", f"Label: {top_pred}, Confidence: {confidence:.2%}")
    
    return {
        "text": text,
        "processed_text": processed_text,
        "top_prediction": top_pred,
        "category": top_pred,
        "confidence": confidence,
        "confidence_percentage": round(confidence * 100, 2),
        "probabilities": prob_dict,
        "execution_time": round(exec_time, 4)
    }
