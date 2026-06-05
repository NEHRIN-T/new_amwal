import { useState } from "react";
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { clientApi } from "../api/client";
import KpiCard from "../components/KpiCard";
import PageHeader from "../components/PageHeader";
import { usePoll } from "../hooks/usePoll";

export default function OccupancyPage() {
  const [offset, setOffset] = useState(0);
  const { data } = usePoll(() => clientApi.occupancy({ offset }), 30000, [offset]);
  const kpis = data?.kpis;
  const donut = [{ value: kpis?.occupancy_rate || 0 }, { value: 100 - (kpis?.occupancy_rate || 0) }];

  return (
    <>
      <PageHeader title="OCCUPANCY AND VACANCY" />
      <div className="banner">ILLUSTRATIVE SCENARIO - All rents assumption-based.</div>
      <div className="kpi-grid">
        <KpiCard label="CURRENT OCCUPANCY" value={(kpis?.occupancy_rate ?? "-") + "%"} sub="Target: 94% Occupied" />
        <KpiCard label="CRITICAL VACANCY" value={kpis?.critical_vacancy} sub="> 60 days" />
        <KpiCard label="TOTAL MONTHLY REVENUE LOSS" value={kpis?.vacancy_loss_mo} sub="Assumed foregone income" />
        <KpiCard label="MAX DAYS VACANT" value={kpis?.max_days_vacant + " days"} sub={"Unit Ref: " + (kpis?.max_days_unit_ref || "")} />
      </div>
      <div className="chart-grid-2">
        <div className="chart-card">
          <h3>Occupancy Summary</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={donut} innerRadius={60} outerRadius={80} dataKey="value" startAngle={90} endAngle={-270}>
                <Cell fill="#3b82f6" />
                <Cell fill="#e5e7eb" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <p style={{ textAlign: "center", fontWeight: 700, fontSize: "1.5rem", marginTop: -120 }}>
            {data?.donut?.percent}%
          </p>
          <p style={{ textAlign: "center" }}>{data?.donut?.occupied} of {data?.donut?.total} occupied</p>
        </div>
        <div className="chart-card">
          <h3>Vacant Units</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Ref</th>
                <th>Type</th>
                <th>Rent/Mo</th>
                <th>Days Vacant</th>
                <th>Est. Loss</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {(data?.vacant_units || []).map((u) => (
                <tr key={u.unit_ref}>
                  <td>{u.unit_ref}</td>
                  <td>{u.type}</td>
                  <td>{u.rent_mo}</td>
                  <td style={{ color: u.days_vacant > 60 ? "#dc2626" : "inherit" }}>{u.days_vacant}d</td>
                  <td>{u.est_loss}</td>
                  <td>
                    <span className={"badge badge-" + (u.status === "critical" ? "critical" : "monitor")}>{u.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ marginTop: 8, fontWeight: 600 }}>Total Est. Loss: {data?.vacant_total_loss}</p>
        </div>
      </div>
      <div className="chart-card">
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <h3>Occupancy Trend - 12 Months</h3>
          <div>
            <button type="button" className="btn-ghost" onClick={() => setOffset(Math.max(0, offset - 12))}>
              Prev
            </button>
            <button type="button" className="btn-ghost" onClick={() => setOffset(offset + 12)}>
              Next
            </button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data?.occupancy_trend || []}>
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="occupied" stackId="a" fill="#3b82f6" />
            <Bar dataKey="vacant" stackId="a" fill="#fbcfe8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
