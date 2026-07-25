# Kuska — Fase 1: captura móvil offline

## 1. Objetivo

Construir y verificar el primer flujo funcional de la aplicación Android: una persona debe poder registrar un incidente con una fotografía, una descripción y una ubicación, aunque no tenga conexión a internet.

Al finalizar esta fase, el reporte deberá permanecer disponible después de cerrar o reiniciar la aplicación.

```text
Abrir Kuska
     ↓
Registrar fotografía
     ↓
Escribir descripción
     ↓
Confirmar ubicación
     ↓
Guardar en el dispositivo
     ↓
Consultar el reporte pendiente
```

Esta fase no incluye backend, sincronización real, procesamiento con Gemma, dashboard, mapas ni autenticación.

---

## 2. Resultado esperado

Una aplicación Android capaz de:

1. Solicitar permisos de cámara y ubicación de manera comprensible.
2. Capturar o seleccionar una fotografía.
3. Comprimir la imagen antes de almacenarla.
4. Escribir una descripción del incidente.
5. Obtener la ubicación GPS o aceptar una ubicación manual.
6. Guardar el reporte y sus metadatos en SQLite.
7. Conservar la fotografía en el sistema de archivos de la aplicación.
8. Mostrar una lista de reportes locales.
9. Abrir el detalle de un reporte.
10. Recuperar toda la información después de reiniciar la aplicación.

---

## 3. Alcance

### Incluido

- Proyecto móvil con React Native, Expo y TypeScript.
- Ejecución inicial en Android.
- Navegación entre inicio, formulario, lista y detalle.
- Captura desde cámara.
- Selección desde galería.
- Una fotografía por reporte.
- Descripción escrita.
- GPS con precisión registrada.
- Descripción manual de la ubicación.
- Persistencia mediante SQLite.
- Persistencia de la fotografía en el almacenamiento interno.
- Estados locales `draft` y `pending`.
- Indicador local del estado de conectividad.
- Validación del formulario.
- Pruebas en modo avión.

### Fuera del alcance

- Envío al backend.
- Sincronización automática.
- Reintentos de red.
- Análisis mediante Gemma.
- Audio o video.
- Varias fotografías por reporte.
- Mapa interactivo.
- Notificaciones.
- Inicio de sesión.
- Edición colaborativa.
- Eliminación automática de evidencia.

---

## 4. Stack de la fase

| Necesidad | Tecnología |
|---|---|
| Aplicación | React Native + Expo + TypeScript |
| Navegación | Expo Router |
| Base de datos | Expo SQLite |
| Cámara | Expo Camera |
| Galería | Expo ImagePicker |
| Archivos | Expo FileSystem |
| Compresión | Expo ImageManipulator |
| Ubicación | Expo Location |
| Conectividad | NetInfo |
| Validación | Zod |
| Estado de interfaz | Zustand |
| Pruebas unitarias | Vitest |
| Pruebas de componentes | React Native Testing Library |

### Decisión de persistencia

SQLite almacenará datos estructurados y referencias de archivos. Las fotografías no deben guardarse como BLOB dentro de SQLite durante el MVP; se conservarán como archivos y la base de datos guardará su URI local.

---

## 5. Preparación del proyecto

### 5.1 Requisitos

- Node.js LTS.
- npm.
- Android Studio con un emulador configurado o un dispositivo Android físico.
- Expo Go para pruebas iniciales.
- Git.

Para verificar:

```powershell
node --version
npm --version
git --version
```

### 5.2 Crear la aplicación

Desde la carpeta de trabajo:

```powershell
npx.cmd create-expo-app@latest kuska-mobile
Set-Location ".\kuska-mobile"
```

Seleccionar una plantilla con Expo Router y TypeScript si el asistente lo solicita.

### 5.3 Instalar dependencias nativas

```powershell
npx.cmd expo install expo-router expo-sqlite expo-camera expo-image-picker expo-file-system expo-image-manipulator expo-location
npm.cmd install @react-native-community/netinfo zustand zod
```

Para pruebas:

```powershell
npm.cmd install --save-dev vitest @testing-library/react-native
```

