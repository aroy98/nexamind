import { useEffect, useState } from "react";
import { listItems } from "./api.js";
import AddItemForm from "./components/AddItemForm.jsx";
import ItemList from "./components/ItemList.jsx";
import AskPanel from "./components/AskPanel.jsx";

export default function App() {
  const [items, setItems] = useState([]);

  function refreshItems() {
    listItems().then(setItems).catch(() => {});
  }

  useEffect(refreshItems, []);

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-5xl space-y-6 p-6 md:p-10">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AI Knowledge Inbox</h1>
          <p className="text-sm text-muted-foreground">
            Save notes and URLs, then ask questions over what you've saved.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-6">
            <AddItemForm onSaved={refreshItems} />
            <ItemList items={items} />
          </div>
          <AskPanel />
        </div>
      </div>
    </main>
  );
}
