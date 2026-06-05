import { useState } from "react";
import { Area, AreaChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { clientApi } from "../api/client";
import KpiCard from "../components/KpiCard";
import PageHeader from "../components/PageHeader";
import PropertyPanel from "../components/PropertyPanel";
import { usePoll } from "../hooks/usePoll";

function OccupancyBars({ rows }) {
  return (
    <div>
      {(rows || []).map((r) => (
        <div key={r.label} style={{ marginBottom: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem" }}>
            <span>{r.label}</span>
            <span>{r.display}</span>
          </div>
          <div style={{ height: 8, background: "#e5e7eb", borderRadius: 4, marginTop: 4 }}>
            <div style={{ width: r.percent + "%", height: "100%", background: r.color, borderRadius: 4 }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function PortfolioOverview() {
  const { data } = usePoll(() => clientApi.portfolio(), 30000);
  const [panelOpen, setPanelOpen] = useState(false);
  const [panelTab, setPanelTab] = useState("all");
  const kpis = data?.kpis;
  const trend = data?.income_trend || [];
  const openPanel = (tab = "all") => {
    setPanelTab(tab);
    setPanelOpen(true);
  };

  return (
    <>
      <PageHeader title="PORTFOLIO OVERVIEW" />
      <div className="banner">ILLUSTRATIVE SCENARIO - All figures assumption-based.</div>
      <div className="kpi-grid">
        <KpiCard label="TOTAL UNITS" value={kpis?.total_units ?? "-"} sub={kpis?.total_breakdown} onClick={() => openPanel("all")} />
        <KpiCard label="OCCUPANCY RATE" value={(kpis?.occupancy_rate ?? "-") + "%"} sub={kpis?.occupied + " occupied"} onClick={() => openPanel("all")} />
        <KpiCard label="MONTHLY INCOME" value={kpis?.monthly_income} sub="Assumed current rents" onClick={() => openPanel("all")} />
        <KpiCard label="RENT LEAKAGE / YR" value={kpis?.rent_leakage_yr} sub="Assumed gap vs market" onClick={() => openPanel("all")} />
        <KpiCard label="MARKET POTENTIAL / YR" value={kpis?.market_potential_yr} sub="Full occ. market rents" onClick={() => openPanel("all")} />
      </div>
      <div className="chart-grid-2">
        <div className="chart-card">
          <h3>Portfolio Composition</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={data?.composition || []} dataKey="count" nameKey="label" innerRadius={55} outerRadius={90}>
                {(data?.composition || []).map((e, i) => (
                  <Cell key={i} fill={e.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-card">
          <h3>Occupancy by Category</h3>
          <OccupancyBars rows={data?.occupancy_by_category} />
        </div>
      </div>
      <div className="chart-card">
        <h3>Occupancy Trend - 12 Months</h3>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={trend}>
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="income_fils" stroke="#22c55e" fill="#bbf7d0" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <PropertyPanel open={panelOpen} onClose={() => setPanelOpen(false)} vacantCount={kpis?.vacant} initialTab={panelTab} />
    </>
  );
}
