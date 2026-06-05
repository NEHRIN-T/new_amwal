import { useMemo, useState } from "react";
import { Bar, BarChart, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { clientApi } from "../api/client";
import KpiCard from "../components/KpiCard";
import PageHeader from "../components/PageHeader";
import { usePoll } from "../hooks/usePoll";

export default function RentalIntelligence() {
  const { data } = usePoll(() => clientApi.rental(), 30000);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const kpis = data?.kpis;

  const filtered = useMemo(() => {
    let rows = data?.units || [];
    if (filter !== "all") rows = rows.filter((r) => r.status === filter);
    if (search) {
      const q = search.toLowerCase();
      rows = rows.filter(
        (r) =>
          r.unit_ref?.toLowerCase().includes(q) ||
          r.area?.toLowerCase().includes(q) ||
          r.type_label?.toLowerCase().includes(q)
      );
    }
    return rows;
  }, [data, filter, search]);

  const gapChart = (data?.gap_by_type || []).map((g) => ({
    name: g.category,
    current: g.current_fils / 100,
    market: g.market_fils / 100,
  }));

  return (
    <>
      <PageHeader title="RENTAL INTELLIGENCE" />
      <div className="banner">ILLUSTRATIVE SCENARIO - All data assumption-based.</div>
      <div className="kpi-grid">
        <KpiCard label="EST. LEAKAGE / YR" value={kpis?.leakage_yr} sub="Assumed Cap vs Market" />
        <KpiCard label="UNITS BELOW MARKET" value={kpis?.units_below_market} sub={`${kpis?.units_below_pct}% of Portfolio`} />
        <KpiCard label="AVG GAP / UNIT / YR" value={kpis?.avg_gap_yr} sub="Below-market average" />
        <KpiCard label="AT OR ABOVE MARKET" value={kpis?.at_or_above_market} sub={`${kpis?.at_or_above_pct}% of Portfolio`} />
      </div>
      <div className="chart-grid-2">
        <div className="chart-card">
          <h3>Gap by Property Type</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={gapChart}>
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(v) => `${v / 1000}K`} />
              <Tooltip />
              <Legend />
              <Bar dataKey="current" fill="#22c55e" name="Current" />
              <Bar dataKey="market" fill="#3b82f6" name="Market" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Rent Gap Distribution</h3>
          {(data?.gap_distribution || []).map((b) => (
            <div key={b.band} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem" }}>
                <span>{b.band}</span>
                <span>{b.count} units</span>
              </div>
              <div style={{ height: 10, background: "#e5e7eb", borderRadius: 4 }}>
                <div
                  style={{
                    width: `${Math.min(100, (b.count / 20) * 100)}%`,
                    height: "100%",
                    background: b.color,
                    borderRadius: 4,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="chart-card">
        <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
          {["all", "critical", "review", "at_market"].map((f) => (
            <button
              key={f}
              type="button"
              className={filter === f ? "btn-primary" : "btn-ghost"}
              onClick={() => setFilter(f)}
            >
              {f === "all" ? "All (60)" : f.charAt(0).toUpperCase() + f.slice(1).replace("_", " ")}
            </button>
          ))}
          <input
            placeholder="Search unit, type, area..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ marginLeft: "auto", padding: 8, borderRadius: 8, border: "1px solid var(--color-border)" }}
          />
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Unit Ref</th>
              <th>Type</th>
              <th>Area</th>
              <th>Mkt Rent</th>
              <th>Curr Rent</th>
              <th>Gap / Yr</th>
              <th>Last Review</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row) => (
              <tr key={row.unit_ref}>
                <td>{row.unit_ref}</td>
                <td>{row.type_label}</td>
                <td>{row.area}</td>
                <td>{row.market_rent}</td>
                <td>{row.current_rent}</td>
                <td className="gap-red">{row.gap_yr}</td>
                <td>{row.last_review}</td>
                <td>
                  <span className={`badge badge-${row.status === "critical" ? "critical" : row.status === "review" ? "monitor" : "at-market"}`}>
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
