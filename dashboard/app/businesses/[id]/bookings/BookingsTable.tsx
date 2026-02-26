"use client";

import { useState } from "react";
import type { Booking } from "@/lib/api";
import { Calendar, User, Search } from "lucide-react";

const STATUS_STYLES: Record<string, { bg: string; color: string }> = {
  confirmed: { bg: "var(--success-bg)", color: "var(--success)" },
  pending: { bg: "var(--warning-bg)", color: "var(--warning)" },
  cancelled: { bg: "var(--error-bg)", color: "var(--error)" },
  completed: { bg: "var(--info-bg)", color: "var(--info)" },
  no_show: { bg: "var(--error-bg)", color: "var(--error)" },
};

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function formatTime(t: string | null) {
  if (!t) return "";
  const [h, m] = t.split(":");
  const hh = parseInt(h, 10);
  const am = hh < 12;
  const hour = hh % 12 || 12;
  return `${hour}:${m} ${am ? "AM" : "PM"}`;
}

export function BookingsTable({ bookings }: { bookings: Booking[] }) {
  const [filter, setFilter] = useState<string>("all");
  const [search, setSearch] = useState("");

  const filtered = bookings.filter((b) => {
    if (filter !== "all" && b.status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        b.booking_reference.toLowerCase().includes(q) ||
        (b.guest_name ?? "").toLowerCase().includes(q) ||
        (b.service_name ?? "").toLowerCase().includes(q)
      );
    }
    return true;
  });

  const counts = {
    all: bookings.length,
    confirmed: bookings.filter((b) => b.status === "confirmed").length,
    pending: bookings.filter((b) => b.status === "pending").length,
    cancelled: bookings.filter((b) => b.status === "cancelled").length,
    completed: bookings.filter((b) => b.status === "completed").length,
  };

  return (
    <div>
      {/* Filter tabs */}
      <div className="flex items-center gap-6 mb-4">
        <div className="flex gap-1">
          {(["all", "confirmed", "pending", "cancelled", "completed"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className="rounded-lg px-3 py-1.5 text-xs font-medium capitalize transition-colors"
              style={{
                background: filter === s ? "var(--accent-muted)" : "transparent",
                color: filter === s ? "var(--accent)" : "var(--text-secondary)",
              }}
            >
              {s} ({counts[s]})
            </button>
          ))}
        </div>
        <div className="ml-auto relative">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2"
            style={{ color: "var(--text-muted)" }}
          />
          <input
            type="text"
            placeholder="Search bookings..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-8 pr-3 py-1.5 text-sm w-64"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div
          className="rounded-xl border-2 border-dashed p-12 text-center"
          style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}
        >
          <Calendar size={40} className="mx-auto mb-3 opacity-40" />
          <p className="font-medium">No bookings found</p>
          <p className="text-sm mt-1">
            {filter !== "all"
              ? `No ${filter} bookings. Try a different filter.`
              : "Bookings will appear here when guests make reservations via Telegram."}
          </p>
        </div>
      ) : (
        <div
          className="overflow-hidden rounded-xl border"
          style={{ borderColor: "var(--border)" }}
        >
          <table className="w-full">
            <thead>
              <tr style={{ background: "var(--bg-secondary)" }}>
                <Th>Reference</Th>
                <Th>Guest</Th>
                <Th>Room Type</Th>
                <Th>Dates</Th>
                <Th>Guests</Th>
                <Th>Total</Th>
                <Th>Status</Th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((b) => (
                <tr
                  key={b.id}
                  className="border-t transition-colors"
                  style={{ borderColor: "var(--border)" }}
                >
                  <Td>
                    <code
                      className="rounded px-1.5 py-0.5 text-xs font-mono"
                      style={{ background: "var(--bg-input)", color: "var(--text-primary)" }}
                    >
                      {b.booking_reference}
                    </code>
                  </Td>
                  <Td>
                    <div className="flex items-center gap-2">
                      <div
                        className="flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-bold"
                        style={{ background: "var(--accent-muted)", color: "var(--accent)" }}
                      >
                        {(b.guest_name ?? "G")[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="text-sm" style={{ color: "var(--text-primary)" }}>
                          {b.guest_name ?? "Guest"}
                        </p>
                        {b.guest_phone && (
                          <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                            {b.guest_phone}
                          </p>
                        )}
                      </div>
                    </div>
                  </Td>
                  <Td>
                    <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                      {b.service_name ?? "--"}
                    </span>
                  </Td>
                  <Td>
                    <div>
                      {b.check_in_date ? (
                        <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                          {formatDate(b.check_in_date)}
                          {b.check_out_date && ` - ${formatDate(b.check_out_date)}`}
                        </span>
                      ) : (
                        <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                          {formatDate(b.booking_date)}
                          {b.booking_time && ` at ${formatTime(b.booking_time)}`}
                        </span>
                      )}
                      {b.num_nights && (
                        <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                          {b.num_nights} night{b.num_nights > 1 ? "s" : ""}
                        </p>
                      )}
                    </div>
                  </Td>
                  <Td>
                    <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                      {b.num_guests ?? b.party_size ?? "--"}
                    </span>
                  </Td>
                  <Td>
                    {b.total_price ? (
                      <span className="text-sm font-medium" style={{ color: "var(--accent)" }}>
                        GHS {Number(b.total_price).toLocaleString()}
                      </span>
                    ) : (
                      <span className="text-sm" style={{ color: "var(--text-muted)" }}>--</span>
                    )}
                  </Td>
                  <Td>
                    <StatusBadge status={b.status} />
                  </Td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th
      className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-wider"
      style={{ color: "var(--text-muted)" }}
    >
      {children}
    </th>
  );
}

function Td({ children }: { children: React.ReactNode }) {
  return <td className="px-4 py-3">{children}</td>;
}

function StatusBadge({ status }: { status: string }) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.pending;
  return (
    <span
      className="rounded-full px-2.5 py-0.5 text-[11px] font-medium capitalize"
      style={{ background: s.bg, color: s.color }}
    >
      {status.replace("_", " ")}
    </span>
  );
}
