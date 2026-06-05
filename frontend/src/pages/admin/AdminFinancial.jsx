import { useEffect, useState } from "react";
import { backendApi } from "../../api/client";

export default function AdminFinancial() {
  const [fees, setFees] = useState({ fee_type: "percent", fee_percentage: 5.8 });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    backendApi.fees().then((r) => r.data && setFees(r.data));
  }, []);

  async function saveFees() {
    await backendApi.saveFees(fees);
    setMsg("Fee configuration saved.");
  }

  return (
    <div>
      <h1>Financial Data Entry</h1>
      <div className="chart-card">
        <h3>Management Fee Configuration</h3>
        <select value={fees.fee_type} onChange={(e) => setFees({ ...fees, fee_type: e.target.value })}>
          <option value="percent">Percentage of annual income</option>
          <option value="fixed">Fixed per unit</option>
        </select>
        <input
          type="number"
          value={fees.fee_percentage || 5.8}
          onChange={(e) => setFees({ ...fees, fee_percentage: e.target.value })}
          style={{ display: "block", marginTop: 8, width: "100%" }}
        />
        <button type="button" className="btn-primary" style={{ marginTop: 12 }} onClick={saveFees}>
          Save
        </button>
        {msg && <p>{msg}</p>}
      </div>
    </div>
  );
}
