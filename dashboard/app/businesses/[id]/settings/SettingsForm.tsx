"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Business } from "@/lib/api";
import { Save } from "lucide-react";

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAY_LABELS: Record<string, string> = {
  mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday",
  fri: "Friday", sat: "Saturday", sun: "Sunday",
};

export function SettingsForm({ business }: { business: Business }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({
    name: business.name,
    working_hours: business.working_hours ?? Object.fromEntries(DAYS.map((d) => [d, ["06:00", "23:00"]])),
    timezone: business.timezone ?? "Africa/Accra",
    location: business.location ?? "",
    phone: business.phone ?? "",
    telegram_bot_token: business.telegram_bot_token ?? "",
    telegram_group_id: business.telegram_group_id ?? "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaved(false);
    setLoading(true);
    try {
      await api.businesses.update(business.id, {
        name: form.name.trim(),
        working_hours: form.working_hours,
        timezone: form.timezone,
        location: form.location.trim() || null,
        phone: form.phone.trim() || null,
        telegram_bot_token: form.telegram_bot_token.trim() || null,
        telegram_group_id: form.telegram_group_id.trim() || null,
      });
      setSaved(true);
      router.refresh();
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Update failed");
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
    <form onSubmit={handleSubmit} className="space-y-8">
      {error && (
        <div
          className="rounded-lg border p-4 text-sm"
          style={{ background: "var(--error-bg)", borderColor: "var(--error)", color: "var(--error)" }}
        >
          {error}
        </div>
      )}
      {saved && (
        <div
          className="rounded-lg border p-4 text-sm"
          style={{ background: "var(--success-bg)", borderColor: "var(--success)", color: "var(--success)" }}
        >
          Settings saved successfully.
        </div>
      )}

      {/* General */}
      <Section title="General">
        <div>
          <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
            Property Name
          </label>
          <input
            type="text"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="w-full"
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
              Location
            </label>
            <input
              type="text"
              value={form.location}
              onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
              Phone
            </label>
            <input
              type="text"
              value={form.phone}
              onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
              className="w-full"
            />
          </div>
        </div>
        <div>
          <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
            Timezone
          </label>
          <input
            type="text"
            value={form.timezone}
            onChange={(e) => setForm((f) => ({ ...f, timezone: e.target.value }))}
            className="w-full"
          />
        </div>
      </Section>

      {/* Operating Hours */}
      <Section title="Operating Hours">
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
          Front desk / reception hours for each day.
        </p>
        <div className="space-y-2">
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
      </Section>

      {/* Telegram */}
      <Section title="Telegram Integration">
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
            className="w-full text-sm"
          />
          <p className="mt-1 text-[11px]" style={{ color: "var(--text-muted)" }}>
            Each property uses its own Telegram bot.
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
            className="w-full text-sm"
          />
        </div>
      </Section>

      <button
        type="submit"
        disabled={loading}
        className="flex items-center gap-2 rounded-lg px-6 py-2.5 text-sm font-semibold disabled:opacity-50"
        style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
      >
        <Save size={16} />
        {loading ? "Saving..." : "Save Changes"}
      </button>
    </form>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      className="rounded-xl border p-6 space-y-4"
      style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
        {title}
      </h3>
      {children}
    </div>
  );
}
