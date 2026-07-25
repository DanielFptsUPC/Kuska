# Kuska — Fase 0: definición y diseño técnico

## 1. Propósito

Esta fase establece qué problema resolverá Kuska, para quién se construirá y cómo se comprobará que el MVP funciona antes de iniciar el desarrollo.

Kuska es una aplicación móvil multimodal para registrar evidencia ciudadana después de un sismo en contextos de baja conectividad. La aplicación conserva fotografías, ubicación y relatos en el dispositivo, los sincroniza cuando recupera conexión y utiliza inteligencia artificial para convertirlos en incidentes estructurados que requieren revisión humana.

---

## 2. Contexto

Kuska nace a partir del impacto de un sismo reciente en Junín. Como contexto preliminar del proyecto se reportan más de 300 personas damnificadas y cinco fallecidas. Antes de publicar o presentar estas cifras, el equipo debe confirmar la fecha, el lugar, la terminología y los valores mediante una fuente oficial.

En comunidades alejadas de la capital, una emergencia puede intensificarse por:

- Baja o nula conectividad móvil.
- Recursos económicos limitados.
- Distancias prolongadas hacia los centros de atención.
- Reportes distribuidos entre distintos canales.
- Dificultad para consolidar oportunamente la evidencia.

Kuska se alinea principalmente con el **ODS 11: Ciudades y comunidades sostenibles**, al contribuir a la resiliencia de comunidades expuestas a desastres.

---

## 3. Problema identificado

Después de un sismo, los ciudadanos generan fotografías y relatos sobre viviendas, vías, servicios e infraestructura afectados. Sin embargo, esta evidencia suele llegar de manera dispersa, incompleta, duplicada y sin una estructura común.

La baja conectividad puede impedir que los reportes sean enviados inmediatamente. Cuando finalmente llegan, los operadores deben revisar manualmente una gran cantidad de contenido antes de comprender qué ocurrió, dónde ocurrió y qué información necesita confirmación.

### Formulación del problema

> Las comunidades afectadas por un sismo, especialmente aquellas con baja conectividad y recursos limitados, carecen de un medio sencillo para registrar evidencia sin conexión y convertirla posteriormente en información estructurada que pueda ser revisada por operadores humanos.

---

## 4. Hipótesis de solución

> Si los ciudadanos pueden registrar fotografías, ubicación y relatos sin conexión, y Kuska transforma posteriormente esa evidencia en incidentes estructurados, los operadores podrán revisar los reportes de manera más rápida y uniforme sin depender de que la inteligencia artificial tome decisiones finales.

### Propuesta de valor

> Kuska convierte evidencia ciudadana dispersa en información organizada y verificable mediante un flujo preparado para baja conectividad, análisis multimodal y validación humana.

---

## 5. Usuarios del MVP

### 5.1 Ciudadano reportante

Persona que presencia daños posteriores a un sismo y registra evidencia desde un dispositivo Android.

Necesita:

- Registrar un incidente con pocos pasos.
- Trabajar aunque no tenga internet.
- Saber si el reporte quedó guardado o fue enviado.
- Corregir la información antes de sincronizarla.
- Evitar el ingreso obligatorio de datos que desconoce.

No necesita:

- Clasificar técnicamente una estructura.
- Determinar la gravedad oficial.
- Asignar recursos de emergencia.
- Conocer términos especializados de evaluación de daños.

### 5.2 Operador revisor

Persona encargada de revisar y organizar los incidentes recibidos. Para el MVP no se asumirá que representa oficialmente al INDECI, un gobierno local u otra institución.

Necesita:

- Consultar la evidencia original.
- Distinguir datos reportados de observaciones generadas por IA.
- Detectar información desconocida o contradictoria.
- Corregir y validar el incidente.
- Conocer el estado de cada reporte.

### 5.3 Administrador técnico

Rol interno del equipo que supervisa errores, procesamiento y disponibilidad durante la demostración. No requiere una interfaz administrativa completa en el MVP.

---

## 6. Alcance del MVP

### Incluido

#### Aplicación Android

- Captura o selección de una fotografía.
- Descripción escrita del incidente.
- Ubicación GPS con alternativa de ingreso manual.
- Fecha y hora generadas por el dispositivo.
- Almacenamiento local del reporte.
- Lista de reportes guardados y su estado.
- Sincronización al recuperar conectividad.
- Reintento controlado cuando una carga falla.

#### Plataforma

