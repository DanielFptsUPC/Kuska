# Kuska — Backend

API (FastAPI) para el MVP de Kuska. El frontend (móvil + dashboard) vive en otro repositorio.

Contexto de negocio completo en [docs/ALCANCE.md](docs/ALCANCE.md); guía de trabajo del equipo backend en [docs/BACKEND.md](docs/BACKEND.md).

## Primera vez

```bash
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y rellena tus llaves (Google AI Studio + Supabase).

## Correr

```bash
uvicorn app.main:app --reload
```

Swagger interactivo: http://localhost:8000/docs
