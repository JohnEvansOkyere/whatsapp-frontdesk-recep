"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";

export function ServiceForm({ businessId }: { businessId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [duration_minutes, setDurationMinutes] = useState(60);
  const [price, setPrice] = useState("");
  const [capacity, setCapacity] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setLoading(true);
    try {
      await api.businesses.services.create(businessId, {
        name: name.trim(),
        description: description.trim() || null,
        duration_minutes,
        price: price ? Number(price) : null,
        capacity: capacity ? Number(capacity) : null,
      });
      setName("");
      setDescription("");
      setDurationMinutes(60);
      setPrice("");
      setCapacity("");
      router.refresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-3 space-y-3">
      <div>
        <input
          type="text"
          placeholder="Name (e.g. Table for 2, Deluxe Room)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
        />
      </div>
      <div>
        <textarea
          placeholder="Description (optional)"
          rows={2}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
        />
      </div>
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-xs text-slate-500">Duration (min)</label>
          <input
            type="number"
            min={15}
            step={15}
            value={duration_minutes}
            onChange={(e) => setDurationMinutes(Number(e.target.value))}
            className="mt-0.5 w-24 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-500">Price (optional)</label>
          <input
            type="number"
            min={0}
            step={0.01}
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            placeholder="—"
            className="mt-0.5 w-24 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-500">Capacity (optional)</label>
          <input
            type="number"
            min={1}
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
            placeholder="—"
            className="mt-0.5 w-24 rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
          />
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
      >
        {loading ? "Adding..." : "Add service"}
      </button>
    </form>
  );
}
