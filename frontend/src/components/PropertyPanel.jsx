import { useEffect, useState } from "react";
import { clientApi } from "../api/client";

const TABS = [
  { id: "all", label: "All (60)" },
  { id: "lx_villas", label: "LX Villas" },
  { id: "villas", label: "Villas" },
  { id: "apartments", label: "Apartments" },
  { id: "flats", label: "Flats" },
  { id: "vacant", label: "Vacant (9)" },
];

export default function PropertyPanel({ open, onClose, vacantCount, initialTab = "all" }) {
  const [tab, setTab] = useState("all");
  const [search, setSearch] = useState("");
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    if (!open) return;
    setTab(initialTab);
    setSelected(null);
  }, [open, initialTab]);

  useEffect(() => {
    if (!open) return;
    clientApi.properties({ tab, search }).then((r) => setItems(r.data));
  }, [open, tab, search]);

  const tabs = TABS.map((t) =>
    t.id === "vacant" ? { ...t, label: `Vacant (${vacantCount ?? 9})` } : t
  );

  return (
    <>
      <div className={`panel-overlay ${open ? "open" : ""}`} onClick={onClose} />
      <div className={`slide-panel ${open ? "open" : ""}`}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 16 }}>
          <div>
            <h2 style={{ margin: 0 }}>All Properties — 60 Units</h2>
            <p style={{ margin: "4px 0 0", color: "var(--color-text-muted)", fontSize: "0.85rem" }}>
              Click any property for full detail
            </p>
          </div>
          <button type="button" className="btn-ghost" onClick={onClose}>✕</button>
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
          {tabs.map((t) => (
            <button
              key={t.id}
              type="button"
              className={tab === t.id ? "btn-primary" : "btn-ghost"}
              style={{ borderRadius: 999, fontSize: "0.8rem" }}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
          <input
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ marginLeft: "auto", padding: "8px 12px", borderRadius: 8, border: "1px solid var(--color-border)" }}
          />
        </div>
        {selected ? (
          <div className="chart-card">
            <button type="button" className="btn-ghost" onClick={() => setSelected(null)}>← Back</button>
            <h3>{selected.unit_ref} — {selected.type_label}</h3>
            <p>{selected.area}</p>
            <p>Status: <strong>{selected.status_label}</strong></p>
            <p>Rent: {selected.rent_month}</p>
            {selected.gap_year && <p className="gap-red">Gap: {selected.gap_year}</p>}
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
            {items.map((p) => (
              <div
                key={p.id}
                className="chart-card"
                style={{ padding: 0, overflow: "hidden", cursor: "pointer" }}
                onClick={() => setSelected(p)}
              >
                <div style={{ position: "relative", height: 140, background: "#e5e7eb" }}>
                  {p.photo_url && (
                    <img src={p.photo_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  )}
                  <span
                    className={`badge ${p.occupancy_status === "occupied" ? "badge-at-market" : "badge-critical"}`}
                    style={{ position: "absolute", top: 8, right: 8 }}
                  >
                    {p.status_label}
                  </span>
                </div>
                <div style={{ padding: 12 }}>
                  <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>{p.unit_ref}</div>
                  <div style={{ fontWeight: 700 }}>{p.type_label}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>{p.area}</div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
                    <span style={{ fontWeight: 600 }}>{p.rent_month}/mo</span>
                  </div>
                  {p.gap_year && (
                    <div style={{ background: "#fee2e2", color: "#b91c1c", padding: "4px 8px", borderRadius: 4, marginTop: 8, fontSize: "0.75rem" }}>
                      ~Gap: {p.gap_year}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