### 5.4 Ejecutar

```powershell
npx.cmd expo start
```

Primero comprobar el flujo en Expo Go. Antes de cerrar la fase, ejecutar también una compilación de desarrollo en Android para validar las funciones nativas utilizadas.

---

## 6. Estructura propuesta

```text
kuska-mobile/
├── app/
│   ├── _layout.tsx
│   ├── index.tsx
│   └── reports/
│       ├── new.tsx
│       ├── index.tsx
│       └── [id].tsx
├── src/
│   ├── components/
│   │   ├── ConnectivityBanner.tsx
│   │   ├── PhotoField.tsx
│   │   ├── LocationField.tsx
│   │   └── ReportCard.tsx
│   ├── db/
│   │   ├── database.ts
│   │   ├── migrations.ts
│   │   └── reports-repository.ts
│   ├── features/
│   │   └── reports/
│   │       ├── report-schema.ts
│   │       ├── report-service.ts
│   │       └── report-store.ts
│   ├── services/
│   │   ├── image-service.ts
│   │   ├── location-service.ts
│   │   └── connectivity-service.ts
│   ├── types/
│   │   └── report.ts
│   └── constants/
│       └── messages.ts
├── assets/
├── app.json
├── package.json
└── README.md
```

---

## 7. Modelo local de datos

### 7.1 Tipo de dominio

```ts
export type LocalReportStatus = "draft" | "pending";

export type LocalIncidentReport = {
  id: string;
  status: LocalReportStatus;
  transcript: string;
  latitude: number | null;
  longitude: number | null;
  accuracyMeters: number | null;
  manualLocation: string | null;
  imageId: string;
  imageLocalUri: string;
  imageMimeType: "image/jpeg" | "image/png" | "image/webp";
  imageSizeBytes: number;
  createdAt: string;
  updatedAt: string;
};
```

### 7.2 Tabla SQLite

```sql
CREATE TABLE IF NOT EXISTS incident_reports (
  id TEXT PRIMARY KEY NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft', 'pending')),
  transcript TEXT NOT NULL DEFAULT '',
  latitude REAL,
  longitude REAL,
  accuracy_meters REAL,
  manual_location TEXT,
  image_id TEXT NOT NULL,
  image_local_uri TEXT NOT NULL,
  image_mime_type TEXT NOT NULL,
  image_size_bytes INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_incident_reports_status
ON incident_reports(status);

CREATE INDEX IF NOT EXISTS idx_incident_reports_created_at
ON incident_reports(created_at DESC);
```

### Reglas

- `id` e `image_id` son UUID generados en el dispositivo.
- Las fechas utilizan ISO 8601 en UTC.
- Una coordenada ausente se almacena como `null`.
- La ubicación manual puede utilizarse sin GPS.
- Un reporte `pending` debe tener fotografía, descripción válida y alguna forma de ubicación.
- Un reporte `draft` puede estar incompleto.

---

## 8. Esquema de validación

```ts
import { z } from "zod";

export const localReportSchema = z
  .object({
    id: z.string().uuid(),
    status: z.enum(["draft", "pending"]),
    transcript: z.string().trim().max(2000),
    latitude: z.number().min(-90).max(90).nullable(),
    longitude: z.number().min(-180).max(180).nullable(),
    accuracyMeters: z.number().nonnegative().nullable(),
    manualLocation: z.string().trim().max(300).nullable(),
    imageId: z.string().uuid(),
    imageLocalUri: z.string().min(1),
    imageMimeType: z.enum(["image/jpeg", "image/png", "image/webp"]),
    imageSizeBytes: z.number().int().positive(),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
  })
  .superRefine((report, context) => {
    if (report.status !== "pending") return;

    if (report.transcript.length < 10) {
      context.addIssue({
        code: "custom",
        path: ["transcript"],
        message: "Describe el incidente con al menos 10 caracteres",
      });
    }

    const hasCoordinates =
      report.latitude !== null && report.longitude !== null;
    const hasManualLocation = Boolean(report.manualLocation?.trim());

    if (!hasCoordinates && !hasManualLocation) {
      context.addIssue({
        code: "custom",
        path: ["manualLocation"],
        message: "Indica la ubicación del incidente",
      });
    }
  });
```

