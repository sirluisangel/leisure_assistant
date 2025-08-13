from llama_cpp import Llama
from collections import defaultdict
from typing import Iterator
import re, json

MODEL_PATH = "./mistral-7b-instruct-v0.1.Q2_K.gguf"

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0
)

TEMPLATE = (
    "<h3 style='font-weight: bold; color: #6a0dad;'>Eres un coach emocional empático y profesional.</h3>"
    "<p>El usuario se siente <span style='color: #6a0dad; font-weight: bold;'>{emotion}</span>.</p>"
    "<p><b>Mensaje del usuario:</b> {text}</p>"
    "<p><b>Contexto previo:</b> {history}</p><br>"
    "<p><b>Tu tarea es generar una lista de recomendaciones prácticas para mejorar su bienestar emocional.</b></p>"
    "<p>Responde <b>únicamente</b> en español, sin usar palabras en inglés.</p>"
    "<p>Puedes dar tantas como consideres útiles.</p>"
    "<p>Por favor, responde solo con los pasos numerados, sin repetir el mensaje ni la emoción.</p>"
    "<p><b>Formato esperado:</b></p>"
    "<ul>"
    "<li>1. ...</li>"
    "<li>2. ...</li>"
    "<li>3. ...</li>"
    "</ul>"
    "<h4>Recomendaciones:</h4>"
    "<p style='font-size: 16px; line-height: 1.6;'>{recommendations}</p>"
)

def cargar_palabras_clave():
    with open('categorias_palabras.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Optimización usando expresiones regulares y set para palabras clave
def clasificar_recomendacion(texto):
    categorias_palabras = cargar_palabras_clave()
    texto = texto.lower()
    
    # Crear un set de palabras clave por categoría
    for categoria, palabras in categorias_palabras.items():
        if any(re.search(rf'\b{re.escape(palabra)}\b', texto) for palabra in palabras):
            return categoria

    return "GENERAL"

def agrupar_recomendaciones_por_tipo(texto):
    lineas = [l.strip() for l in texto.split("\n") if re.match(r"^\d+\.", l.strip())]
    categorias = defaultdict(list)
    recomendaciones_vistas = set()

    for linea in lineas:
        contenido = re.sub(r"^\d+\.\s*", "", linea).strip()
        if contenido in recomendaciones_vistas:
            continue
        recomendaciones_vistas.add(contenido)
        tipo = clasificar_recomendacion(contenido)
        categorias[tipo].append(contenido)

    orden_tipos = ["GENERAL", "FÍSICA", "COGNITIVA", "EMOCIONAL", "SOCIAL", "ESPIRITUAL"]
    resultado = ""

    for tipo in orden_tipos:
        recs = categorias.get(tipo)
        if recs:
            resultado += f"RECOMENDACIÓN {tipo}\n"
            for idx, rec in enumerate(recs, start=1):
                resultado += f"\t{idx}. {rec}\n"
            resultado += "\n"

    return resultado.strip()

def generate_recommendation(context: dict):
    emotion = context.get("emotion", "Desconocida")
    prompt = TEMPLATE.format(
        emotion=emotion,
        text=context.get("text", "").strip(),
        history=context.get("history", "Sin contexto").strip(),
        recommendations="... Aquí van las recomendaciones generadas ...",
    )

    try:
        output = llm(prompt, max_tokens=512, temperature=0.7, top_p=0.9)
        
        if isinstance(output, Iterator):
            first_response = next(output)
        else:
            first_response = output

        raw_text = first_response['choices'][0]['text'].strip()

        if raw_text.lower().startswith("eres un") or len(raw_text) < 20:
            return {
                "error": "⚠ El modelo respondió con texto genérico o vacío.",
                "emocion": context.get("emotion", "Desconocida"),
                "recomendacion": raw_text,
            }
        
        for stop_phrase in ["Eres un", "Mensaje:", "Contexto", "Respuesta:"]:
            if stop_phrase in raw_text:
                raw_text = raw_text.split(stop_phrase)[0].strip()

        recomendaciones_formateadas = agrupar_recomendaciones_por_tipo(raw_text)

        return {
            "error": None,
            "emocion": emotion,
            "recomendacion": recomendaciones_formateadas,
        }

    except Exception as e:
        return {
            "error": f"⚠ Error generando recomendación: {str(e)}",
            "emocion": emotion,
            "recomendacion": None,
        }