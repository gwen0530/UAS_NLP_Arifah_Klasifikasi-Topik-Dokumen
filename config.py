import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "document-topic-classification-secret-key"
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
TFIDF_PATH = os.path.join(MODEL_DIR, "tfidf.pkl")
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
DEFAULT_DATASET_PATH = os.path.join(DATASET_DIR, "dataset.csv")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"csv"}

CATEGORIES = [
    "Teknologi",
    "Pendidikan",
    "Kesehatan",
    "Politik",
    "Ekonomi",
    "Olahraga",
    "Hiburan"
]

COLOR_PALETTE = {
    "primary": "#F59E0B",
    "secondary": "#FDBA74",
    "background": "#FFF7ED",
    "card": "#FFFFFF",
    "sidebar": "#FFEDD5",
    "hover": "#FB923C",
    "text": "#444444",
    "border": "#FED7AA"
}
