"""
Chat router — handles conversational AI requests.
"""
import logging
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, Request

from app.services.ai_service import run_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list)

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v):
        # Strip leading/trailing whitespace
        return v.strip()


class ToolTraceItem(BaseModel):
    tool: str
    input: dict
    result_preview: str


class ChatResponse(BaseModel):
    answer: str
    tool_trace: List[ToolTraceItem]
    model: str
    sources_used: List[str]


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Accepts a user message and conversation history.
    Returns Claude's answer with full tool trace for transparency.
    """
    try:
        messages = [{"role": "user", "content": request.message}]
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in (request.conversation_history or [])
        ]

        result = run_chat(messages=messages, conversation_history=history)

        # Extract unique sources from tool trace
        sources = list({item["tool"] for item in result["tool_trace"]})

        return ChatResponse(
            answer=result["answer"],
            tool_trace=[ToolTraceItem(**t) for t in result["tool_trace"]],
            model=result["model"],
            sources_used=sources,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/suggested-questions")
async def get_suggested_questions():
    """Return example questions users can ask."""
    return {
        "questions": [
            "Which titles performed best in 2025?",
            "Why is Stellar Run trending recently?",
            "Compare Dark Orbit vs Last Kingdom",
            "Which city had the strongest engagement last month?",
            "What explains weak comedy performance?",
            "What recommendations would you give for leadership?",
            "Which genre is growing fastest?",
            "What audience segments are most engaged?",
        ]
    }
