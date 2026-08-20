import logging

from fastapi import APIRouter

from app.answering import answer_question
from app.chunking import chunk_text
from app.embeddings import embed_texts
from app.ingestion import validate_and_extract
from app.retrieval import top_k_chunks
from app.schemas import IngestRequest, IngestResponse, ItemsResponse, QueryRequest, QueryResponse
from app.storage import insert_chunks, insert_item, list_items

router = APIRouter()
logger = logging.getLogger("app.routes")


@router.post("/ingest", response_model=IngestResponse, status_code=201)
def ingest(request: IngestRequest):
    raw_content, source_url, title = validate_and_extract(request.source_type, request.content)

    chunks = chunk_text(raw_content)
    embeddings = embed_texts(chunks)

    item_id = insert_item(request.source_type, raw_content, source_url, title)
    insert_chunks(item_id, chunks, embeddings)

    logger.info("item ingested", extra={"extra_fields": {"item_id": item_id, "chunk_count": len(chunks)}})

    with_item = list_items()[0]  # newest first, just inserted
    return IngestResponse(**with_item, chunk_count=len(chunks))


@router.get("/items", response_model=ItemsResponse)
def get_items():
    return ItemsResponse(items=list_items())


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    question = request.question.strip()
    if not question:
        raise ValueError("question must not be empty")

    [query_embedding] = embed_texts([question])
    matches = top_k_chunks(query_embedding)
    answer, sources = answer_question(question, matches)

    logger.info(
        "question answered",
        extra={"extra_fields": {"question_length": len(question), "retrieval_hits": len(matches)}},
    )
    return QueryResponse(answer=answer, sources=sources)
