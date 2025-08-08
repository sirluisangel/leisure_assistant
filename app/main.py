from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
from .nlp import preprocess, embed_text
from .emotion_net import EmotionNet, EMOTIONS, load_model_state, model_infer
from .generator import generate_recommendation

app = FastAPI(title='Leisure Assistant PRO - AI Coach')

# Definir rutas base y estáticas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dos niveles arriba de app/main.py
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Montar carpeta estática para servir archivos estáticos
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

# Ruta al modelo y carga
MODEL_PATH = os.path.join('data', 'emotion_model.pth')
model = EmotionNet()
if os.path.exists(MODEL_PATH):
    load_model_state(model, MODEL_PATH)

# Archivo para historial
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_HISTORY = os.path.join(DATA_DIR, 'history.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(DATA_HISTORY):
    with open(DATA_HISTORY, 'w', encoding='utf-8') as f:
        json.dump([], f)

# Pydantic para request body en /analyze
class FeelingRequest(BaseModel):
    text: str

# Ruta principal que devuelve el index.html
@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = os.path.join(STATIC_DIR, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return html_content

# Ruta para analizar sentimiento
@app.post('/analyze')
async def analyze(req: FeelingRequest):
    text = req.text
    clean = preprocess(text)
    vec = embed_text(clean)
    emotion, conf = model_infer(model, vec)
    return JSONResponse({'emotion': emotion, 'confidence': conf})

# Ruta para recomendar según sentimiento
@app.post('/recommend')
async def recommend(request: Request):
    payload = await request.json()
    user_text = payload.get('feeling_text', '')
    detected_emotion = payload.get('detected_emotion', 'Unknown')
    history_context = payload.get('history', '')

    prompt_context = {
        'text': user_text,
        'emotion': detected_emotion,
        'history': history_context
    }

    rec = generate_recommendation(prompt_context)

    # Guardar historial
    with open(DATA_HISTORY, 'r', encoding='utf-8') as f:
        hist = json.load(f)
    hist.append({
        'fecha': __import__('datetime').datetime.now().isoformat(),
        'texto': user_text,
        'emocion': detected_emotion,
        'recomendacion': rec
    })
    with open(DATA_HISTORY, 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

    return JSONResponse({'recommendation': rec})

# Ruta para obtener historial
@app.get('/history')
async def history():
    with open(DATA_HISTORY, 'r', encoding='utf-8') as f:
        return JSONResponse(json.load(f))
