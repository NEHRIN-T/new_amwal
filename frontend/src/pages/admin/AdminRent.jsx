import { useState } from "react";
import { backendApi } from "../../api/client";
import { usePoll } from "../../hooks/usePoll";

export default function AdminRent() {
  const { data, refresh } = usePoll(() => backendApi.rentData(), 30000);
  const rows = data?.results || data || [];
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({});

  async function save() {
    await backendApi.updateRent(editId, {
      current_annual_fils: Math.round(form.current_annual * 100),
      market_annual_fils: Math.round(form.market_annual * 100),
      is_assumed: false,
    });
    setEditId(null);
    refresh();
  }

  return (
    <div>
      <h1>Rent and Market Data</h1>
      <table className="data-table">
        <thead>
          <tr>
            <th>Unit</th>
            <th>Current Annual (AED)</th>
            <th>Market Annual (AED)</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.unit_ref}</td>
              <td>{(r.current_annual_fils / 100).toLocaleString()}</td>
              <td>{(r.market_annual_fils / 100).toLocaleString()}</td>
              <td>{r.gap_status}</td>
              <td>
                <button
                  type="button"
                  className="btn-ghost"
                  onClick={() => {
                    setEditId(r.id);
                    setForm({
                      current_annual: r.current_annual_fils / 100,
                      market_annual: r.market_annual_fils / 100,
                    });
                  }}
                >
                  Edit
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {editId && (
        <div className="chart-card" style={{ marginTop: 16 }}>
          <h3>Edit Rent</h3>
          <input
            type="number"
            value={form.current_annual}
            onChange={(e) => setForm({ ...form, current_annual: e.target.value })}
            placeholder="Current annual AED"
            style={{ display: "block", marginBottom: 8, width: "100%" }}
          />
          <input
            type="number"
            value={form.market_annual}
            onChange={(e) => setForm({ ...form, market_annual: e.target.value })}
            placeholder="Market annual AED"
            style={{ display: "block", marginBottom: 8, width: "100%" }}
          />
          <button type="button" className="btn-primary" onClick={save}>
            Save
          </button>
        </div>
      )}
    </div>
  );
}
