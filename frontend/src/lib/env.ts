import type { AppMode } from "../types/contracts";

const rawMode = (
  import.meta.env.APP_MODE ??
  import.meta.env.VITE_APP_MODE ??
  "fixture"
).toString();

export const appMode: AppMode =
  rawMode.toLowerCase() === "live" ? "live" : "fixture";

export const apiBaseUrl = (
  import.meta.env.API_BASE_URL ??
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000"
)
  .toString()
  .replace(/\/+$/, "");
