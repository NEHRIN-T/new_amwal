import { backendApi } from "../../api/client";
import { usePoll } from "../../hooks/usePoll";

export default function AdminLeases() {
  const { data: leases } = usePoll(() => backendApi.leases(), 30000);
  const rows = leases?.data?.results || leases?.data || [];

  return (
    <div>
      <h1>Tenant and Lease Management</h1>
      <table className="data-table">
        <thead>
          <tr>
            <th>Unit</th>
            <th>Tenant</th>
            <th>Start</th>
            <th>End</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((l) => (
            <tr key={l.id}>
              <td>{l.unit_ref}</td>
              <td>{l.tenant_name}</td>
              <td>{l.start_date}</td>
              <td>{l.end_date}</td>
              <td>{l.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
