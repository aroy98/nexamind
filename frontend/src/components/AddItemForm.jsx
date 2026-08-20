import { useState } from "react";
import { ingestItem } from "../api.js";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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
    <Card>
      <CardHeader>
        <CardTitle>Add to inbox</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-2">
            <Button
              type="button"
              size="sm"
              variant={sourceType === "note" ? "default" : "outline"}
              onClick={() => setSourceType("note")}
            >
              Note
            </Button>
            <Button
              type="button"
              size="sm"
              variant={sourceType === "url" ? "default" : "outline"}
              onClick={() => setSourceType("url")}
            >
              URL
            </Button>
          </div>

          <div className="space-y-2">
            <Label htmlFor="content">{sourceType === "note" ? "Note text" : "URL"}</Label>
            {sourceType === "note" ? (
              <Textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste a note..."
                rows={4}
              />
            ) : (
              <Input
                id="content"
                type="text"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="https://example.com/article"
              />
            )}
          </div>

          <Button type="submit" disabled={saving || !content.trim()}>
            {saving ? "Saving..." : "Save"}
          </Button>

          {error && (
            <p role="alert" className="text-sm text-destructive">
              {error}
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