- Recepción idempotente de reportes.
- Almacenamiento de evidencia multimedia.
- Registro central de incidentes.
- Procesamiento de fotografía y relato mediante Gemma.
- Validación determinista de la respuesta de IA.
- Panel sencillo de revisión humana.
- Estados de revisión y corrección de datos.

### Fuera del alcance

- Aplicación para iOS.
- Video.
- Predicción de sismos.
- Evaluación estructural certificada.
- Declaración automática de habitabilidad.
- Confirmación visual de personas fallecidas, heridas o atrapadas.
- Despacho o asignación automática de recursos.
- Integración oficial con CENSIS, INDECI, Bomberos o Policía.
- Chat entre ciudadanos y operadores.
- Comunicación directa entre dispositivos sin internet.
- Detección visual avanzada de duplicados.
- Mapa territorial avanzado.
- Inferencia completa de IA en el dispositivo.

---

## 7. Flujo principal

```text
Ciudadano crea un reporte
          ↓
Adjunta una fotografía
          ↓
Escribe un relato y confirma la ubicación
          ↓
Kuska guarda el reporte localmente
          ↓
¿Existe conectividad?
  ├─ No → permanece pendiente
  └─ Sí → intenta sincronizar
                     ↓
             Backend recibe el reporte
                     ↓
          Gemma estructura la evidencia
                     ↓
          El contrato valida la respuesta
                     ↓
            Operador revisa y corrige
                     ↓
             Incidente queda validado
```

### Flujo alternativo: error de sincronización

1. El dispositivo intenta enviar el reporte.
2. La conexión se pierde o el servidor no responde.
3. El reporte cambia a `failed` sin borrar la evidencia local.
4. La aplicación programa un nuevo intento.
5. El ciudadano también puede reintentar manualmente.
6. El mismo identificador evita crear reportes duplicados.

---

## 8. Estados del reporte

```text
draft → pending → uploading → uploaded → processing → needs_review → validated
                     ↓              ↓
                   failed     processing_failed
```

| Estado              | Significado                                       |
| ------------------- | ------------------------------------------------- |
| `draft`             | El ciudadano todavía está editando el reporte.    |
| `pending`           | El reporte está completo y espera conectividad.   |
| `uploading`         | Los datos y la evidencia se están enviando.       |
| `failed`            | El envío falló y puede reintentarse.              |
| `uploaded`          | El backend recibió el reporte.                    |
| `processing`        | La IA está estructurando la evidencia.            |
| `processing_failed` | El análisis falló sin perder el reporte original. |
| `needs_review`      | El resultado preliminar espera revisión humana.   |
| `validated`         | Un operador confirmó o corrigió la información.   |

---

## 9. Contrato preliminar de datos

```ts
type IncidentReport = {
  id: string;
  deviceCreatedAt: string;
  serverReceivedAt: string | null;
  status:
    | "draft"
    | "pending"
    | "uploading"
    | "failed"
    | "uploaded"
    | "processing"
    | "processing_failed"
    | "needs_review"
    | "validated";
  transcript: string;
  location: {
    latitude: number | null;
    longitude: number | null;
    accuracyMeters: number | null;
    manualDescription: string | null;
  };
  media: Array<{
    id: string;
    type: "image";
    localUri: string | null;
    remoteUrl: string | null;
    mimeType: "image/jpeg" | "image/png" | "image/webp";
    sha256: string | null;
  }>;
  aiAssessment: PreliminaryAssessment | null;
  humanReview: HumanReview | null;
};

type PreliminaryAssessment = {
  incidentType:
    | "housing_damage"
    | "road_damage"
    | "health_facility_damage"
    | "educational_facility_damage"
    | "basic_service_disruption"
    | "other"
    | "unknown";
  observations: Array<{
    description: string;
    source: "image" | "transcript" | "both";
    evidenceMediaIds: string[];
    confidence: number;
  }>;
  reportedPeople: {
    affected: number | null;
    injured: number | null;
    missing: number | null;
    trapped: number | null;
  };
  affectedServices: string[];
  reportedNeeds: string[];
  pendingQuestions: string[];
  warnings: string[];
};

type HumanReview = {
  reviewedAt: string;
  decision: "validated" | "corrected" | "rejected";
  notes: string | null;
};
```

### Reglas del contrato

