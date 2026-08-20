async function handleResponse(response) {
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error || "Request failed");
  }
  return body;
}

export function ingestItem({ source_type, content }) {
  return fetch("/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_type, content }),
  }).then(handleResponse);
}

export function listItems() {
  return fetch("/items").then(handleResponse).then((body) => body.items);
}

export function askQuestion(question) {
  return fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  }).then(handleResponse);
}
