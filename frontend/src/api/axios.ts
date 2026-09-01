import axios from "axios";

const RAW_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const API_BASE_URL = RAW_API_BASE_URL.replace(/\/+$/, "");

// TIMEOUT — DEFAULT 5 MINUTES (300,000ms) FOR LONG-RUNNING LLM / INGESTION REQUESTS
export const API_TIMEOUT =
  Number(process.env.NEXT_PUBLIC_API_TIMEOUT) || 300_000;

// SHARED AXIOS INSTANCE
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: API_TIMEOUT,
});

// REQUEST INTERCEPTOR — LOG OUTGOING REQUESTS
api.interceptors.request.use(
  (config) => {
    const startTime = Date.now();
    (config as any).metadata = { startTime };

    const method = config.method?.toUpperCase() || "METHOD";
    const fullUrl = `${config.baseURL || ""}${config.url || ""}`;

    console.groupCollapsed(
      `🌐 [API Request] ${method} ${config.url || ""}`
    );
    console.log("Full URL:", fullUrl);
    if (config.params) console.log("Query Params:", config.params);
    if (config.data) console.log("Request Payload:", config.data);
    console.log("Timeout:", `${config.timeout ?? API_TIMEOUT}ms`);
    console.groupEnd();

    return config;
  },
  (error) => {
    console.error("❌ [API Request Config Error]", error);
    return Promise.reject(error);
  }
);

// RESPONSE INTERCEPTOR — LOG SUCCESSFUL RESPONSES AND DETAILED ERRORS
api.interceptors.response.use(
  (response) => {
    const startTime = (response.config as any)?.metadata?.startTime;
    const duration = startTime
      ? `${Date.now() - startTime}ms`
      : "unknown duration";
    const method = response.config.method?.toUpperCase() || "METHOD";

    console.groupCollapsed(
      `✅ [API Response] ${response.status} ${method} ${response.config.url} (${duration})`
    );
    console.log("Status:", response.status, response.statusText);
    console.log("Data:", response.data);
    console.log("Latency:", duration);
    console.groupEnd();

    return response;
  },
  (error) => {
    const config = error.config;
    const startTime = config?.metadata?.startTime;
    const duration = startTime
      ? `${Date.now() - startTime}ms`
      : "unknown duration";
    const method = config?.method?.toUpperCase() || "REQUEST";
    const url = config?.url || "unknown endpoint";

    if (error.code === "ECONNABORTED" || error.message?.includes("timeout")) {
      console.error(
        `⏳ [API Timeout] ${method} ${url} exceeded timeout limit of ${config?.timeout ?? API_TIMEOUT}ms (Elapsed: ${duration})`,
        error
      );
    } else if (error.response) {
      console.group(
        `❌ [API Error Response] ${error.response.status} ${method} ${url} (${duration})`
      );
      console.error("Status:", error.response.status, error.response.statusText);
      console.error("Response Body:", error.response.data);
      console.error("Error Object:", error);
      console.groupEnd();
    } else if (error.request) {
      console.error(
        `❌ [API Network Error] ${method} ${url} - No response received from server (${duration}):`,
        error.message
      );
    } else {
      console.error(`❌ [API Error] ${error.message}`, error);
    }

    return Promise.reject(error);
  }
);

export default api;

