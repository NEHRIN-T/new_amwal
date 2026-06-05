import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/client";

export default function Login() {
  const [username, setUsername] = useState("owner");
  const [password, setPassword] = useState("amwal123");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const data = await login(username, password);
      if (data.user.portal === "client") navigate("/");
      else navigate("/admin/properties");
    } catch {
      setError("Invalid credentials");
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#f4f6f8" }}>
      <form onSubmit={handleSubmit} className="chart-card" style={{ width: 360 }}>
        <h2 style={{ marginTop: 0 }}>AMWAL Login</h2>
        <p style={{ fontSize: "0.85rem", color: "#6b7280" }}>Client: owner / Backend: admin, pmanager, analyst</p>
        <label style={{ display: "block", marginBottom: 8 }}>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} style={{ width: "100%", padding: 8, marginBottom: 12 }} />
        <label style={{ display: "block", marginBottom: 8 }}>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", padding: 8, marginBottom: 12 }} />
        {error && <p style={{ color: "#dc2626" }}>{error}</p>}
        <button type="submit" className="btn-primary" style={{ width: "100%" }}>
          Sign in
        </button>
      </form>
    </div>
  );
}
