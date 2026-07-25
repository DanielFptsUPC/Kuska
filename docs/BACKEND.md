# Kuska — Guía Backend (Hackathon "Build with Gemma" — GDG Callao)

> Dale este archivo completo a tu asistente de IA (Claude, opencode, etc.) como contexto de arranque. El alcance funcional completo está en [`ALCANCE.md`](./ALCANCE.md) — léelo primero si necesitas más detalle de negocio.

## Contexto en una frase

Kuska recibe fotos/video/texto/GPS de un reporte ciudadano post-sismo, se lo pasa a **Gemma 4** (multimodal) para clasificarlo y priorizarlo, y expone esa información a una app móvil (offline-first) y a un dashboard web. Sprint de 1 día: 25 julio 2026, 08:30–16:30, envío a Kaggle a las 16:30 en punto.

## Equipo backend (2 personas)

- **Backend A — Gemma & Priorización** (Andrés, rama `andres`): integración con Gemma 4, prompt engineering para clasificación estructurada, motor de priorización, endpoint de detalle de incidente.
- **Backend B — Datos & Sincronización**: modelo de datos, storage de fotos/video, endpoint de ingesta/sync offline, deploy.

Trabajen sobre ramas propias y mergeen seguido a `main` (o a una rama `dev` compartida) para no bloquearse — con 4 personas y 8 horas, conflictos de integración tardíos son el mayor riesgo.

## Stack recomendado

| Capa | Elección | Por qué |
|---|---|---|
| API | **Python 3.11 + FastAPI** | Async, scaffolding rápido, y el Gemma Cookbook oficial trae ejemplos en Python — menos fricción integrando el modelo. |
| Modelo | **Gemma 4 vía Google AI Studio (Gemini API)** | Inferencia en la nube, sin GPU local, tier gratuito generoso, multimodal (imagen+video+texto) en una sola llamada. |
| DB + Storage | **Supabase** (Postgres + Storage) | Setup en minutos, sin backend de auth que construir (no se pide auth compleja), soporta geodata y guardar fotos/video directo. |
| Deploy | **Railway o Render (free tier)** | URL pública estable para que el móvil y el dashboard no dependan del wifi del local. |

Si el equipo ya domina Node más que Python, Express+TypeScript también funciona — el contrato de API de abajo es lo único que de verdad tiene que respetarse.

## Contrato de API (acordar esto en los primeros 30 minutos)

```
POST /incidents
  multipart/form-data:
    photos[]      : image files (1-N)
    video          : video file (opcional)
    description    : string
    lat, lon       : float
    client_id      : string (uuid generado en el móvil, para deduplicar en el sync)
    created_at_client : ISO 8601
  → 201 { incident_id, status: "processing" }

GET /incidents?status=&priority=&bbox=
  → 200 [{ id, lat, lon, priority, type, status, created_at, thumbnail_url }]

GET /incidents/{id}
  → 200 {
      id, description, photos[], video_url, lat, lon, created_at, status,
      gemma_result: {
        type, damage_level, trapped_people_possible,
        secondary_risks: [], priority: "alta"|"media"|"baja",
        explanation
      }
    }

POST /sync/batch
  body: [ { ...mismo payload que POST /incidents, client_id } ]
  → 200 [{ client_id, incident_id, status }]
  # Idempotente por client_id: si ya existe, no lo duplica.
```

Devuelvan siempre `client_id` en las respuestas de sync — es lo que el móvil usa para marcar localmente qué ya se subió.

## Prompt de Gemma (punto de partida)

Pídanle a Gemma que devuelva **JSON estricto** (no texto libre) para que el backend no tenga que parsear lenguaje natural:

```
Eres un sistema de apoyo a la respuesta ante desastres. Analiza la(s) foto(s)/video y la descripción
del ciudadano. Responde SOLO un JSON con este esquema exacto:
{
  "type": "colapso_estructural | grietas | incendio | persona_atrapada | via_bloqueada | otro",
  "damage_level": "leve | moderado | severo | critico",
  "trapped_people_possible": true | false,
  "secondary_risks": ["fuego", "gas", "cables_electricos", ...],
  "priority": "alta | media | baja",
  "explanation": "1-2 frases explicando el razonamiento, en español"
}
Descripción del ciudadano: "{description}"
```

Prueben esto aislado (script suelto o Google AI Studio / Colab) en la **primera hora** — es la pieza más nueva y riesgosa, y si el formato de salida falla, afecta a los 4.

## Checklist de instalación (Backend A / Andrés)

1. **Cuenta Google AI Studio** → https://aistudio.google.com → generar API key para Gemini/Gemma. Probar con un `curl` simple antes de escribir código.
2. **Python 3.11+** — verificar con `python --version`. Si no está: instalar desde python.org (marcar "Add to PATH").
3. **VS Code** — ya lo tienes. Instalar extensión "Python" y "Thunder Client" (cliente REST integrado, evita instalar Postman aparte).
4. **Git** — ya lo tienes (repo `Kuska`, rama `andres`).
5. Crear entorno virtual y proyecto FastAPI:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install fastapi uvicorn python-multipart google-genai supabase
   ```
6. **Cuenta Supabase** → https://supabase.com → crear proyecto → copiar `URL` y `anon/service key` → crear bucket de Storage para fotos/video.
7. **ngrok** (opcional pero recomendado) → https://ngrok.com → para exponer tu backend local (`ngrok http 8000`) y que el celular con Expo Go pueda pegarle sin estar en la misma red. Alternativa: deployar temprano a Railway/Render y trabajar siempre contra esa URL.
8. **No necesitas** Android Studio, Xcode ni Docker para esta parte — son cosas de frontend/mobile o de infra que no aportan velocidad hoy.

## Ritmo sugerido (alineado al cronograma del evento)

- **08:30–09:00** — Kickoff: cerrar el contrato de API de arriba con el equipo, crear proyecto Supabase, conseguir API key de Gemini, scaffold FastAPI vacío con los endpoints como stubs.
- **09:00–11:00** — Backend A: probar Gemma multimodal aislado + prompt. Backend B: schema de DB + endpoint `/sync/batch` con datos mock.
- **11:00–13:00** — Integración real: `/incidents` end-to-end con una foto de prueba, clasificación real de Gemma guardada en DB.
- **13:00–14:30** — Offline/sync robusto (idempotencia, reintentos), endpoint `/incidents/{id}` completo para el dashboard.
- **14:30–15:30** — Deploy a Railway/Render, pulir manejo de errores, datos de demo sembrados.
- **15:30–16:15** — Escribir el Writeup de Kaggle (arquitectura + uso de Gemma), verificar que el repo sea público, subir todo.
- **16:15–16:30** — Buffer. Enviar antes de las 16:30, no al filo.

## Notas de negocio a no perder de vista

- Los resultados de Gemma son **apoyo**, no verdad absoluta — no hace falta lógica de "certeza garantizada".
- No hay que construir autenticación compleja (está explícitamente fuera de alcance).
- iOS está fuera de alcance — no pierdan tiempo validando ese caso.
