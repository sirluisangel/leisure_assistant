from llama_cpp import Llama
from collections import defaultdict
import re

# Ruta del modelo
MODEL_PATH = "./mistral-7b-instruct-v0.1.Q2_K.gguf"

# Instanciar modelo
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0
)

# Prompt de entrada
TEMPLATE = (
    "Eres un coach emocional empático y profesional.\n"
    "El usuario se siente {emotion}.\n"
    "Mensaje: {text}\n"
    "Contexto breve: {history}\n\n"
    "Tu tarea es generar una lista de recomendaciones prácticas para mejorar su bienestar emocional.\n"
    "Responde *únicamente* en español, sin usar palabras en inglés.\n"
    "Puedes dar tantas como consideres útiles.\n"
    "Por favor, responde solo con los pasos numerados, sin repetir el mensaje ni la emoción.\n"
    "Formato esperado:\n"
    "1. ...\n"
    "2. ...\n"
    "3. ...\n\n"
    "Recomendaciones:"
)


# Clasificador simple por tipo
def clasificar_recomendacion(texto):
    texto = texto.lower()
    if any(p in texto for p in ["ejercicio", "dormir", "rutina", "alimentación", "cuerpo", "salud", "físico"]):
        return "FÍSICA"
    elif any(p in texto for p in ["pensar", "reflexiona", "analiza", "diario", "registro", "mental", "yoga", "cognitivo"]):
        return "COGNITIVA"
    elif any(p in texto for p in ["sentimiento", "emoción", "aceptación", "gratitud", "autoestima", "auto-compasión", "autocompasión"]):
        return "EMOCIONAL"
    elif any(p in texto for p in ["familia", "amigos", "apoyo", "habla", "relaciones", "social"]):
        return "SOCIAL"
    elif any(p in texto for p in ["meditación", "respiración", "mindfulness", "espiritual", "conexión", "alma"]):
        return "ESPIRITUAL"
    else:
        return "GENERAL"

# Agrupador y formateador
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

# Generador principal
def generate_recommendation(context: dict):
    prompt = TEMPLATE.format(
        emotion=context.get("emotion", "Desconocida"),
        text=context.get("text", "").strip(),
        history=context.get("history", "Sin contexto").strip()
    )

    try:
        output = llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9
        )
        raw_text = output['choices'][0]['text'].strip()

        if raw_text.lower().startswith("eres un") or len(raw_text) < 20:
            return {
                "error": "⚠ El modelo respondió con texto genérico o vacío.",
                "emocion": context.get("emotion", "Desconocida"),
                "recomendacion": raw_text
            }
                # Eliminar posibles partes no deseadas
        for stop_phrase in ["Eres un", "Mensaje:", "Contexto", "Respuesta:"]:
            if stop_phrase in raw_text:
                raw_text = raw_text.split(stop_phrase)[0].strip()

        # Agrupar por tipo
        recomendaciones_formateadas = agrupar_recomendaciones_por_tipo(raw_text)

        return {
            "error": None,
            "emocion": context.get("emotion", "Desconocida"),
            "recomendacion": recomendaciones_formateadas
        }
    
    except Exception as e:
        return {
            "error": f"⚠ Error generando recomendación: {str(e)}",
            "emocion": context.get("emotion", "Desconocida"),
            "recomendacion":None
        }
