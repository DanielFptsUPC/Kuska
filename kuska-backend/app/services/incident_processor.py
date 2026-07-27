import asyncio
import logging
from collections.abc import Awaitable, Callable
from functools import lru_cache

from app.config import get_settings
from app.models import GemmaResult, IncidentStatus, Priority
from app.repositories import IncidentRepository
from app.services.gemma_processor import GemmaIncidentAnalyzer
from supabase import create_client

IncidentAnalyzer = Callable[[list[str], str], Awaitable[GemmaResult]]
logger = logging.getLogger(__name__)


async def process_incident_analysis(
    repository: IncidentRepository,
    analyzer: IncidentAnalyzer,
    incident_id,
    media_paths: list[str],
    description: str,
) -> None:
    """Procesa Gemma después de responder al cliente y persiste el resultado."""
    try:
        result = await analyzer(media_paths, description)
        analysis_status = (
            IncidentStatus.NEEDS_REVIEW
            if result.confidence < get_settings().gemini_review_threshold
            else IncidentStatus.VALIDATED
        )
        await asyncio.to_thread(repository.save_analysis, incident_id, result, analysis_status)
    except Exception:
        logger.exception("No se pudo analizar el incidente %s", incident_id)
        await asyncio.to_thread(repository.mark_processing_failed, incident_id)


async def analyze_incident(media_paths: list[str], description: str) -> GemmaResult:
    """Simula la clasificación que entregará el módulo real de Gemma."""
    del media_paths
    normalized_description = description.casefold()

    if "atrapad" in normalized_description:
        return GemmaResult(
            type="persona_atrapada",
            damage_level="critico",
            trapped_people_possible=True,
            secondary_risks=[],
            priority=Priority.ALTA,
            explanation="La descripción indica una posible persona atrapada.",
        )
    if "incendio" in normalized_description or "fuego" in normalized_description:
        return GemmaResult(
            type="incendio",
            damage_level="severo",
            trapped_people_possible=False,
            secondary_risks=["fuego"],
            priority=Priority.ALTA,
            explanation="La descripción reporta fuego o un posible incendio.",
        )
    if "bloquead" in normalized_description or "escombro" in normalized_description:
        return GemmaResult(
            type="via_bloqueada",
            damage_level="moderado",
            trapped_people_possible=False,
            secondary_risks=[],
            priority=Priority.MEDIA,
            explanation="La descripción reporta una vía bloqueada por escombros.",
        )

    return GemmaResult(
        type="otro",
        damage_level="leve",
        trapped_people_possible=False,
        secondary_risks=[],
        priority=Priority.BAJA,
        explanation="Clasificación simulada para validar el flujo del backend.",
    )


@lru_cache
def get_incident_analyzer() -> IncidentAnalyzer:
    settings = get_settings()
    processor = settings.incident_processor.casefold()
    if processor == "mock":
        return analyze_incident
    if processor != "gemma":
        raise RuntimeError("INCIDENT_PROCESSOR debe ser 'mock' o 'gemma'")
    if not settings.genai_api_key:
        raise RuntimeError("GEMINI_API_KEY o GOOGLE_API_KEY es obligatoria para usar Gemma")
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError("Supabase debe estar configurado para cargar la evidencia")
    supabase_client = create_client(settings.supabase_url, settings.supabase_service_key)
    return GemmaIncidentAnalyzer(
        api_key=settings.genai_api_key,
        model=settings.gemini_model,
        supabase_client=supabase_client,
        bucket=settings.supabase_storage_bucket,
    )
