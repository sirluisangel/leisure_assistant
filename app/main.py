from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import os
import json

# Importar módulos internos
from .nlp import preprocess, embed_text
from .emotion_net import EmotionNet, load_model_state, model_infer
from .generator import generate_recommendation

# Inicializar FastAPI
app = FastAPI(title="Leisure Assistant PRO - AI Coach")

# --------------------- RUTAS Y CONFIG ---------------------

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_PATH = os.path.join(DATA_DIR, 'emotion_model.pth')
DATA_HISTORY = os.path.join(DATA_DIR, 'history.json')

# Crear carpetas/archivos necesarios
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(DATA_HISTORY):
    with open(DATA_HISTORY, 'w', encoding='utf-8') as f:
        json.dump([], f)

# Montar carpeta estática
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

# --------------------- MODELO DE EMOCIONES ---------------------

# Cargar modelo de emociones entrenado
model = EmotionNet()
if os.path.exists(MODEL_PATH):
    load_model_state(model, MODEL_PATH)

# --------------------- MODELOS DE PETICIÓN ---------------------

class FeelingRequest(BaseModel):
    text: str

# --------------------- FUNCIONES AUXILIARES ---------------------

def cargar_historial():
    with open(DATA_HISTORY, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_historial(historial):
    with open(DATA_HISTORY, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

# --------------------- RUTAS ---------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    """Página principal (HTML)"""
    index_path = os.path.join(STATIC_DIR, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.post("/analyze")
async def analyze(req: FeelingRequest):
    """Analiza el texto del usuario y predice su emoción"""
    clean_text = preprocess(req.text)
    vec = embed_text(clean_text)
    emotion, confidence = model_infer(model, vec)
    return JSONResponse({
        "emotion": emotion,
        "confidence": confidence
    })

@app.post("/recommend")
async def recommend(request: Request):
    """Genera recomendaciones personalizadas y guarda en historial"""
    try:
        payload = await request.json()
        user_text = payload.get('feeling_text', '').strip()
        detected_emotion = payload.get('detected_emotion', 'Desconocida').strip()
        history_context = payload.get('history', '').strip()

        prompt_context = {
            'text': user_text,
            'emotion': detected_emotion,
            'history': history_context
        }

        resultado = generate_recommendation(prompt_context)

        # Cargar y actualizar historial
        historial = cargar_historial()
        historial.append({
            "fecha": datetime.now().isoformat(),
            "texto": user_text,
            "emocion": detected_emotion,
            "recomendacion": resultado.get("recomendacion") or "Sin recomendación"
        })
        guardar_historial(historial)

        return JSONResponse({
            "recommendation": resultado.get("recomendacion") or "Sin recomendación",
            "error": resultado.get("error")
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Ocurrió un error al generar la recomendación: {str(e)}"}
        )

@app.get("/history")
async def history():
    """Devuelve el historial de análisis previos"""
    try:
        historial = cargar_historial()
        return JSONResponse(content=historial)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"No se pudo cargar el historial: {str(e)}"}
        )
    
@app.get('/history-view', response_class=HTMLResponse)
async def history_page():
    """Devuelve la página de historial como HTML"""
    history_path = os.path.join(STATIC_DIR, 'history.html')
    with open(history_path, 'r', encoding='utf-8') as f:
        return f.read()