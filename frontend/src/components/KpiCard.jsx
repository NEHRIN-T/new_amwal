export default function KpiCard({ label, value, sub, onClick, className = "" }) {
  return (
    <div
      className={`kpi-card ${className} ${onClick ? "clickable" : ""}`}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      onKeyDown={onClick ? (e) => e.key === "Enter" && onClick() : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={onClick ? { cursor: "pointer" } : undefined}
    >
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}
