export default function ItemList({ items }) {
  return (
    <div>
      <h2>Saved items</h2>
      {items.length === 0 ? (
        <p>Nothing saved yet.</p>
      ) : (
        <ul>
          {items.map((item) => (
            <li key={item.id}>
              <span>[{item.source_type}]</span> {item.title}{" "}
              <time>{new Date(item.created_at).toLocaleString()}</time>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
