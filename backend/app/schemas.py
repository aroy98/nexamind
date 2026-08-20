from typing import Literal

from pydantic import BaseModel


class IngestRequest(BaseModel):
    source_type: Literal["note", "url"]
    content: str


class IngestResponse(BaseModel):
    id: int
    source_type: str
    title: str | None
    source_url: str | None
    created_at: str
    chunk_count: int


class ItemSummary(BaseModel):
    id: int
    source_type: str
    title: str | None
    source_url: str | None
    created_at: str


class ItemsResponse(BaseModel):
    items: list[ItemSummary]


class QueryRequest(BaseModel):
    question: str


class SourceSnippet(BaseModel):
    item_id: int
    title: str | None
    source_type: str
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
