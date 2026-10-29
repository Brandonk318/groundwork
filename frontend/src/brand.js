// The product name lives here ONLY (frontend). Backend: backend/app/config.py DEFAULT_APP_NAME.
// Finalists: Groundwork / Commissary Club. Override at build time with VITE_APP_NAME.
export const APP_NAME = import.meta.env.VITE_APP_NAME || "Groundwork";
