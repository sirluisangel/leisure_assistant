# 🎯 Leisure Assistant

> Asistente emocional inteligente que analiza sentimientos y proporciona recomendaciones personalizadas.

## 📋 Características principales

- 🧠 Análisis emocional mediante IA
- 💡 Recomendaciones personalizadas 
- 📊 Historial de análisis emocionales
- 🌐 Soporte multilingüe
- ⚡ API REST con FastAPI

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- pip

### Pasos de instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tuuser/leisure_assistant.git
cd leisure_assistant
```

2. Crear entorno virtual:
```bash
python -m venv venv
```

3. Activar entorno virtual:

**Windows:**
```bash
venv\Scripts\activate
```

**Unix/macOS:**
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

## 💻 Uso

1. Crear directorio de datos:
```bash
mkdir data
```

2. Iniciar servidor:
```bash
uvicorn app.main:app --reload
```

3. Abrir en navegador:
```
http://127.0.0.1:8000/
```

## 🏗️ Estructura del proyecto

```
leisure_assistant/
├── app/
│   ├── emotion_net.py   # Red neuronal de emociones
│   ├── generator.py     # Generador de recomendaciones
│   ├── nlp.py           # Procesamiento de lenguaje
│   └── main.py          # Servidor FastAPI
├── static/              # Frontend
├── data/               # Datos y modelos
└── requirements.txt    # Dependencias
```

## 🛠️ Desarrollo

### Componentes principales
- **FastAPI Server**: Maneja rutas y lógica de backend
- **Emotion Net**: Red neuronal PyTorch para clasificación
- **NLP Pipeline**: Preprocesamiento y embeddings
- **Generator**: Sistema de recomendaciones con transformers

### Modelos
- Puedes usar modelos pre-entrenados de HuggingFace
- Entrenamiento personalizado disponible en `emotion_net.py`
- Integración opcional con OpenAI GPT-4