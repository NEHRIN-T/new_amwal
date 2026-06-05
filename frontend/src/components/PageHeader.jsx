export default function PageHeader({ title, onExport }) {
  return (
    <div className="page-header">
      <h1 className="page-title">{title}</h1>
      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        <span style={{ fontSize: "0.75rem", color: "#dc2626" }}>● Illustrative data</span>
        <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>March 2026</span>
        <button type="button" className="btn-ghost" onClick={onExport}>Export</button>
        <button type="button" className="btn-primary">+ Ask AI</button>
      </div>
    </div>
  );
}
