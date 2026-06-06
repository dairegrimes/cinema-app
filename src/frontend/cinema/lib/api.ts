import type { Listing } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchListings(): Promise<Listing[]> {
  const response = await fetch(`${API_BASE}/listings/`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to fetch listings (${response.status})`);
  }
  return response.json();
}

export function formatListingTime(timestamp: number): string {
  return new Intl.DateTimeFormat("en-IE", {
    timeZone: "Europe/Dublin",
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(timestamp * 1000));
}
