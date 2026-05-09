"""
Documents router — serves document search and listing.
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.pdf_service import search_documents, list_documents

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/")
async def list_docs():
    """List all indexed PDF documents."""
    try:
        return {"documents": list_documents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_docs(q: str = Query(..., min_length=2), top_k: int = Query(default=5, le=10)):
    """Search document content by keyword."""
    try:
        results = search_documents(q, top_k=top_k)
        return {"query": q, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
