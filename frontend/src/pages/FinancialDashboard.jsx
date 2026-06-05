import { Bar, BarChart, Cell, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { clientApi } from "../api/client";
import KpiCard from "../components/KpiCard";
import PageHeader from "../components/PageHeader";
import { usePoll } from "../hooks/usePoll";

function formatFils(f) {
  if (!f) return "0";
  return "AED " + (f / 100 / 1_000_000).toFixed(2) + "M";
}

export default function FinancialDashboard() {
  const { data } = usePoll(() => clientApi.financial(), 30000);
  const kpis = data?.kpis;
  const wf = data?.waterfall || {};
  const trend = (data?.revenue_trend || []).map((t) => ({
    month: t.month,
    current: t.current_fils / 100,
    potential: t.potential_fils / 100,
    bear: t.bear_fils / 100,
  }));

  const waterfallBars = [
    { name: "Market Potential", value: wf.market_potential_fils, fill: "#22c55e" },
    { name: "Vacancy Loss", value: -wf.vacancy_loss_fils, fill: "#f472b6" },
    { name: "Rent Gap", value: -wf.rent_gap_fils, fill: "#f472b6" },
    { name: "Mgmt Fees", value: -wf.management_fees_fils, fill: "#f472b6" },
    { name: "Net Income", value: wf.net_income_fils, fill: "#22c55e" },
  ];

  return (
    <>
      <PageHeader title="FINANCIAL DASHBOARD" />
      <div className="banner">ASSUMPTION MODEL - Phase 1 data import replaces figures with actuals.</div>
      <div className="kpi-grid">
        <KpiCard label="ANNUAL INCOME" value={kpis?.annual_income} sub="Assumed current rents" />
        <KpiCard label="MARKET POTENTIAL" value={kpis?.market_potential} sub="Full occ. market rents" />
        <KpiCard label="GO-TO POTENTIAL" value={kpis?.go_to_potential} sub="Recoverable Annually" />
        <KpiCard label="VACANCY COST / MO" value={kpis?.vacancy_cost_mo} sub="Vacant units" />
        <KpiCard label="AVG GROSS YIELD" value={"~" + kpis?.avg_gross_yield + "%"} sub={"vs Dubai avg " + kpis?.dubai_avg_yield + "%"} />
        <KpiCard label="CONCENTRATION" value={kpis?.concentration_pct + "%"} sub="LX Villas value share" />
      </div>
      <div className="chart-grid-2">
        <div className="chart-card">
          <h3>Revenue Trend - 12 Months</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={trend}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="current" stroke="#22c55e" name="Current" />
              <Line type="monotone" dataKey="potential" stroke="#f59e0b" name="Potential" />
              <Line type="monotone" dataKey="bear" stroke="#dc2626" name="Bear" />
            </LineChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
            <div className="kpi-card" style={{ flex: 1, background: "#ecfdf5" }}>
              CURRENT {data?.revenue_summary?.current_mo}
            </div>
            <div className="kpi-card" style={{ flex: 1, background: "#fff7ed" }}>
              POTENTIAL {data?.revenue_summary?.potential_mo}
            </div>
            <div className="kpi-card" style={{ flex: 1, background: "#fef2f2" }}>
              BEAR {data?.revenue_summary?.bear_mo}
            </div>
          </div>
        </div>
        <div className="chart-card">
          <h3>Revenue Waterfall</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={waterfallBars}>
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v) => formatFils(Math.abs(v))} />
              <Bar dataKey="value">
                {waterfallBars.map((e, i) => (
                  <Cell key={i} fill={e.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <ul style={{ listStyle: "none", padding: 0, fontSize: "0.85rem" }}>
            <li>Market Potential: {formatFils(wf.market_potential_fils)}</li>
            <li style={{ color: "#dc2626" }}>- Vacancy Loss: {formatFils(wf.vacancy_loss_fils)}</li>
            <li style={{ color: "#dc2626" }}>- Rent Gap: {formatFils(wf.rent_gap_fils)}</li>
            <li style={{ color: "#dc2626" }}>- Mgmt Fees: {formatFils(wf.management_fees_fils)}</li>
            <li style={{ color: "#16a34a", fontWeight: 700 }}>= Net: {formatFils(wf.net_income_fils)}</li>
          </ul>
        </div>
      </div>
      <div className="chart-grid-2">
        <div className="chart-card">
          <h3>Gross Yield by Type</h3>
          {(data?.yield_by_type || []).map((y) => (
            <div key={y.label} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #eee" }}>
              <span>{y.label}</span>
              <strong>~{y.yield_pct}%</strong>
            </div>
          ))}
        </div>
        <div className="chart-card">
          <h3>5-Year Revenue Scenarios</h3>
          {(data?.scenarios || []).map((s) => (
            <div key={s.scenario} style={{ marginBottom: 8, fontSize: "0.8rem" }}>
              <strong>{s.scenario}</strong>: {s.description}
            </div>
          ))}
        </div>
      </div>
      <div className="chart-card">
        <h3>Full Financial Breakdown</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Category</th>
              <th>Units</th>
              <th>Occ.</th>
              <th>Occ%</th>
              <th>Leakage</th>
              <th>Yield</th>
            </tr>
          </thead>
          <tbody>
            {(data?.breakdown || []).map((r) => (
              <tr key={r.category} style={r.is_total ? { fontWeight: 700 } : {}}>
                <td>{r.category}</td>
                <td>{r.units}</td>
                <td>{r.occupied}</td>
                <td>{r.occ_pct}%</td>
                <td>{formatFils(r.leakage_fils)}</td>
                <td>{r.yield_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
