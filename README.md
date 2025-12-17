# EmilIA Chatbot - Servicio de Webhook

Asistente virtual para Schaller & Ponce, reemplazo de n8n con control total y confiabilidad.

## Características

- ✅ **Sin dependencias de plataformas inestables:** Código Python puro
- ✅ **Control total del prompt:** Archivo `prompt.md` versionado
- ✅ **Usa Anthropic Claude:** API confiable y poderosa
- ✅ **Deploy simple:** Docker en Render
- ✅ **Sin credenciales encriptadas:** API key en variable de entorno
- ✅ **Debugging fácil:** Logs claros, código simple

## Estructura del Proyecto

```
emilia-chatbot/
├── app.py              # Aplicación Flask principal
├── prompt.md           # Prompt de sistema de EmilIA (configurable)
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Para deploy en Render
├── .gitignore
└── README.md
```

## Desarrollo Local

### Prerrequisitos

- Python 3.11+
- API Key de Anthropic

### Setup

1. Crear entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
export ANTHROPIC_API_KEY="tu-api-key"
export PORT=8080
```

4. Ejecutar:
```bash
python app.py
```

5. Probar:
```bash
curl -X POST http://localhost:8080/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"chatInput":"Hola, ¿qué servicios ofrecen?"}'
```

## Deploy en Render

### Paso 1: Crear repositorio en GitHub

```bash
git init
git add .
git commit -m "Initial commit: EmilIA chatbot service"
git remote add origin https://github.com/TU_USUARIO/emilia-chatbot.git
git push -u origin main
```

### Paso 2: Crear servicio en Render

1. Ve a https://dashboard.render.com
2. "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Configuración:
   - **Name:** emilia-chatbot
   - **Runtime:** Docker
   - **Plan:** Free
5. Variables de entorno:
   - `ANTHROPIC_API_KEY`: Tu API key de Anthropic
6. "Create Web Service"

### Paso 3: Obtener URL del servicio

Una vez deployed, tu URL será algo como:
```
https://emilia-chatbot.onrender.com
```

Webhook endpoint:
```
https://emilia-chatbot.onrender.com/webhook/chat
```

## Actualizar Prompt

Para mejorar las respuestas de EmilIA:

1. Edita `prompt.md` con los cambios deseados
2. Commit y push a GitHub:
```bash
git add prompt.md
git commit -m "Mejora de prompt: [descripción]"
git push
```
3. Render auto-deploys automáticamente

## Endpoints

### `POST /webhook/chat`

Endpoint principal del chatbot.

**Request:**
```json
{
  "chatInput": "Mensaje del usuario"
}
```

**Response:**
```json
{
  "output": "Respuesta de EmilIA"
}
```

### `GET /health`

Health check detallado.

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "api_key_configured": true,
    "prompt_loaded": true,
    "prompt_length": 3542
  }
}
```

### `GET /`

Health check simple.

**Response:**
```json
{
  "service": "EmilIA Chatbot",
  "status": "running",
  "version": "1.0.0"
}
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY no configurada"

Asegúrate de haber agregado la variable de entorno en Render:
1. Dashboard → Tu servicio → Environment
2. Agregar `ANTHROPIC_API_KEY` con tu API key
3. Guardar y redesplegar

### Error: "prompt.md no encontrado"

El archivo `prompt.md` debe estar en la raíz del proyecto. Verifica que esté en el repositorio.

### Respuestas lentas

Primera respuesta puede tardar ~30 segundos (cold start de Render free tier). Respuestas posteriores son rápidas.

## Arquitectura

```
Website (schaller-ponce.com.ar)
    ↓ POST /webhook/chat
EmilIA Service (Render)
    ↓ API call
Anthropic Claude
    ↓ Response
EmilIA Service
    ↓ JSON response
Website (muestra mensaje)
```

## Ventajas vs n8n

| Característica | n8n | EmilIA Service |
|----------------|-----|----------------|
| Credenciales | Encriptadas (se corrompen) | Variable de entorno (simple) |
| Prompt | UI de n8n (no versionado) | Archivo .md (versionado en Git) |
| Debugging | Difícil | Logs claros |
| Costo | $7/mes (paid tier necesario) | Gratis (Render free tier) |
| Control | Limitado | Total |
| Confiabilidad | Problemas en free tier | Estable |

## Mantenimiento

### Actualizar modelo de Claude

Edita `app.py`, línea del model:
```python
model="claude-3-5-sonnet-20241022",  # Cambiar aquí
```

### Aumentar timeout

Edita `Dockerfile`, línea de gunicorn:
```dockerfile
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 180 app:app
```

### Ver logs en Render

Dashboard → Tu servicio → Logs (en tiempo real)

## Licencia

Propiedad de Schaller & Ponce. Uso interno.

## Autor

Desarrollado para Schaller & Ponce
Consultoría en IA y Data Science
https://schaller-ponce.com.ar
