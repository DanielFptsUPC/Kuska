# Kuska — Guía Frontend (Hackathon "Build with Gemma" — GDG Callao)

> Dale este archivo completo a tu asistente de IA (Claude, opencode, etc.) como contexto de arranque. El alcance funcional completo está en [`ALCANCE.md`](./ALCANCE.md) — léelo primero si necesitas más detalle de negocio.

## Contexto en una frase

Kuska recibe fotos/video/texto/GPS de un reporte ciudadano post-sismo, el backend se lo pasa a **Gemma 4** para clasificarlo y priorizarlo, y esa información se muestra en una app móvil (offline-first, para capturar reportes) y un dashboard web (para que un operador vea el mapa de incidentes). Sprint de 1 día: 25 julio 2026, 08:30–16:30, envío a Kaggle a las 16:30 en punto.

## Equipo frontend (2 personas)

- **Frontend A — App móvil**: captura de foto/video/texto/GPS, almacenamiento local, cola de sincronización offline-first.
- **Frontend B — Dashboard web**: mapa de incidentes, lista priorizada, vista de detalle con evidencia y explicación de Gemma.

## Stack recomendado

| Capa | Elección | Por qué |
|---|---|---|
| App móvil | **React Native + Expo** (managed workflow) | Se prueba en un celular real con la app **Expo Go** escaneando un QR — **no necesitas instalar Android Studio ni emulador**. Tiene módulos listos para cámara, video, GPS y storage local. |
| Dashboard | **Next.js + React** | Deploy gratis e instantáneo en Vercel, requisito del hackathon es demo pública sin login. |
| Mapa | **Leaflet** (react-leaflet) con OpenStreetMap | Gratis, sin API key, suficiente para un mapa de pines con prioridad por color. |

## Contrato de API (el mismo que usa el equipo de backend)

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
```

Mientras el backend no esté listo, **no esperen** — mockeen estas respuestas con datos falsos y avancen la UI en paralelo. Cambien la URL base a la real apenas el equipo de backend deploye.

## App móvil — qué construir

1. Pantalla de captura: cámara (foto obligatoria, video opcional), campo de texto para descripción, GPS automático (pedir permiso de ubicación).
2. Guardar el reporte **localmente primero** (no bloquear al usuario esperando red) — usar `expo-file-system` para los archivos y `expo-sqlite` o `AsyncStorage` para la cola de reportes pendientes.
3. Servicio de sync: cuando detecte conexión (`@react-native-community/netinfo`), sube los reportes pendientes vía `POST /sync/batch` y marca como sincronizados los que el backend confirme.
4. Pantalla simple de "mis reportes" con estado (pendiente / sincronizado / procesado).

## Dashboard — qué construir

1. Mapa con pines de incidentes (color por prioridad: rojo=alta, amarillo=media, verde=baja), usando `GET /incidents`.
2. Lista lateral ordenada por prioridad.
3. Vista de detalle al hacer click en un incidente: fotos/video, descripción, y el bloque `gemma_result` (tipo, nivel de daño, riesgos, explicación).
4. Nada de login — es explícitamente parte del alcance no tener auth compleja.

## Checklist de instalación

### Para quien haga la app móvil
1. **Node.js LTS** (v20+) → https://nodejs.org
2. Instalar Expo CLI (no requiere instalación global, se usa con `npx`):
   ```bash
   npx create-expo-app kuska-mobile
   cd kuska-mobile
   npx expo install expo-camera expo-location expo-file-system expo-sqlite
   ```
3. Instalar la app **Expo Go** en tu celular (Play Store) — al correr `npx expo start` aparece un QR, lo escaneas y la app corre en tu teléfono real, en vivo.
4. **No necesitas Android Studio** salvo que al final quieran generar un `.apk` instalable para la demo — eso se hace con `eas build` (Expo Application Services) sin instalar nada pesado localmente. Para la demo del día, correr vía Expo Go o grabar un video es suficiente y más rápido.

### Para quien haga el dashboard
1. **Node.js LTS** (v20+) — mismo que arriba.
2. ```bash
   npx create-next-app@latest kuska-dashboard
   cd kuska-dashboard
   npm install leaflet react-leaflet
   ```
3. Cuenta en **Vercel** (vercel.com, login con GitHub) para deployar con un click y tener URL pública — requisito del hackathon.

## Ritmo sugerido (alineado al cronograma del evento)

- **08:30–09:00** — Kickoff: cerrar el contrato de API con backend, `npx create-expo-app` y `npx create-next-app` ya corriendo, celulares con Expo Go instalado.
- **09:00–11:00** — UI base con datos mockeados: pantalla de captura (móvil) y mapa+lista (dashboard).
- **11:00–13:00** — Conectar a backend real (`POST /incidents`, `GET /incidents`).
- **13:00–14:30** — Offline-first real en móvil (cola local + sync); dashboard con vista de detalle completa.
- **14:30–15:30** — Pulido visual, manejo de estados de carga/error, probar el flujo completo dos veces.
- **15:30–16:15** — Deploy final del dashboard a Vercel (URL pública, sin login), grabar video de respaldo de la app móvil funcionando.
- **16:15–16:30** — Buffer. Confirmar que los links del Writeup de Kaggle funcionan sin login antes de las 16:30.

## Notas de negocio a no perder de vista

- **Offline-first no es opcional** — es uno de los 6 puntos del "resultado esperado" del proyecto: debe poder registrar un incidente sin conexión y sincronizar después.
- No hay que construir autenticación compleja (fuera de alcance).
- Solo Android — iOS está fuera de alcance, no pierdan tiempo ahí.
