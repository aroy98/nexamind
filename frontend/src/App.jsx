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
    <main>
      <h1>AI Knowledge Inbox</h1>
      <AddItemForm onSaved={refreshItems} />
      <ItemList items={items} />
      <AskPanel />
    </main>
  );
}
