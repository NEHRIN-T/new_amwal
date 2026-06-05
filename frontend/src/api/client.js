import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("amwal_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function login(username, password) {
  const { data } = await api.post("/api/auth/login/", { username, password });
  localStorage.setItem("amwal_token", data.access);
  localStorage.setItem("amwal_user", JSON.stringify(data.user));
  return data;
}

export function logout() {
  localStorage.removeItem("amwal_token");
  localStorage.removeItem("amwal_user");
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem("amwal_user") || "null");
  } catch {
    return null;
  }
}

export const clientApi = {
  portfolio: () => api.get("/api/client/portfolio/"),
  properties: (params) => api.get("/api/client/properties/", { params }),
  rental: () => api.get("/api/client/rental-intelligence/"),
  occupancy: (params) => api.get("/api/client/occupancy/", { params }),
  financial: () => api.get("/api/client/financial/"),
};

export const backendApi = {
  properties: (params) => api.get("/api/backend/properties/", { params }),
  rentData: (params) => api.get("/api/backend/rent-data/", { params }),
  updateRent: (id, body) => api.patch(`/api/backend/rent-data/${id}/`, body),
  tenants: () => api.get("/api/backend/tenants/"),
  leases: () => api.get("/api/backend/leases/"),
  createLease: (body) => api.post("/api/backend/leases/", body),
  occupancyDashboard: () => api.get("/api/backend/occupancy/dashboard/"),
  fees: () => api.get("/api/backend/financial/fees/"),
  saveFees: (body) => api.post("/api/backend/financial/fees/", body),
  scenarios: () => api.get("/api/backend/financial/scenarios/"),
  saveScenarios: (body) => api.put("/api/backend/financial/scenarios/", body),
};
