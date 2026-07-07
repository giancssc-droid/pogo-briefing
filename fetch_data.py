"""
fetch_data.py
--------------
Descarga TODA la información cruda que necesitamos para armar el briefing diario
de Pokémon GO y la guarda en data/latest.json.

Fuentes:
1. ScrapedDuck (https://github.com/bigfoott/ScrapedDuck)
   -> Proyecto público que ya scrapea LeekDuck.com y publica JSON estructurado:
      - events.json   (eventos activos y próximos, con fechas de inicio/fin)
      - raids.json    (jefes de incursión actuales, por tier)
      - research.json (tareas de investigación de campo y sus recompensas)
      - eggs.json     (huevos de Dynamax/Max Battles y sus posibles Pokémon)

2. Feeds RSS que ya usa el proyecto ScrapyGo:
   - Pokémon GO oficial
   - GO Hub Events
   - GO Hub News
   - LeekDuck Twitter (vía rss-bridge)

No necesitas tocar nada de este archivo para que funcione. Si algún día una
fuente cambia de URL, ese es el único lugar que habría que actualizar.
"""

import json
import os
from datetime import datetime, timedelta, timezone

import feedparser
import requests

# --------------------------------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------------------------------

# Zona horaria de Venezuela (UTC-4, sin horario de verano)
VENEZUELA_UTC_OFFSET = timedelta(hours=-4)

# Solo nos interesan noticias publicadas en los últimos N días
# (esto es lo que evita el problema de "noticias viejas" que tenías con Enzo)
MAX_NEWS_AGE_DAYS = 4

# Máximo de noticias a incluir por fuente, para no saturar el prompt de la IA
MAX_NEWS_PER_SOURCE = 8

SCRAPEDDUCK_BASE = "https://raw.githubusercontent.com/bigfoott/ScrapedDuck/data"

SCRAPEDDUCK_SOURCES = {
    "events": f"{SCRAPEDDUCK_BASE}/events.json",
    "raids": f"{SCRAPEDDUCK_BASE}/raids.json",
    "research": f"{SCRAPEDDUCK_BASE}/research.json",
    "eggs": f"{SCRAPEDDUCK_BASE}/eggs.json",
}

RSS_SOURCES = {
    "oficial": "https://pokemongo.com/es/news",
    "gohub_events": "https://pokemongohub.net/post/category/event/feed/",
    "gohub_news": "https://pokemongohub.net/post/category/news/feed/",
    "leekduck_twitter": (
        "https://rss-bridge.org/bridge01/?action=display"
        "&username=LeekDuckTwitter&bridge=TelegramBridge&format=Atom"
    ),
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "latest.json")


# --------------------------------------------------------------------------
# FUNCIONES
# --------------------------------------------------------------------------

def fetch_json(url: str):
    """Descarga un JSON crudo. Si falla, devuelve None en vez de reventar todo el script."""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        print(f"[AVISO] No se pudo descargar {url}: {exc}")
        return None


def fetch_scrapedduck_data() -> dict:
    data = {}
    for key, url in SCRAPEDDUCK_SOURCES.items():
        print(f"Descargando {key} desde ScrapedDuck...")
        data[key] = fetch_json(url) or []
    return data


def parse_entry_date(entry) -> datetime | None:
    """Intenta obtener la fecha de publicación de una entrada RSS, en UTC."""
    for field in ("published_parsed", "updated_parsed"):
        value = getattr(entry, field, None)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return None


def fetch_rss_news() -> dict:
    """Descarga los feeds RSS y se queda solo con lo publicado recientemente."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_NEWS_AGE_DAYS)
    news_by_source = {}

    for source_name, url in RSS_SOURCES.items():
        print(f"Descargando feed RSS: {source_name}...")
        try:
            parsed = feedparser.parse(url)
        except Exception as exc:  # noqa: BLE001
            print(f"[AVISO] No se pudo leer el feed {source_name}: {exc}")
            news_by_source[source_name] = []
            continue

        items = []
        for entry in parsed.entries:
            entry_date = parse_entry_date(entry)
            # Si no hay fecha, la incluimos igual (mejor de más que perder info)
            if entry_date and entry_date < cutoff:
                continue

            items.append({
                "title": getattr(entry, "title", "").strip(),
                "summary": getattr(entry, "summary", "").strip()[:500],
                "link": getattr(entry, "link", ""),
                "published": entry_date.isoformat() if entry_date else None,
            })

        # Ordenar del más nuevo al más viejo y recortar
        items.sort(key=lambda i: i["published"] or "", reverse=True)
        news_by_source[source_name] = items[:MAX_NEWS_PER_SOURCE]

    return news_by_source


def main():
    now_utc = datetime.now(timezone.utc)
    now_venezuela = now_utc + VENEZUELA_UTC_OFFSET

    combined = {
        "generated_at_utc": now_utc.isoformat(),
        "today_venezuela": now_venezuela.strftime("%Y-%m-%d"),
        "today_venezuela_readable": now_venezuela.strftime("%A %d de %B de %Y"),
        "scrapedduck": fetch_scrapedduck_data(),
        "news": fetch_rss_news(),
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"\nListo. Datos combinados guardados en {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
