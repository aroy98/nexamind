def test_ingest_note(client):
    response = client.post("/ingest", json={"source_type": "note", "content": "The sky is blue."})
    assert response.status_code == 201
    body = response.json()
    assert body["chunk_count"] >= 1
    assert body["source_type"] == "note"


def test_ingest_invalid_url(client):
    response = client.post("/ingest", json={"source_type": "url", "content": "not-a-url"})
    assert response.status_code == 422
    assert "error" in response.json()


def test_ingest_empty_note(client):
    response = client.post("/ingest", json={"source_type": "note", "content": "   "})
    assert response.status_code == 422


def test_query_empty_question(client):
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422


def test_query_no_relevant_content(client):
    response = client.post("/query", json={"question": "anything, inbox is empty"})
    assert response.status_code == 200
    body = response.json()
    assert body["sources"] == []


def test_list_items_empty_and_populated(client):
    assert client.get("/items").json()["items"] == []

    client.post("/ingest", json={"source_type": "note", "content": "First note"})
    client.post("/ingest", json={"source_type": "note", "content": "Second note"})

    items = client.get("/items").json()["items"]
    assert len(items) == 2
    assert items[0]["title"].startswith("Second")  # newest first
