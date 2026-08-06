# 📅 Pogo Briefing

Un sistema automatizado que genera y entrega un resumen diario de Pokémon GO — eventos activos, raids que valen la pena, y noticias relevantes — directo a Telegram y a una página web, sin que el usuario tenga que revisar múltiples fuentes cada mañana.

## Qué hace

Todos los días a las 8:00 AM (hora de Venezuela), el sistema:

1. **Recopila datos estructurados** de eventos, raids, research y huevos desde [ScrapedDuck](https://github.com/bigfoott/ScrapedDuck), un proyecto público que scrapea LeekDuck.
2. **Recopila noticias** desde el feed oficial de Pokémon GO, GO Hub y LeekDuck Twitter.
3. **Le pide a Gemini** (la API gratuita de Google) que filtre todo ese ruido y arme un resumen conciso, priorizando lo que realmente vale la pena hacer ese día.
4. **Entrega el resultado** por Telegram y lo publica en una página web estática vía GitHub Pages.

Todo corre solo, sin intervención manual, usando GitHub Actions como programador de tareas.

## Cómo se ve

El briefing llega como un mensaje de Telegram con encabezados en negrita y secciones separadas — solo las que tienen contenido relevante ese día:

> **📅 Pokémon GO - Jueves 06 de agosto de 2026**
>
> **🎉 Eventos activos**
> • Summer Marathon: Arctic Ember (hasta el 10 de agosto), Shiny Snom debuta.
>
> • Ultra League and Weather Cup (hasta el 11 de agosto).
>
> **⚔️ Raids activas**
> • 5 estrellas: Uxie, Mesprit y Azelf, todos con shiny disponible.
>
> • Shadow Giratina (Forma Alterada) en Raids Oscuras.
>
> **🎯 Prioridad de hoy**
> • Completa las raids legendarias con shiny disponible antes del 11.
>
> • Revisa el debut de Shiny Snom en el Summer Marathon.

Nada de listas interminables de cada jefe de raid tier 1, ni secciones vacías con "nada destacado hoy" — solo lo que importa, en un formato que se lee de un vistazo.

## Arquitectura

| Componente | Rol |
|---|---|
| `fetch_data.py` | Descarga y consolida los datos crudos (raids, research, eventos, noticias) |
| `generate_briefing.py` | Le pasa los datos a Gemini, genera el texto, y lo distribuye |
| GitHub Actions | Ejecuta todo el flujo automáticamente cada mañana |
| GitHub Pages | Publica una versión web del briefing del día |
| Telegram Bot API | Entrega el briefing con formato enriquecido (HTML) |

## Stack

- **Python** — lógica de scraping, procesamiento y distribución
- **Google Gemini API** (`gemini-2.5-flash`) — capa gratuita, sin tarjeta de crédito, para generar el texto del briefing
- **Telegram Bot API** — entrega diaria con formato HTML
- **GitHub Actions** — automatización con cron diario
- **GitHub Pages** — hosting de la versión web

## Por qué existe

Antes de esto, revisar Pokémon GO significaba pasar por Inoreader, Enzo Reader, y varias páginas distintas cada mañana para armar mentalmente qué hacer ese día. Este proyecto reemplaza todo ese proceso manual por un resumen que llega solo, ya filtrado y priorizado.

## Costo

$0. La capa gratuita de Gemini, GitHub Actions para repositorios personales, GitHub Pages, Telegram y ScrapedDuck son gratuitos, y el uso de este proyecto (una ejecución corta al día) está muy por debajo de cualquier límite gratuito.

---

Proyecto personal, mantenido activamente.