La validación del formulario debe ejecutarse antes de marcar un reporte como `pending`. SQLite no sustituye la validación del dominio.

---

## 9. Manejo de fotografías

### Flujo

1. Solicitar permiso de cámara o galería.
2. Capturar o seleccionar la imagen.
3. Verificar el formato.
4. Corregir orientación si fuera necesario.
5. Redimensionar el lado mayor a un máximo inicial de 1600 píxeles.
6. Convertir preferentemente a JPEG con calidad aproximada de `0.75`.
7. Generar un UUID para la evidencia.
8. Copiar el archivo al directorio persistente de la aplicación.
9. Registrar URI, tipo y tamaño.
10. Mostrar la vista previa.

### Reglas

- No depender de la URI temporal devuelta por la cámara.
- No borrar la imagen al cerrar el formulario si el reporte fue guardado.
- No conservar metadatos EXIF innecesarios.
- No aceptar una imagen vacía o inaccesible.
- Informar claramente si el dispositivo no tiene espacio suficiente.
- Mantener la imagen original fuera del carrete, salvo que el usuario elija guardarla allí.

### Presupuesto inicial

- Formatos: JPEG, PNG o WebP.
- Tamaño objetivo: entre 500 KB y 1.5 MB.
- Límite local inicial: 5 MB después del procesamiento.
- Una imagen por reporte en esta fase.

---

## 10. Manejo de ubicación

### Flujo recomendado

1. Explicar por qué se solicita la ubicación.
2. Solicitar permiso mientras la aplicación está en uso.
3. Intentar obtener una coordenada con precisión balanceada.
4. Mostrar la precisión obtenida.
5. Permitir reintentar.
6. Permitir escribir comunidad, distrito o referencia manual.

### Casos controlados

- Permiso concedido y ubicación disponible.
- Permiso rechazado.
- GPS desactivado.
- Obtención demasiado lenta.
- Precisión baja.
- Ubicación manual sin coordenadas.

La falta de GPS no debe impedir guardar un reporte si existe una descripción manual de la ubicación.

---

## 11. Diseño de pantallas

### 11.1 Inicio

```text
┌─────────────────────────────┐
│ Kuska                       │
│ Sin conexión                │
│                             │
│ [ Registrar incidente ]     │
│                             │
│ Reportes pendientes: 2      │
│ [ Ver mis reportes ]        │
└─────────────────────────────┘
```

### 11.2 Nuevo reporte

```text
┌─────────────────────────────┐
│ Nuevo incidente             │
│                             │
│ [ Tomar fotografía ]        │
│ [ Elegir de galería ]       │
│                             │
│ [ Vista previa ]            │
│                             │
│ ¿Qué ocurrió?               │
│ [                         ] │
│                             │
│ Ubicación                   │
│ GPS: precisión 24 m         │
│ Referencia: [             ] │
│                             │
│ [ Guardar para enviar ]     │
└─────────────────────────────┘
```

### 11.3 Reportes locales

```text
┌─────────────────────────────┐
│ Mis reportes                │
│                             │
│ [foto] Vivienda dañada      │
│        Pendiente            │
│        25/07/2026 10:30     │
│                             │
│ [foto] Vía bloqueada        │
│        Borrador             │
└─────────────────────────────┘
```

### 11.4 Detalle

- Fotografía completa.
- Descripción.
- Coordenadas y referencia manual.
- Fecha del dispositivo.
- Estado local.
- Aviso: `Este reporte todavía no ha sido enviado`.

---

## 12. Experiencia en baja conectividad

La interfaz debe distinguir claramente:

- **Guardado:** existe en el dispositivo.
- **Pendiente:** está listo para sincronizar, pero aún no se envió.
- **Enviado:** no se utilizará hasta implementar la Fase 2.

### Mensajes recomendados

Sin conexión:

> No tienes conexión. Puedes registrar el incidente y Kuska lo conservará en este dispositivo.

