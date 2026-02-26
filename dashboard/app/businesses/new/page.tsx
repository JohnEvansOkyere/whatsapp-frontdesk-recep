"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { ArrowLeft, Building2, Hotel, UtensilsCrossed } from "lucide-react";
import Link from "next/link";

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAY_LABELS: Record<string, string> = {
  mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday",
  fri: "Friday", sat: "Saturday", sun: "Sunday",
};
const defaultHours: Record<string, string[]> = Object.fromEntries(
  DAYS.map((d) => [d, ["06:00", "23:00"]])
);

const businessTypes = [
  { value: "hotel" as const, label: "Hotel", icon: Hotel, desc: "Rooms, suites, and hotel services" },
  { value: "restaurant" as const, label: "Restaurant", icon: UtensilsCrossed, desc: "Table reservations and dining" },
  { value: "hostel" as const, label: "Hostel", icon: Building2, desc: "Budget rooms and dormitories" },
];

export default function NewBusinessPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    type: "hotel" as "restaurant" | "hostel" | "hotel",
    working_hours: defaultHours,
    timezone: "Africa/Accra",
    location: "",
    phone: "",
    telegram_bot_token: "",
    telegram_group_id: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const biz = await api.businesses.create({
        name: form.name.trim(),
        type: form.type,
        working_hours: form.working_hours,
        timezone: form.timezone,
        location: form.location.trim() || null,
        phone: form.phone.trim() || null,
        telegram_bot_token: form.telegram_bot_token.trim() || null,
        telegram_group_id: form.telegram_group_id.trim() || null,
      });
      router.push(`/businesses/${biz.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create property");
    } finally {
      setLoading(false);
    }
  };

  const setDayHours = (day: string, index: 0 | 1, value: string) => {
    setForm((f) => {
      const next = { ...f.working_hours };
      const arr = [...(next[day] ?? ["06:00", "23:00"])];
      arr[index] = value;
      next[day] = arr;
      return { ...f, working_hours: next };
    });
  };

  return (
    <div className="p-8">
      <Link
        href="/businesses"
        className="mb-6 inline-flex items-center gap-2 text-sm transition-colors"
        style={{ color: "var(--text-secondary)" }}
      >
        <ArrowLeft size={16} />
        Back to Properties
      </Link>

      <div className="mx-auto max-w-2xl">
        <h1 className="text-2xl font-semibold mb-1" style={{ color: "var(--text-primary)" }}>
          Add new property
        </h1>
        <p className="text-sm mb-8" style={{ color: "var(--text-secondary)" }}>
          Set up your hotel, restaurant, or hostel. The AI bot will use these details to serve your guests.
        </p>

        <form onSubmit={handleSubmit} className="space-y-8">
          {error && (
            <div
              className="rounded-lg border p-4 text-sm"
              style={{ background: "var(--error-bg)", borderColor: "var(--error)", color: "var(--error)" }}
            >
              {error}
            </div>
          )}

          {/* Property Type */}
          <div>
            <label className="block text-sm font-medium mb-3" style={{ color: "var(--text-primary)" }}>
              Property Type
            </label>
            <div className="grid grid-cols-3 gap-3">
              {businessTypes.map(({ value, label, icon: Icon, desc }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setForm((f) => ({ ...f, type: value }))}
                  className="rounded-xl border p-4 text-left transition-all"
                  style={{
                    background: form.type === value ? "var(--accent-muted)" : "var(--bg-card)",
                    borderColor: form.type === value ? "var(--accent)" : "var(--border)",
                  }}
                >
                  <Icon
                    size={24}
                    style={{ color: form.type === value ? "var(--accent)" : "var(--text-muted)" }}
                  />
                  <p
                    className="mt-2 text-sm font-semibold"
                    style={{ color: form.type === value ? "var(--accent)" : "var(--text-primary)" }}
                  >
                    {label}
                  </p>
                  <p className="mt-0.5 text-[11px]" style={{ color: "var(--text-muted)" }}>
                    {desc}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Property Name */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-primary)" }}>
              Property Name
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Kempinski Hotel Gold Coast City"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              className="block w-full"
            />
          </div>

          {/* Location & Phone */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-primary)" }}>
                Location
              </label>
              <input
                type="text"
                placeholder="e.g. Accra, Ghana"
                value={form.location}
                onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
                className="block w-full"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-primary)" }}>
                Phone
              </label>
              <input
                type="text"
                placeholder="e.g. +233 30 263 1000"
                value={form.phone}
                onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                className="block w-full"
              />
            </div>
          </div>

          {/* Timezone */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-primary)" }}>
              Timezone
            </label>
            <input
              type="text"
              value={form.timezone}
              onChange={(e) => setForm((f) => ({ ...f, timezone: e.target.value }))}
              className="block w-full"
            />
          </div>

          {/* Working Hours */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-primary)" }}>
              Operating Hours
            </label>
            <p className="text-xs mb-3" style={{ color: "var(--text-muted)" }}>
              Front desk / reception hours for each day of the week.
            </p>
            <div
              className="rounded-xl border p-4 space-y-2"
              style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
            >
              {DAYS.map((day) => (
                <div key={day} className="flex items-center gap-3">
                  <span className="w-24 text-sm" style={{ color: "var(--text-secondary)" }}>
                    {DAY_LABELS[day]}
                  </span>
                  <input
                    type="time"
                    value={form.working_hours[day]?.[0] ?? "06:00"}
                    onChange={(e) => setDayHours(day, 0, e.target.value)}
                    className="w-28 text-sm"
                  />
                  <span style={{ color: "var(--text-muted)" }}>to</span>
                  <input
                    type="time"
                    value={form.working_hours[day]?.[1] ?? "23:00"}
                    onChange={(e) => setDayHours(day, 1, e.target.value)}
                    className="w-28 text-sm"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Telegram Config */}
          <div>
            <h3 className="text-sm font-medium mb-3" style={{ color: "var(--text-primary)" }}>
              Telegram Integration
            </h3>
            <div
              className="rounded-xl border p-4 space-y-4"
              style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
            >
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                  Bot Token
                </label>
                <input
                  type="password"
                  autoComplete="off"
                  placeholder="Paste your bot token from @BotFather"
                  value={form.telegram_bot_token}
                  onChange={(e) => setForm((f) => ({ ...f, telegram_bot_token: e.target.value }))}
                  className="block w-full text-sm"
                />
                <p className="mt-1 text-[11px]" style={{ color: "var(--text-muted)" }}>
                  Each property needs its own Telegram bot. Create one via @BotFather.
                </p>
              </div>
              <div>
                <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                  Staff Group Chat ID
                </label>
                <input
                  type="text"
                  placeholder="e.g. -1001234567890"
                  value={form.telegram_group_id}
                  onChange={(e) => setForm((f) => ({ ...f, telegram_group_id: e.target.value }))}
                  className="block w-full text-sm"
                />
                <p className="mt-1 text-[11px]" style={{ color: "var(--text-muted)" }}>
                  For staff notifications and human handoff. Add the bot to your staff group.
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg px-6 py-2.5 text-sm font-semibold transition-colors disabled:opacity-50"
              style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
            >
              {loading ? "Creating..." : "Create Property"}
            </button>
            <button
              type="button"
              onClick={() => router.push("/businesses")}
              className="rounded-lg border px-6 py-2.5 text-sm font-medium transition-colors"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
