import { backendApi } from "../../api/client";
import { usePoll } from "../../hooks/usePoll";

export default function AdminProperties() {
  const { data } = usePoll(() => backendApi.properties(), 30000);
  const rows = data?.results || data || [];

  return (
    <div>
      <h1>Property Management</h1>
      <p>Read-only list (add/edit deferred per FRD).</p>
      <table className="data-table">
        <thead>
          <tr>
            <th>Unit Ref</th>
            <th>Type</th>
            <th>Area</th>
            <th>Status</th>
            <th>Occupancy</th>
            <th>Current Rent</th>
            <th>Market Rent</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.unit_ref}</td>
              <td>{r.type_label}</td>
              <td>{r.area}</td>
              <td>{r.status}</td>
              <td>{r.occupancy_status}</td>
              <td>{r.current_rent}</td>
              <td>{r.market_rent}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