Reporte guardado:

> Reporte guardado en este dispositivo. Se podrá enviar cuando exista conexión.

Permiso de ubicación rechazado:

> No pudimos acceder a tu ubicación. Escribe el nombre de la comunidad, distrito o una referencia cercana.

Permiso de cámara rechazado:

> Kuska necesita permiso para tomar una fotografía. También puedes seleccionar una imagen existente.

---

## 13. Plan de implementación por loops

### Loop 1 — Proyecto ejecutable

Implementar:

- Proyecto Expo con TypeScript.
- Expo Router.
- Pantalla inicial.
- Ejecución en un Android real o emulado.

Prueba:

```powershell
npx.cmd expo start
```

Criterio de salida: la pantalla inicial abre sin errores.

### Loop 2 — Base de datos local

Implementar:

- Inicialización de SQLite.
- Migración `001_create_incident_reports`.
- Repositorio para crear, consultar y actualizar reportes.
- Activación de claves foráneas y modo WAL.

Pruebas:

- Crear un reporte de prueba.
- Cerrar la aplicación.
- Abrirla nuevamente.
- Confirmar que el reporte existe.

Criterio de salida: la persistencia sobrevive al reinicio.

### Loop 3 — Captura y persistencia de imagen

Implementar:

- Permisos.
- Cámara y galería.
- Compresión.
- Copia al directorio persistente.
- Vista previa.

Pruebas:

- Tomar una fotografía.
- Seleccionar otra desde la galería.
- Reiniciar la aplicación.
- Confirmar que la imagen continúa disponible.

Criterio de salida: ninguna URI temporal queda como evidencia definitiva.

### Loop 4 — Ubicación

Implementar:

- Permiso de ubicación.
- Obtención de coordenadas.
- Precisión.
- Alternativa manual.

Pruebas:

- GPS disponible.
- Permiso rechazado.
- GPS desactivado.
- Solo ubicación manual.

Criterio de salida: el reporte puede completarse en los cuatro escenarios.

### Loop 5 — Formulario completo

Implementar:

- Fotografía.
- Descripción.
- Ubicación.
- Validación.
- Guardado como `pending`.
- Guardado parcial como `draft`, si el tiempo lo permite.

Pruebas negativas:

- Sin fotografía.
- Descripción menor a 10 caracteres.
- Sin GPS ni referencia manual.
- Imagen inaccesible.

Criterio de salida: solo los reportes válidos cambian a `pending`.

### Loop 6 — Lista y detalle

Implementar:

- Lista ordenada por fecha descendente.
- Miniatura.
- Estado.
- Navegación al detalle.
- Estado vacío.

Criterio de salida: todos los reportes guardados pueden consultarse sin conexión.

### Loop 7 — Validación en modo avión

Ejecutar el flujo vertical:

1. Activar modo avión.
2. Abrir Kuska.
3. Registrar una fotografía.
4. Escribir una descripción.
5. Utilizar GPS si está disponible o escribir la ubicación.
6. Guardar el reporte.
7. Cerrar la aplicación completamente.
8. Abrir Kuska.
9. Verificar el reporte y su fotografía.

Criterio de salida: no se pierde ningún dato y la interfaz nunca afirma que el reporte fue enviado.

---

## 14. Pruebas mínimas

### Unitarias

- El esquema acepta un reporte `pending` válido.
- El esquema rechaza un reporte sin fotografía.
- El esquema rechaza una descripción demasiado corta.
- El esquema acepta ubicación manual sin GPS.
- El esquema rechaza coordenadas fuera de rango.
- El repositorio inserta y recupera un reporte.
- El repositorio ordena por fecha descendente.

### Integración

- La fotografía procesada existe en el almacenamiento persistente.
- El registro SQLite apunta a un archivo accesible.
- Una actualización conserva `createdAt` y modifica `updatedAt`.
- Reiniciar la aplicación no elimina reportes.

### Manuales en Android

