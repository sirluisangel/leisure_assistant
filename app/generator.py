# app/generator.py
# Generador de recomendaciones usando transformers text-generation (GPT-2 por defecto)
from transformers import pipeline
import os
from dotenv import load_dotenv
load_dotenv()
GEN_NAME = os.getenv('GEN_MODEL','gpt2')
GENERATOR = pipeline('text-generation', model=GEN_NAME)

TEMPLATE = (
    "Eres un asistente empático y profesional. Usuario: {text}\n"
    "Emoción detectada: {emotion}\n"
    "Contexto corto: {history}\n"
    "Genera una respuesta empática, explicativa y pasos prácticos (3 pasos concretos) para ayudar al usuario."
)

def generate_recommendation(context: dict):
    prompt = TEMPLATE.format(text=context.get('text',''), emotion=context.get('emotion','Unknown'), history=context.get('history',''))
    out = GENERATOR(prompt, max_length=200, num_return_sequences=1)
    text = out[0]['generated_text']
    # quitar la parte del prompt si aparece
    if 'Genera una respuesta' in text:
        return text.split('Genera una respuesta')[-1].strip()
    return text.strip()
