"""
generate_briefing.py
---------------------
Lee data/latest.json (generado por fetch_data.py), se lo pasa a la API
GRATUITA de Google Gemini con instrucciones precisas, y genera el briefing
diario de Pokémon GO.

Salidas:
1. briefing.md                        -> versión en texto plano
2. docs/pogo-briefing/index.html      -> versión web (para GitHub Pages)
3. Mensaje enviado por Telegram (si están configuradas las variables de entorno)

Variables de entorno necesarias (se configuran como "Secrets" en GitHub):
- GEMINI_API_KEY      -> tu clave gratuita de Google AI Studio
- TELEGRAM_BOT_TOKEN  -> token del bot de Telegram (opcional)
- TELEGRAM_CHAT_ID    -> ID del chat/usuario al que enviar el mensaje (opcional)

Sobre el costo: Gemini ofrece un nivel gratuito real, sin tarjeta de
crédito, para el modelo "gemini-2.5-flash" (y variantes "flash-lite").
Con una sola llamada al día, este proyecto nunca se acerca al límite
gratuito. Si algún día Google cambia las condiciones, revisa
https://ai.google.dev/gemini-api/docs/pricing para confirmar.
"""

import json
import os
from datetime import datetime

import requests

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "latest.json")
MD_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "briefing.md")
HTML_OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "docs", "pogo-briefing", "index.html"
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Modelo gratuito de Gemini. "gemini-2.5-flash" es el más estable y probado.
# Si quieres aún más margen de cuota gratuita, puedes cambiar a
# "gemini-2.5-flash-lite".
MODEL = "gemini-2.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
)

SYSTEM_PROMPT = """\
Eres un asistente que redacta un briefing diario de Pokémon GO en español, \
para un jugador que quiere saber en 30 segundos qué hacer hoy.

Recibirás datos crudos en JSON:
- scrapedduck.events: eventos, cada uno con nombre y fechas de inicio/fin (UTC)
- scrapedduck.raids: jefes de incursión actuales, con nombre y tier
- scrapedduck.research: tareas de investigación de campo y sus recompensas
- scrapedduck.eggs: huevos de Max Battles / Dynamax y los Pokémon que pueden salir
- news: noticias recientes agrupadas por fuente (oficial, GO Hub, LeekDuck Twitter)
- today_venezuela: la fecha de HOY en formato YYYY-MM-DD, en hora de Venezuela

Instrucciones:
1. Compara las fechas de inicio/fin de cada evento contra today_venezuela para \
   decidir qué eventos están ACTIVOS hoy, cuáles ya terminaron (ignóralos) y \
   cuáles son próximos (menciona como máximo 2, si empiezan en los próximos 5 días).
2. En raids, agrupa por tier (5 estrellas / Mega / 3 estrellas / 1 estrella / Sombra) \
   y destaca solo los que probablemente valga la pena hacer (legendarios, \
   Mega, shiny disponible). No listes los 20 jefes de tier 1 si no aportan nada.
3. En eggs, estos representan lo que antes llamábamos "Dynamax activo". \
   Lista los Pokémon disponibles.
4. En research, menciona solo las tareas con recompensas relevantes \
   (shiny disponible, Pokémon raro, mucho polvo estelar), no la lista completa.
5. En news, ignora duplicados entre fuentes y quédate con lo más importante \
   de los últimos días. Si no hay nada relevante, omite la sección.
6. Termina con una sección "🎯 Prioridad de hoy": 2 a 4 bullets con lo más \
   importante que el jugador debería hacer hoy, en orden de importancia.
7. Sé conciso. Nada de relleno ni explicaciones de tu proceso. Usa exactamente \
   este formato (respeta los emojis y encabezados):

📅 Pokémon GO - [fecha legible]

🎉 Eventos activos
• ...

⚔️ Raids activas
• ...

🟣 Dynamax / Max Battles
• ...

📰 Noticias importantes
• ...

🎯 Prioridad de hoy
• ...

Si alguna sección no tiene contenido relevante, escribe "• Nada destacado hoy" \
en esa sección en vez de omitir el encabezado.
Responde ÚNICAMENTE con el briefing en ese formato, sin texto antes ni después.
"""


def call_gemini(data: dict) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "Falta la variable de entorno GEMINI_API_KEY. "
            "Configúrala como Secret en GitHub."
        )

    user_message = (
        "Aquí están los datos de hoy. Genera el briefing:\n\n"
        + json.dumps(data, ensure_ascii=False)
    )

    response = requests.post(
        GEMINI_URL,
        headers={
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [
                {"role": "user", "parts": [{"text": user_message}]}
            ],
            "generationConfig": {
                "maxOutputTokens": 1500,
                "temperature": 0.4,
            },
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()

    candidates = payload.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Gemini no devolvió respuesta: {payload}")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "\n".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise RuntimeError(f"Gemini devolvió una respuesta vacía: {payload}")
    return text


def save_markdown(briefing_text: str):
    with open(MD_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(briefing_text + "\n")


def save_html(briefing_text: str, today_readable: str):
    os.makedirs(os.path.dirname(HTML_OUTPUT_PATH), exist_ok=True)
    escaped = (
        briefing_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pokémon GO - Briefing diario</title>
<style>
  body {{
    font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
    background: #12141a;
    color: #f1f1f1;
    max-width: 640px;
    margin: 0 auto;
    padding: 24px 16px 60px;
    line-height: 1.6;
  }}
  pre {{
    white-space: pre-wrap;
    font-family: inherit;
    font-size: 1.05rem;
    background: #1c1f27;
    border-radius: 12px;
    padding: 20px;
  }}
  .updated {{
    color: #8b8f9a;
    font-size: 0.85rem;
    margin-top: 20px;
    text-align: center;
  }}
</style>
</head>
<body>
<pre>{escaped}</pre>
<p class="updated">Actualizado: {today_readable} (hora de Venezuela)</p>
</body>
</html>
"""
    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)


def send_telegram(briefing_text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[INFO] Telegram no configurado, se omite el envío.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": briefing_text},
        timeout=20,
    )
    if resp.ok:
        print("Mensaje enviado por Telegram correctamente.")
    else:
        print(f"[AVISO] Telegram devolvió un error: {resp.status_code} {resp.text}")


def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Generando briefing con la API gratuita de Gemini...")
    briefing_text = call_gemini(data)

    save_markdown(briefing_text)
    save_html(briefing_text, data.get("today_venezuela_readable", datetime.now().isoformat()))
    send_telegram(briefing_text)

    print("\n--- BRIEFING GENERADO ---\n")
    print(briefing_text)


if __name__ == "__main__":
    main()
