from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from google import genai
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import os, json
from functools import lru_cache
from transformers import pipeline

# Importar módulos internos
from .nlp import preprocess, embed_text
from .generator import generate_recommendation
from fastapi.templating import Jinja2Templates

# Inicializar FastAPI
app = FastAPI(title="Leisure Assistant PRO - AI Coach")

# Reemplaza con la URL de la API de Gemini (según la documentación)
GEMINI_API_URL = "https://api.gemini.com/v1/recommendations"  # Ejemplo de URL

# Agrega tu clave API de Gemini
API_KEY = "SACA TU API KEY"

# --------------------- RUTAS Y CONFIG ---------------------
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

# Configurar el cliente de Gemini con la clave de API
client = genai.Client(api_key=API_KEY)

app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

templates = Jinja2Templates(directory=STATIC_DIR)

# --------------------- MODELO DE EMOCIONES ---------------------
# Usar un modelo de Hugging Face para clasificación de emociones
emotion_classifier = pipeline(
    "text-classification", 
    model="bhadresh-savani/bert-base-uncased-emotion"  # Cambiar por el modelo adecuado
)

# --------------------- MODELOS DE PETICIÓN ---------------------
class FeelingRequest(BaseModel):
    text: str

# Mapeo de emociones de inglés a español
EMOTION_MAPPING = {
    "anger": "Enojo",
    "fear": "Miedo",
    "joy": "Feliz",
    "sadness": "Tristeza",
    "surprise": "Sorpresa",
    "disgust": "Desgusto",
    "contempt": "Desprecio"
}

# Función para mapear la emoción detectada a español
def map_emotion_to_spanish(emotion):
    return EMOTION_MAPPING.get(emotion, emotion)  # Si no se encuentra, retorna la emoción en inglés


# --------------------- FUNCIONES AUXILIARES ---------------------
@lru_cache(maxsize=1)
def cargar_historial():
    """Carga el historial de interacciones desde un archivo JSON y lo guarda en cache"""
    try:
        with open(DATA_HISTORY, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error al cargar el historial: {str(e)}")

def guardar_historial(historial):
    """Guarda el historial actualizado en el archivo JSON"""
    try:
        with open(DATA_HISTORY, 'w', encoding='utf-8') as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Error al guardar el historial: {str(e)}")

# --------------------- RUTAS ---------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal (HTML)"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al cargar la página principal: {str(e)}"})

@app.post("/analyze")
async def analyze(req: FeelingRequest):
    """Analiza el texto del usuario y predice su emoción usando Hugging Face"""
    try:
        # Preprocesar el texto antes de enviarlo al modelo de emociones
        clean_text = preprocess(req.text)  # Usamos preprocess desde nlp.py
        result = emotion_classifier(clean_text)  # Clasificación de emociones con el modelo de Hugging Face

        emotion = result[0]['label']  # La emoción detectada (por ejemplo: 'anger', 'joy')
        confidence = result[0]['score']  # Confianza en la predicción

        # Mapear la emoción a español
        emotion_in_spanish = map_emotion_to_spanish(emotion)

        return JSONResponse({
            "emotion": emotion_in_spanish,
            "confidence": confidence
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error en la predicción de emoción: {str(e)}"})

@app.post("/recommend")
async def recommend(request: Request):
    """Genera recomendaciones personalizadas y guarda en historial usando Gemini API"""
    try:
        payload = await request.json()
        user_text = payload.get('feeling_text', '').strip()
        detected_emotion = payload.get('detected_emotion', 'Desconocida').strip()
        history_context = payload.get('history', '').strip()

        # Preprocesar el texto antes de pasarlo al generador de recomendaciones
        preprocessed_text = preprocess(user_text)
        
        # Generar contenido usando la API de Gemini (Gemini 2.5 Flash)
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Modelo adecuado para generar contenido
            contents=f"Genera recomendaciones para mejorar el bienestar emocional del usuario que se siente {detected_emotion}. El texto del usuario es: {user_text}. Contexto: {history_context}"
        )

        recommendation = response.text.strip()  # Obtener la recomendación generada

        # Cargar y actualizar historial
        historial = cargar_historial()
        historial.append({
            "fecha": datetime.now().isoformat(),
            "texto": user_text,
            "emocion": detected_emotion,
            "recomendacion": recommendation or "Sin recomendación"
        })
        guardar_historial(historial)

        return JSONResponse({
            "recommendation": recommendation or "Sin recomendación",
            "error": None
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Ocurrió un error al generar la recomendación: {str(e)}"}
        )

@app.get("/history")
async def history():
    try:
        historial = cargar_historial()
        return JSONResponse(content=historial)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"No se pudo cargar el historial: {str(e)}"})

@app.get('/history-view', response_class=HTMLResponse)
async def history_page():
    """Devuelve la página de historial como HTML"""
    try:
        return templates.TemplateResponse("history.html", {"request": None})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al cargar la página de historial: {str(e)}"})