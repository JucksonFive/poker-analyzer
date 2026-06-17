"""Hand history import API endpoints.

POST   /api/import/upload  — upload and import a hand history file
GET    /api/import/logs     — import history
GET    /api/import/formats  — supported formats list
"""

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from backend.src.database import get_db
from backend.src.models.schemas import ImportResult
from backend.src.services.import_service import ImportService

router = APIRouter()

# Max file size: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024

ALLOWED_EXTENSIONS = {".txt", ".hh", ".xml"}


@router.post("/upload")
async def upload_hand_history(
    file: UploadFile = File(...),
    site: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """Upload and import a hand history file.

    Returns SSE stream with import progress events.
    """
    # Validate file extension
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Save to temp file for processing
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=suffix, delete=False, mode="wb"
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    service = ImportService(db)

    async def event_generator():
        try:
            async for event in service.import_file(tmp_path, site=site):
                yield {"event": "progress", "data": json.dumps(event)}
        finally:
            # Clean up temp file
            tmp_path.unlink(missing_ok=True)
        yield {
            "event": "complete",
            "data": json.dumps({"status": "completed"}),
        }

    return EventSourceResponse(event_generator())


@router.get("/logs")
async def get_import_logs(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """Get history of hand history imports."""
    # TODO: Implement import log retrieval
    return {"logs": [], "total": 0, "page": page, "page_size": page_size}


@router.get("/formats")
async def get_supported_formats():
    """List all supported hand history formats."""
    from backend.src.importers.registry import PARSER_REGISTRY

    return {
        "formats": [
            {"site": name, "status": "MVP" if name in ("PokerStars", "GGPoker", "Ignition") else "Post-MVP"}
            for name in PARSER_REGISTRY
        ]
    }
