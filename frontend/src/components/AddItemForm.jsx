import { useState } from "react";
import { ingestItem } from "../api.js";

export default function AddItemForm({ onSaved }) {
  const [sourceType, setSourceType] = useState("note");
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      await ingestItem({ source_type: sourceType, content });
      setContent("");
      onSaved();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Add to inbox</h2>
      <label>
        <input
          type="radio"
          checked={sourceType === "note"}
          onChange={() => setSourceType("note")}
        />
        Note
      </label>
      <label>
        <input
          type="radio"
          checked={sourceType === "url"}
          onChange={() => setSourceType("url")}
        />
        URL
      </label>
      <div>
        {sourceType === "note" ? (
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste a note..."
            rows={4}
          />
        ) : (
          <input
            type="text"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="https://example.com/article"
          />
        )}
      </div>
      <button type="submit" disabled={saving || !content.trim()}>
        {saving ? "Saving..." : "Save"}
      </button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
