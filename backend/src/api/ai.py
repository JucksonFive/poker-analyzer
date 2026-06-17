"""AI Assistant API endpoints.

POST /api/ai/query  — ask a natural language question about poker data
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.database import get_db
from backend.src.models.schemas import AIQuery, AIResponse
from backend.src.services.ai_service import AIService

router = APIRouter()


@router.post("/query", response_model=AIResponse)
async def ask_ai(
    query: AIQuery,
    db: Session = Depends(get_db),
):
    """Ask a natural language question about your poker data.

    The AI assistant translates your question into SQL, executes it
    read-only against your local database, and returns a natural
    language answer with supporting data.

    Example questions:
    - "What is my VPIP over the last month?"
    - "Which position am I losing the most money from?"
    - "Show me my biggest winning and losing hands this week"
    """
    service = AIService(db)
    result = await service.query(query.question)
    return AIResponse(**result)
