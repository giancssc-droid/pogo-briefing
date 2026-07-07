# Briefing diario de Pokémon GO — Guía de instalación

Este sistema reemplaza a Inoreader + Enzo Reader. Cada mañana a las **8:00 AM
(hora de Venezuela)**, automáticamente:

1. Descarga datos ya estructurados de raids, research, eventos y huevos
   (desde el proyecto público ScrapedDuck, que scrapea LeekDuck por ti).
2. Descarga tus feeds RSS de noticias (oficial, GO Hub, LeekDuck Twitter).
3. Le pasa todo eso a la IA de Claude, que genera el briefing con el formato
   que ya conoces.
4. Te lo envía por **Telegram** y lo publica en una **página web** (GitHub Pages).

No necesitas escribir ni modificar código. Solo seguir estos pasos.

---

## Paso 1 — Crear el repositorio

1. Ve a [github.com/new](https://github.com/new).
2. Nómbralo, por ejemplo, `pogo-briefing`.
3. Que sea público o privado, cualquiera funciona.
4. Sube todos los archivos de esta carpeta (`fetch_data.py`,
   `generate_briefing.py`, `requirements.txt`, la carpeta `.github/`, etc.)
   a ese repositorio. Puedes arrastrarlos directamente en la interfaz web de
   GitHub ("Add file" → "Upload files").

> Si prefieres mantener todo junto con tu repo `ScrapyGo` actual, también
> puedes copiar estos archivos ahí, en carpetas nuevas, sin que choquen con
> lo que ya tienes.

---

## Paso 2 — Conseguir tu clave GRATUITA de la API de Gemini

1. Entra a [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   con tu cuenta de Google.
2. Click en **Create API key** → **Create API key in new project**.
3. Copia la clave que te aparece.
4. **No hace falta tarjeta de crédito.** El modelo que usamos
   (`gemini-2.5-flash`) tiene una capa 100% gratuita, y con una sola llamada
   al día este proyecto está muy por debajo de cualquier límite gratuito.

> Nota: Google ajusta de vez en cuando las condiciones de su capa gratuita.
> Si en el futuro algo cambia, revisa https://ai.google.dev/gemini-api/docs/pricing.
> Mientras tanto, esto no te costará nada.

---

## Paso 3 — Crear tu bot de Telegram

1. Abre Telegram y busca al usuario **@BotFather**.
2. Envíale `/newbot` y sigue las instrucciones (nombre del bot, nombre de
   usuario terminado en "bot").
3. BotFather te dará un **token** parecido a:
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`. Cópialo.
4. Ahora busca a tu bot recién creado por su nombre de usuario y envíale
   cualquier mensaje (ej. "hola") para iniciar la conversación.
5. Para obtener tu **chat_id**, busca al bot **@userinfobot** en Telegram,
   envíale `/start`, y te dará tu ID numérico (ej. `987654321`).

---

## Paso 4 — Configurar los "Secrets" en GitHub

Estos son como contraseñas que el sistema usa, pero que nadie más puede ver.

1. En tu repositorio de GitHub, ve a **Settings** → **Secrets and variables**
   → **Actions**.
2. Click en **New repository secret** y agrega estos tres, uno por uno:

   | Nombre | Valor |
   |---|---|
   | `GEMINI_API_KEY` | La clave del Paso 2 |
   | `TELEGRAM_BOT_TOKEN` | El token del Paso 3 |
   | `TELEGRAM_CHAT_ID` | Tu ID numérico del Paso 3 |

---

## Paso 5 — Dar permiso de escritura al workflow

1. Ve a **Settings** → **Actions** → **General**.
2. Baja hasta **Workflow permissions**.
3. Selecciona **Read and write permissions**.
4. Guarda los cambios.

(Esto es necesario porque el sistema necesita guardar el briefing generado
de vuelta en el repositorio cada día.)

---

## Paso 6 — Activar GitHub Pages

1. Ve a **Settings** → **Pages**.
2. En **Source**, selecciona la rama principal (`main`) y la carpeta `/docs`.
3. Guarda. GitHub te dará una URL parecida a:
   `https://tu-usuario.github.io/pogo-briefing/pogo-briefing/`
4. Esa es la página donde verás el briefing todos los días.

---

## Paso 7 — Probarlo manualmente (sin esperar hasta mañana)

1. Ve a la pestaña **Actions** de tu repositorio.
2. Click en el workflow **"Briefing diario Pokémon GO"**.
3. Click en **Run workflow** → **Run workflow** (botón verde).
4. Espera 1-2 minutos y revisa:
   - Si te llegó el mensaje por Telegram.
   - Si la página web se actualizó.
   - Si aparece algún error, click en la ejecución para ver el detalle
     (usualmente indica qué Secret falta o está mal escrito).

---

## ¿Qué hace cada archivo?

| Archivo | Para qué sirve |
|---|---|
| `fetch_data.py` | Descarga todos los datos crudos (raids, research, eventos, noticias) |
| `generate_briefing.py` | Le pide a la IA que arme el briefing, y lo envía/publica |
| `requirements.txt` | Lista de librerías de Python necesarias |
| `.github/workflows/daily-briefing.yml` | El "reloj despertador" que corre todo cada mañana a las 8 AM |
| `data/latest.json` | Se genera solo, es el "borrador" de datos que usa la IA |
| `briefing.md` | Se genera solo, el briefing del día en texto |
| `docs/pogo-briefing/index.html` | Se genera solo, la página web del briefing |

---

## Preguntas frecuentes

**¿Puedo cambiar la hora de envío?**
Sí. Edita la línea `cron: "0 12 * * *"` en
`.github/workflows/daily-briefing.yml`. La hora está en UTC, y Venezuela es
UTC-4 todo el año (sin horario de verano), así que réstale 4 horas a la hora
que quieras en Venezuela para saber qué poner ahí.

**¿Puedo seguir usando Inoreader también?**
Sí, no hay ningún conflicto. Tu feed RSS (`pogo_news_feed.xml`) sigue
funcionando exactamente igual que antes; este sistema solo lo *lee* como una
fuente más, no lo reemplaza.

**¿Qué pasa si ScrapedDuck no tiene datos un día?**
El script sigue funcionando igual, simplemente esa sección quedará vacía y
la IA no incluirá esa parte (o dirá "Nada destacado hoy").

**¿Cuánto cuesta esto?**
Nada. La API de Gemini que usamos (`gemini-2.5-flash`) tiene una capa
gratuita real, sin tarjeta de crédito. GitHub Actions es gratis para
repositorios personales con este nivel de uso (una ejecución corta al día).
Telegram es gratis. ScrapedDuck es un proyecto público y gratuito. No hay
ningún paso en esta guía que requiera pagar.

**¿Y si algún día Gemini deja de ser gratis o cambia sus límites?**
Es la única pieza que depende de un tercero con condiciones que pueden
cambiar. Si eso pasara, el resto del sistema (los datos, Telegram, la
página web) sigue funcionando igual; solo habría que ajustar
`generate_briefing.py` para usar otro proveedor gratuito, o quitar la IA
y armar el texto directamente con Python (te puedo dar esa versión también
si lo prefieres).