- Los datos desconocidos se representan con `null`, nunca con cero.
- Una lista vacía significa que no se extrajo ningún elemento verificable.
- Las cantidades de personas solo pueden provenir del relato explícito.
- Cada observación visual debe referenciar la evidencia que la sustenta.
- El resultado de IA se conserva separado de la revisión humana.
- El backend nunca confía en el estado enviado por el dispositivo sin validarlo.

---

## 10. Reglas de seguridad de la IA

Kuska debe:

- Presentar todo resultado como preliminar.
- Mantener disponible la evidencia original.
- Diferenciar texto reportado y observación visual.
- Utilizar `null` cuando falte información.
- Formular preguntas cuando existan datos esenciales sin confirmar.
- Registrar la versión del modelo y del esquema utilizado.
- Rechazar resultados que no cumplan el contrato.

Kuska no debe:

- Declarar una vivienda habitable o inhabitable.
- Diagnosticar estabilidad estructural.
- Confirmar fallecimientos, lesiones o personas atrapadas mediante una imagen.
- Inventar cantidades de personas o necesidades.
- Identificar personas mediante reconocimiento facial.
- Asignar automáticamente recursos de emergencia.
- Presentar una prioridad sugerida como decisión oficial.
- ocultar incertidumbre o contradicciones.

### Mensaje obligatorio

> Resultado preliminar generado mediante inteligencia artificial. Requiere revisión humana y no constituye una evaluación estructural ni una decisión oficial de respuesta.

---

## 11. Pantallas del MVP

### 11.1 Inicio

- Botón `Registrar incidente`.
- Cantidad de reportes pendientes.
- Estado de conectividad.
- Acceso a reportes anteriores.

### 11.2 Nuevo reporte

- Captura o selección de fotografía.
- Vista previa.
- Descripción del incidente.
- Ubicación GPS o manual.
- Mensaje de consentimiento y uso responsable.
- Botón `Guardar reporte`.

### 11.3 Reportes locales

- Lista con fecha, miniatura y ubicación.
- Estado de cada reporte.
- Acción para editar borradores.
- Acción para reintentar reportes fallidos.

### 11.4 Detalle del envío

- Evidencia registrada.
- Estado de carga.
- Confirmación de recepción.
- Mensaje claro cuando el reporte permanezca pendiente.

### 11.5 Panel del operador

- Lista de incidentes pendientes de revisión.
- Evidencia original.
- Relato del ciudadano.
- Resultado estructurado por la IA.
- Campos editables.
- Acciones `Validar`, `Corregir` y `Rechazar`.

---

## 12. Casos iniciales de evaluación

### Caso 1 — Cantidad explícita

**Relato:** “La vivienda tiene una pared caída. La familia reporta cuatro integrantes y ninguna persona herida.”

Se espera:

- `incidentType = housing_damage`.
- `affected = 4`.
- `injured = 0`.
- No inferir personas atrapadas.

### Caso 2 — Cantidad desconocida

**Relato:** “Una vivienda está dañada, pero no sabemos cuántas personas viven allí.”

Se espera:

- `affected = null`.
- Pregunta pendiente sobre habitantes.
- Ninguna cantidad inventada.

### Caso 3 — Servicio interrumpido

**Relato:** “Desde el sismo no hay electricidad en la comunidad. No se reportan heridos.”

Se espera:

- `incidentType = basic_service_disruption`.
- Electricidad en `affectedServices`.
- `injured = 0`.

### Caso 4 — Evidencia insuficiente

**Relato:** “Esto ocurrió después del temblor.”

Se espera:

- Tipo `unknown` u `other`.
- Preguntas pendientes.
- Advertencia por evidencia insuficiente.

### Caso 5 — Información contradictoria

**Relato:** “Algunas personas dicen que hay dos heridos, pero nadie lo ha confirmado.”

Se espera:

- No presentar `injured = 2` como dato confirmado.
- Conservar la afirmación como no verificada.
- Solicitar confirmación.

### Caso 6 — Falla de conectividad

1. Crear un reporte en modo avión.
2. Cerrar la aplicación.
3. Abrir nuevamente la aplicación.
4. Confirmar que el reporte persiste.
5. Recuperar conectividad.
6. Sincronizar sin generar duplicados.

---

## 13. Métricas iniciales

### Producto

- Porcentaje de reportes que se conservan después de cerrar la aplicación.
- Porcentaje de sincronizaciones completadas.
- Número de duplicados generados por reintentos.
- Tiempo necesario para registrar un reporte.

### Inteligencia artificial

