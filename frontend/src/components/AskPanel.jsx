import { useState } from "react";
import { askQuestion } from "../api.js";

export default function AskPanel() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const response = await askQuestion(question);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Ask a question</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What did I save about...?"
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>
      {error && <p role="alert">{error}</p>}
      {result && (
        <div>
          <p>{result.answer}</p>
          {result.sources.length > 0 && (
            <ul>
              {result.sources.map((source, i) => (
                <li key={i}>
                  <strong>{source.title}</strong>: {source.snippet}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
