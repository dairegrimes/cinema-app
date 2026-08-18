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

export function getListingDayKey(timestamp: number): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Dublin",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(timestamp * 1000));
}

export function formatListingDayLabel(timestamp: number): string {
  return new Intl.DateTimeFormat("en-IE", {
    timeZone: "Europe/Dublin",
    weekday: "short",
    day: "numeric",
    month: "short",
  }).format(new Date(timestamp * 1000));
}

export function formatListingClockTime(timestamp: number): string {
  return new Intl.DateTimeFormat("en-IE", {
    timeZone: "Europe/Dublin",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(timestamp * 1000));
}

export interface SubscriptionResult {
  status: string;
  message: string;
}

export async function createSubscription(input: {
  email: string;
  movie_name: string;
  venue_name?: string;
}): Promise<SubscriptionResult> {
  const response = await fetch(`${API_BASE}/subscriptions/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    let detail = `Failed to subscribe (${response.status})`;
    try {
      const body = await response.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(detail);
  }
  return response.json();
}
