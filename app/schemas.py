from pydantic import BaseModel


class GemmaResult(BaseModel):
    type: str
    damage_level: str
    trapped_people_possible: bool
    secondary_risks: list[str]
    priority: str
    explanation: str


class IncidentSummary(BaseModel):
    id: str
    lat: float
    lon: float
    priority: str | None = None
    type: str | None = None
    status: str
    created_at: str
    thumbnail_url: str | None = None


class IncidentDetail(BaseModel):
    id: str
    description: str
    photo_urls: list[str]
    video_url: str | None = None
    lat: float
    lon: float
    created_at: str
    status: str
    gemma_result: GemmaResult | None = None


class SyncResultItem(BaseModel):
    client_id: str
    incident_id: str
    status: str