| Caso | Resultado esperado |
|---|---|
| Modo avión | Permite guardar y consultar. |
| Permiso de cámara rechazado | Explica el problema y ofrece galería. |
| Permiso de galería rechazado | Permite volver a solicitar o usar cámara. |
| Permiso GPS rechazado | Ofrece ubicación manual. |
| Aplicación cerrada | El reporte persiste. |
| Imagen grande | Se comprime sin congelar la interfaz. |
| Descripción inválida | Muestra el error junto al campo. |
| Sin espacio disponible | Muestra error y no crea un registro inconsistente. |

---

## 15. Criterios de rendimiento

Validar en un Android de gama baja o media:

- La pantalla inicial debe ser utilizable en menos de 3 segundos.
- Las listas no deben cargar imágenes en resolución completa.
- La compresión no debe bloquear permanentemente la interfaz.
- La base de datos debe utilizar operaciones asíncronas.
- Las consultas de lista deben estar paginadas o limitadas.
- La fotografía procesada no debe superar 5 MB.
- El formulario debe conservar sus datos mientras se procesa la imagen.

No utilizar operaciones SQLite síncronas para tareas pesadas en la interfaz.

---

## 16. Privacidad y seguridad

- Explicar el uso de cámara y ubicación antes de solicitar permisos.
- No solicitar acceso permanente a la ubicación.
- No realizar reconocimiento facial.
- Evitar nombres, documentos o teléfonos en el formulario inicial.
- No mostrar coordenadas exactas en una futura vista pública.
- No registrar rutas locales ni relatos completos en servicios de errores.
- No borrar evidencia automáticamente en esta fase.
- Utilizar consultas parametrizadas para SQLite.

Texto inicial sugerido:

> Registra únicamente información relacionada con el incidente. Evita fotografiar rostros, documentos u otros datos personales cuando no sean necesarios.

---

## 17. Evidencias de finalización

Conservar:

- Captura de la pantalla inicial.
- Captura del formulario completo.
- Captura de la lista de reportes pendientes.
- Captura del detalle después de reiniciar la aplicación.
- Video corto del flujo en modo avión.
- Resultado de las pruebas automatizadas.
- Modelo y versión del dispositivo utilizado.
- Tamaño de la fotografía antes y después de comprimirla.

Las evidencias no deben mostrar víctimas, rostros ni información personal.

---

## 18. Definición de terminado

La Fase 1 estará terminada cuando:

- [ ] La aplicación abre en un dispositivo Android.
- [ ] La navegación principal funciona.
- [ ] Es posible capturar o seleccionar una fotografía.
- [ ] La imagen se comprime y se copia a almacenamiento persistente.
- [ ] Se puede ingresar una descripción.
- [ ] Se obtiene GPS o se acepta ubicación manual.
- [ ] El reporte válido se guarda como `pending`.
- [ ] Los datos estructurados están en SQLite.
- [ ] La fotografía permanece accesible después de reiniciar.
- [ ] La lista muestra los reportes locales.
- [ ] El detalle muestra toda la evidencia guardada.
- [ ] El modo avión no impide registrar el incidente.
- [ ] La interfaz diferencia entre guardado y enviado.
- [ ] Las pruebas unitarias pasan.
- [ ] Se completó la prueba vertical en un Android real o emulado.

---

## 19. Entregables

- Código fuente de `kuska-mobile`.
- Migración inicial de SQLite.
- Esquema Zod del reporte local.
- Repositorio de persistencia.
- Servicio de fotografías.
- Servicio de ubicación.
- Pantallas de inicio, formulario, lista y detalle.
- Pruebas automatizadas.
- Evidencia de ejecución en modo avión.
- Registro de problemas conocidos.

---

## 20. Puerta de entrada a la Fase 2

No comenzar la sincronización hasta confirmar que:

1. El identificador UUID se genera una sola vez por reporte.
2. La fotografía está en una ruta persistente.
3. El reporte sobrevive al reinicio.
4. Los estados `draft` y `pending` están bien diferenciados.
5. La ubicación puede ser manual.
6. La aplicación no depende de internet para ninguna operación de esta fase.

La Fase 2 incorporará backend, carga de evidencia, idempotencia, cola de sincronización y reintentos de red.

