import re
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

stop_factory = StopWordRemoverFactory()
stopword_remover = stop_factory.create_stop_word_remover()

stem_factory = StemmerFactory()
stemmer = stem_factory.create_stemmer()

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'http\S+|www\S+|https\S+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    cleaned = clean_text(text)
    if not cleaned:
        return []
    return cleaned.split()

def remove_stopwords(text_or_tokens):
    if isinstance(text_or_tokens, list):
        text = " ".join(text_or_tokens)
    else:
        text = text_or_tokens
    filtered = stopword_remover.remove(text)
    return filtered

def stem_text(text_or_tokens):
    if isinstance(text_or_tokens, list):
        text = " ".join(text_or_tokens)
    else:
        text = text_or_tokens
    stemmed = stemmer.stem(text)
    return stemmed

def preprocess_document(text):
    cleaned = clean_text(text)
    without_stopwords = remove_stopwords(cleaned)
    stemmed = stem_text(without_stopwords)
    return stemmed

def get_preprocessing_stages(text):
    cleaned = clean_text(text)
    tokens = clean_text(text).split()
    without_stopwords = remove_stopwords(cleaned)
    stemmed = stem_text(without_stopwords)
    return {
        "original": text,
        "cleaned": cleaned,
        "tokens": tokens,
        "without_stopwords": without_stopwords,
        "stemmed": stemmed
    }
