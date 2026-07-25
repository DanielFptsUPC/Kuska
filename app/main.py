import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .db import supabase, upload_media
from .gemma import classify_incident
from .schemas import IncidentDetail, IncidentSummary, SyncResultItem

app = FastAPI(title="Kuska API")

# Abierto para el sprint: dashboard y app movil pegan desde origenes distintos
# (localhost, Vercel, Expo). No hay datos sensibles de usuario en juego.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Andres: ingesta + clasificacion Gemma ---
@app.post("/incidents")
async def create_incident(
    photos: list[UploadFile] = File(...),
    video: UploadFile | str | None = File(None),
    description: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    client_id: str = Form(...),
    created_at_client: str = Form(...),
):
    # Swagger manda "" en vez de omitir el campo cuando "Send empty value" queda marcado.
    if isinstance(video, str):
        video = None

    photo_bytes_list = [await p.read() for p in photos]
    photo_urls = [
        upload_media(f"{client_id}/photo_{i}.jpg", data, "image/jpeg")
        for i, data in enumerate(photo_bytes_list)
    ]

    video_url = None
    if video is not None:
        video_bytes = await video.read()
        video_url = upload_media(f"{client_id}/video.mp4", video_bytes, "video/mp4")

    gemma_result = classify_incident(photo_bytes_list, description)

    row = {
        "client_id": client_id,
        "description": description,
        "photo_urls": photo_urls,
        "video_url": video_url,
        "lat": lat,
        "lon": lon,
        "status": "done",
        "gemma_result": gemma_result,
        "created_at_client": created_at_client,
    }
    result = supabase.table("incidents").upsert(row, on_conflict="client_id").execute()
    incident_id = result.data[0]["id"]

    return {"incident_id": incident_id, "status": "done"}


# --- Andres: detalle con resultado de Gemma, para el dashboard ---
@app.get("/incidents/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: str):
    result = supabase.table("incidents").select("*").eq("id", incident_id).single().execute()
    return result.data


# --- Daniel: listado para mapa/lista del dashboard ---
@app.get("/incidents", response_model=list[IncidentSummary])
def list_incidents(status: str | None = None, priority: str | None = None):
    query = supabase.table("incidents").select("*")
    if status:
        query = query.eq("status", status)
    result = query.execute()

    rows = result.data
    if priority:
        rows = [r for r in rows if (r.get("gemma_result") or {}).get("priority") == priority]

    return [
        {
            "id": r["id"],
            "lat": r["lat"],
            "lon": r["lon"],
            "priority": (r.get("gemma_result") or {}).get("priority"),
            "type": (r.get("gemma_result") or {}).get("type"),
            "status": r["status"],
            "created_at": r["created_at"],
            "thumbnail_url": (r.get("photo_urls") or [None])[0],
        }
        for r in rows
    ]


# --- Daniel: ingesta batch para la cola offline del movil ---
@app.post("/sync/batch", response_model=list[SyncResultItem])
async def sync_batch(items: list[dict]):
    results = []
    for item in items:
        existing = (
            supabase.table("incidents")
            .select("id")
            .eq("client_id", item["client_id"])
            .execute()
        )
        if existing.data:
            results.append(
                {"client_id": item["client_id"], "incident_id": existing.data[0]["id"], "status": "done"}
            )
            continue

        row = {**item, "id": str(uuid.uuid4()), "synced_at": datetime.now(timezone.utc).isoformat()}
        inserted = supabase.table("incidents").insert(row).execute()
        results.append(
            {"client_id": item["client_id"], "incident_id": inserted.data[0]["id"], "status": "done"}
        )

    return results