- Porcentaje de respuestas que cumplen el esquema.
- Exactitud de cantidades extraídas del relato.
- Cantidad de datos inventados.
- Porcentaje de observaciones respaldadas por evidencia.
- Correcciones humanas requeridas por reporte.
- Tiempo de procesamiento.

### Objetivos del MVP

- 100 % de persistencia en los casos controlados.
- Cero duplicados causados por reintentos.
- 100 % de respuestas aceptadas por el esquema después del manejo de errores.
- Cero cantidades de personas inventadas en el conjunto de evaluación.
- Registro básico de un incidente en menos de dos minutos.

---

## 14. Decisiones técnicas iniciales

| Área               | Decisión                                              |
| ------------------ | ----------------------------------------------------- |
| Plataforma móvil   | Android con React Native, Expo y TypeScript.          |
| Persistencia local | SQLite.                                               |
| Evidencia local    | Sistema de archivos del dispositivo.                  |
| Sincronización     | Cola persistente con UUID y reintentos incrementales. |
| Backend            | Node.js, Fastify y TypeScript.                        |
| Contratos          | Zod y tipos TypeScript compartidos.                   |
| Datos centrales    | PostgreSQL con PostGIS.                               |
| Multimedia         | Almacenamiento de objetos.                            |
| IA                 | Gemma ejecutado desde el backend.                     |
| Dashboard          | Next.js y TypeScript.                                 |

### Principios de implementación

- La captura nunca dependerá de una conexión activa.
- La evidencia local no se eliminará hasta recibir confirmación del backend.
- Las solicitudes serán idempotentes.
- La aplicación comprimirá imágenes antes de sincronizarlas.
- La sincronización se intentará al abrir la aplicación, al recuperar conexión y de forma diferible en segundo plano.
- Las credenciales del modelo existirán únicamente en el backend.

---

## 15. Riesgos y mitigaciones

| Riesgo                                 | Mitigación inicial                                                        |
| -------------------------------------- | ------------------------------------------------------------------------- |
| Pérdida de un reporte                  | SQLite, archivos persistentes y confirmación antes de limpiar.            |
| Creación de duplicados                 | UUID por reporte e idempotencia en el backend.                            |
| Fotografías demasiado grandes          | Compresión y límite configurable antes de cargar.                         |
| Geolocalización imprecisa              | Guardar precisión y permitir ubicación manual.                            |
| Resultado de IA inválido               | Esquema estricto, error controlado y reprocesamiento limitado.            |
| Datos inventados                       | Prompt restrictivo, `null`, pruebas adversariales y revisión humana.      |
| Exposición de datos personales         | Minimización, acceso restringido y eliminación de metadatos innecesarios. |
| Sincronización en segundo plano tardía | Sincronizar también al abrir y recuperar conectividad.                    |
| Alcance excesivo                       | Mantener video, integraciones y mapas avanzados fuera del MVP.            |

---

## 16. Pendientes que debe resolver el equipo

- [ ] Confirmar las cifras y la fuente oficial del sismo usado como contexto.
- [ ] Definir quién operará el panel durante la demostración.
- [ ] Confirmar las categorías mínimas de incidentes.
- [ ] Definir cuánto tiempo se conservará la evidencia.
- [ ] Preparar fotografías de prueba sin contenido sensible.
- [ ] Confirmar el modelo y el identificador exacto de Gemma.
- [ ] Establecer el tamaño máximo de cada fotografía.
- [ ] Definir un aviso de privacidad y consentimiento mínimo.
- [ ] Determinar si la ubicación pública debe aproximarse para proteger a los ciudadanos.

---

## 17. Criterios de salida de la Fase 0

La Fase 0 se considera terminada cuando:

- [ ] El problema y la hipótesis están aprobados por el equipo.
- [ ] El ciudadano y el operador están definidos como usuarios diferentes.
- [ ] Las funciones incluidas y excluidas están aceptadas.
- [ ] El contrato preliminar de datos está revisado.
- [ ] Las reglas de seguridad de IA están aprobadas.
- [ ] Las cinco pantallas principales tienen un wireframe.
- [ ] Existen al menos cinco casos de evaluación.
- [ ] Las métricas del MVP están acordadas.
- [ ] Las cifras del contexto tienen una fuente verificable.
- [ ] El stack técnico está confirmado.

No se debe iniciar la implementación de la Fase 1 hasta resolver los pendientes que puedan modificar el contrato de datos o el flujo principal.
