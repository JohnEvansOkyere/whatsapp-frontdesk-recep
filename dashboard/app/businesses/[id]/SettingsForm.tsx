"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import type { Business } from "@/lib/api";

const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];

export function SettingsForm({ business }: { business: Business }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: business.name,
    working_hours: business.working_hours ?? Object.fromEntries(DAYS.map((d) => [d, ["09:00", "21:00"]])),
    slot_duration_minutes: business.slot_duration_minutes ?? 30,
    timezone: business.timezone ?? "Africa/Accra",
    location: business.location ?? "",
    phone: business.phone ?? "",
    telegram_group_id: business.telegram_group_id ?? "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.businesses.update(business.id, {
        name: form.name.trim(),
        working_hours: form.working_hours,
        slot_duration_minutes: form.slot_duration_minutes,
        timezone: form.timezone,
        location: form.location.trim() || null,
        phone: form.phone.trim() || null,
        telegram_group_id: form.telegram_group_id.trim() || null,
      });
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Update failed");
    } finally {
      setLoading(false);
    }
  };

  const setDayHours = (day: string, index: 0 | 1, value: string) => {
    setForm((f) => {
      const next = { ...f.working_hours };
      const arr = [...(next[day] ?? ["09:00", "21:00"])];
      arr[index] = value;
      next[day] = arr;
      return { ...f, working_hours: next };
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-slate-700">
          Name
        </label>
        <input
          id="name"
          type="text"
          required
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Working hours</label>
        <p className="mt-0.5 text-xs text-slate-500">Open and close time per day (e.g. 09:00, 21:00)</p>
        <div className="mt-2 space-y-2">
          {DAYS.map((day) => (
            <div key={day} className="flex items-center gap-2">
              <span className="w-10 text-sm capitalize text-slate-600">{day}</span>
              <input
                type="text"
                placeholder="09:00"
                value={form.working_hours[day]?.[0] ?? ""}
                onChange={(e) => setDayHours(day, 0, e.target.value)}
                className="w-20 rounded border border-slate-300 px-2 py-1 text-sm"
              />
              <span className="text-slate-400">to</span>
              <input
                type="text"
                placeholder="21:00"
                value={form.working_hours[day]?.[1] ?? ""}
                onChange={(e) => setDayHours(day, 1, e.target.value)}
                className="w-20 rounded border border-slate-300 px-2 py-1 text-sm"
              />
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="timezone" className="block text-sm font-medium text-slate-700">
            Timezone
          </label>
          <input
            id="timezone"
            type="text"
            value={form.timezone}
            onChange={(e) => setForm((f) => ({ ...f, timezone: e.target.value }))}
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
          />
        </div>
        <div>
          <label htmlFor="slot_duration_minutes" className="block text-sm font-medium text-slate-700">
            Slot duration (minutes)
          </label>
          <input
            id="slot_duration_minutes"
            type="number"
            min={15}
            step={15}
            value={form.slot_duration_minutes}
            onChange={(e) => setForm((f) => ({ ...f, slot_duration_minutes: Number(e.target.value) }))}
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
          />
        </div>
      </div>

      <div>
        <label htmlFor="location" className="block text-sm font-medium text-slate-700">
          Location
        </label>
        <input
          id="location"
          type="text"
          value={form.location}
          onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
        />
      </div>

      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-slate-700">
          Phone
        </label>
        <input
          id="phone"
          type="text"
          value={form.phone}
          onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
        />
      </div>

      <div>
        <label htmlFor="telegram_group_id" className="block text-sm font-medium text-slate-700">
          Telegram group ID
        </label>
        <input
          id="telegram_group_id"
          type="text"
          value={form.telegram_group_id}
          onChange={(e) => setForm((f) => ({ ...f, telegram_group_id: e.target.value }))}
          className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
        />
        <p className="mt-0.5 text-xs text-slate-500">For staff notifications and handoff</p>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
      >
        {loading ? "Saving..." : "Save changes"}
      </button>
    </form>
  );
}
