import asyncio
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from app.models import BatchSyncRequest, SyncResult
from app.repositories import IncidentRepository, get_incident_repository
from app.services import IncidentAnalyzer, get_incident_analyzer, process_incident_analysis

router = APIRouter(prefix="/sync", tags=["sync"])
Repository = Annotated[IncidentRepository, Depends(get_incident_repository)]
Analyzer = Annotated[IncidentAnalyzer, Depends(get_incident_analyzer)]


@router.post("/batch", response_model=list[SyncResult])
async def sync_batch(
    payload: BatchSyncRequest,
    repository: Repository,
    analyzer: Analyzer,
    background_tasks: BackgroundTasks,
) -> list[SyncResult]:
    results: list[SyncResult] = []
    for item in payload.incidents:
        incident, created = await asyncio.to_thread(repository.create_from_batch, item)
        if created:
            media_paths = [*item.photo_urls, *([item.video_url] if item.video_url else [])]
            background_tasks.add_task(
                process_incident_analysis,
                repository,
                analyzer,
                incident.id,
                media_paths,
                item.description,
            )
        results.append(
            SyncResult(
                incident_id=incident.id,
                client_id=incident.client_id,
                status=incident.status,
                created=created,
            )
        )
    return results
