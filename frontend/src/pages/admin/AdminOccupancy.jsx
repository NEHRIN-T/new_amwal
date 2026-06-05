import { backendApi } from "../../api/client";
import { usePoll } from "../../hooks/usePoll";

export default function AdminOccupancy() {
  const { data } = usePoll(() => backendApi.occupancyDashboard(), 30000);

  return (
    <div>
      <h1>Occupancy Management Dashboard</h1>
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Total Vacant</div>
          <div className="kpi-value">{data?.total_vacant}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Critical</div>
          <div className="kpi-value">{data?.critical}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Monitor</div>
          <div className="kpi-value">{data?.monitor}</div>
        </div>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Unit</th>
            <th>Days Vacant</th>
            <th>Status</th>
            <th>Est Loss</th>
          </tr>
        </thead>
        <tbody>
          {(data?.units || []).map((u) => (
            <tr key={u.unit_ref}>
              <td>{u.unit_ref}</td>
              <td>{u.days_vacant}</td>
              <td>{u.status}</td>
              <td>{u.est_loss_mo}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
