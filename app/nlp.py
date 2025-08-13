# app/nlp.py
# Preprocesado con spaCy y embeddings con SentenceTransformers
import spacy
from sentence_transformers import SentenceTransformer

nlp = spacy.load('es_core_news_sm')
EMB_MODEL = None

def load_embedding_model(name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
    global EMB_MODEL
    if EMB_MODEL is None:
        EMB_MODEL = SentenceTransformer(name)
    return EMB_MODEL

def preprocess(text: str) -> str:
    doc = nlp(text.lower())
    tokens = [t.lemma_ for t in doc if t.is_alpha and not t.is_stop]
    return ' '.join(tokens)

def embed_text(text: str):
    m = load_embedding_model()
    vec = m.encode([text])[0]
    return vec