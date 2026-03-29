"""
EmilIA Chatbot - Servicio de webhook para Schaller & Ponce
Reemplazo de n8n con control total y confiabilidad
"""

import os
import time
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS
from anthropic import Anthropic
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app Flask
app = Flask(__name__)

# Configurar CORS para permitir requests desde el website
CORS(app, resources={
    r"/webhook/*": {
        "origins": [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:8888",
            "http://127.0.0.1:8888",
            "https://schaller-ponce.com.ar",
            "https://www.schaller-ponce.com.ar"
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Cache del prompt para no llamar GitHub en cada request
_prompt_cache = {"content": None, "loaded_at": 0}
PROMPT_CACHE_TTL = 300  # 5 minutos

GITHUB_PROMPT_URL = (
    "https://raw.githubusercontent.com/Krl05oP11/emilia-chatbot/main/prompt.md"
)

def load_system_prompt():
    """Carga el prompt desde GitHub (con cache de 5 min) o desde archivo local como fallback"""
    now = time.time()
    if _prompt_cache["content"] and (now - _prompt_cache["loaded_at"]) < PROMPT_CACHE_TTL:
        return _prompt_cache["content"]

    # Intentar cargar desde GitHub
    try:
        with urllib.request.urlopen(GITHUB_PROMPT_URL, timeout=5) as resp:
            prompt = resp.read().decode("utf-8")
            _prompt_cache["content"] = prompt
            _prompt_cache["loaded_at"] = now
            logger.info(f"Prompt cargado desde GitHub ({len(prompt)} chars)")
            return prompt
    except Exception as e:
        logger.warning(f"No se pudo cargar prompt desde GitHub: {e}. Usando archivo local.")

    # Fallback: archivo local
    prompt_file = os.path.join(os.path.dirname(__file__), 'prompt.md')
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
            _prompt_cache["content"] = prompt
            _prompt_cache["loaded_at"] = now
            return prompt
    except FileNotFoundError:
        logger.warning("prompt.md no encontrado, usando prompt por defecto")
        return """Eres EmilIA, la asistente virtual de Schaller & Ponce, una consultoría especializada en Inteligencia Artificial y Data Science.

Tu rol es:
- Ayudar a usuarios a entender nuestros servicios
- Responder preguntas sobre IA, Data Science e IA Agéntica
- Guiar a usuarios interesados a agendar una consulta gratuita

Cuando usuarios pregunten sobre precios o cotizaciones, explica que cada proyecto es único y sugiere agendar una consulta para evaluar sus necesidades específicas.

Sé profesional, amigable y clara."""

# Inicializar cliente de Anthropic
def get_anthropic_client():
    """Obtiene cliente de Anthropic con API key"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no configurada en variables de entorno")
    return Anthropic(api_key=api_key)

@app.route('/')
def index():
    """Endpoint de health check"""
    return jsonify({
        "service": "EmilIA Chatbot",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/webhook/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    Endpoint principal del chatbot
    Recibe: {"chatInput": "mensaje del usuario"}
    Retorna: {"output": "respuesta de EmilIA"}
    """
    # Manejar preflight CORS
    if request.method == 'OPTIONS':
        return '', 204

    try:
        # Obtener mensaje del usuario
        data = request.get_json()
        if not data or 'chatInput' not in data:
            return jsonify({
                "error": "Missing 'chatInput' in request body"
            }), 400

        user_message = data['chatInput']
        logger.info(f"Received message: {user_message[:100]}...")

        # Cargar prompt de sistema
        system_prompt = load_system_prompt()

        # Llamar a Anthropic API
        client = get_anthropic_client()

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5 (latest available)
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        # Extraer respuesta
        assistant_message = response.content[0].text
        logger.info(f"Generated response: {assistant_message[:100]}...")

        # Retornar en formato compatible con el frontend
        return jsonify({
            "output": assistant_message
        })

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({
            "error": "Service configuration error",
            "output": "Lo siento, hay un problema de configuración. Por favor, contacta al administrador."
        }), 500

    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        return jsonify({
            "error": str(e),
            "output": "Lo siento, hubo un problema al procesar tu mensaje. Por favor, intenta nuevamente."
        }), 500

@app.route('/health')
def health():
    """Endpoint de health check — no dispara llamadas externas"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    cached = _prompt_cache["content"]
    return jsonify({
        "status": "healthy",
        "checks": {
            "api_key_configured": bool(api_key),
            "prompt_cached": bool(cached),
            "prompt_length": len(cached) if cached else 0
        }
    })

if __name__ == '__main__':
    # Para desarrollo local
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
