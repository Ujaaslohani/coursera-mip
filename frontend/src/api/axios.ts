import axios from "axios";

// BASE URL — DEFAULTS TO LOCAL FASTAPI SERVER
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// SHARED AXIOS INSTANCE
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000, // TODO : REDUCE THIS TIME IN THE PRODUCTION 
});

export default api;
