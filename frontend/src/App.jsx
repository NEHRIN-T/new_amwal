import { Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import { getUser } from "./api/client";
import Login from "./pages/Login";
import PortfolioOverview from "./pages/PortfolioOverview";
import RentalIntelligence from "./pages/RentalIntelligence";
import OccupancyPage from "./pages/OccupancyPage";
import FinancialDashboard from "./pages/FinancialDashboard";
import AdminProperties from "./pages/admin/AdminProperties";
import AdminRent from "./pages/admin/AdminRent";
import AdminLeases from "./pages/admin/AdminLeases";
import AdminOccupancy from "./pages/admin/AdminOccupancy";
import AdminFinancial from "./pages/admin/AdminFinancial";

function RequireAuth({ children, portal }) {
  const user = getUser();
  if (!user) return <Navigate to="/login" replace />;
  if (portal === "client" && user.portal !== "client" && user.portal !== "both") {
    return <Navigate to="/admin/properties" replace />;
  }
  if (portal === "backend" && user.portal === "client") {
    return <Navigate to="/" replace />;
  }
  return children;
}

function ClientLayout() {
  return (
    <div className="app-layout">
      <Sidebar mode="client" />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<PortfolioOverview />} />
          <Route path="/rental" element={<RentalIntelligence />} />
          <Route path="/occupancy" element={<OccupancyPage />} />
          <Route path="/financial" element={<FinancialDashboard />} />
        </Routes>
      </main>
    </div>
  );
}

function BackendLayout() {
  return (
    <div className="app-layout">
      <Sidebar mode="backend" />
      <main className="main-content">
        <Routes>
          <Route path="properties" element={<AdminProperties />} />
          <Route path="rent" element={<AdminRent />} />
          <Route path="leases" element={<AdminLeases />} />
          <Route path="occupancy" element={<AdminOccupancy />} />
          <Route path="financial" element={<AdminFinancial />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/admin/*"
        element={
          <RequireAuth portal="backend">
            <BackendLayout />
          </RequireAuth>
        }
      />
      <Route
        path="/*"
        element={
          <RequireAuth portal="client">
            <ClientLayout />
          </RequireAuth>
        }
      />
    </Routes>
  );
}
