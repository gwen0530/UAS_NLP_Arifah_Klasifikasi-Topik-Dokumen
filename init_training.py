import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helper import init_db, log_activity
from src.training import train_model

print("Initializing database...")
init_db()
print("Database initialized.")

print("Starting model training...")
result = train_model()
print(f"Training complete!")
print(f"  Accuracy  : {result['accuracy']*100:.2f}%")
print(f"  Precision : {result['precision']*100:.2f}%")
print(f"  Recall    : {result['recall']*100:.2f}%")
print(f"  F1-Score  : {result['f1_score']*100:.2f}%")
print(f"  Dataset   : {result['dataset_size']} records")
print(f"  Classes   : {result['classes']}")
print("Model saved to model/model.pkl and model/tfidf.pkl")
