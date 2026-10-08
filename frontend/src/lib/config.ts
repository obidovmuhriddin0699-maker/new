// Only NEXT_PUBLIC_* values reach the browser. Never put secrets here.
export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);
