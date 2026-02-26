"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Plus, ChevronDown, ChevronUp } from "lucide-react";

const AMENITY_OPTIONS = [
  "WiFi", "TV", "Air Conditioning", "Mini Bar", "Pool", "Gym",
  "Parking", "Room Service", "Balcony", "Sea View", "City View",
  "Breakfast", "Spa Access", "Airport Shuttle", "Laundry", "Safe",
];

export function AddRoomTypeForm({ businessId }: { businessId: string }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    base_price_per_night: "",
    bed_type: "King",
    max_occupancy: 2,
    room_count: 1,
    image_url: "",
    amenities: [] as string[],
  });

  const toggleAmenity = (a: string) => {
    setForm((f) => ({
      ...f,
      amenities: f.amenities.includes(a)
        ? f.amenities.filter((x) => x !== a)
        : [...f.amenities, a],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    setLoading(true);
    try {
      await api.businesses.services.create(businessId, {
        name: form.name.trim(),
        description: form.description.trim() || null,
        base_price_per_night: form.base_price_per_night ? Number(form.base_price_per_night) : null,
        bed_type: form.bed_type || null,
        max_occupancy: form.max_occupancy,
        room_count: form.room_count,
        image_url: form.image_url.trim() || null,
        amenities: form.amenities.length > 0 ? form.amenities : null,
        duration_minutes: 60,
      });
      setForm({
        name: "",
        description: "",
        base_price_per_night: "",
        bed_type: "King",
        max_occupancy: 2,
        room_count: 1,
        image_url: "",
        amenities: [],
      });
      setOpen(false);
      router.refresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="rounded-xl border"
      style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between p-5 text-left"
      >
        <div className="flex items-center gap-3">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-lg"
            style={{ background: "var(--accent-muted)", color: "var(--accent)" }}
          >
            <Plus size={18} />
          </div>
          <div>
            <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
              Add Room Type
            </p>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              Define a new room category for your property
            </p>
          </div>
        </div>
        {open ? (
          <ChevronUp size={18} style={{ color: "var(--text-muted)" }} />
        ) : (
          <ChevronDown size={18} style={{ color: "var(--text-muted)" }} />
        )}
      </button>

      {open && (
        <form onSubmit={handleSubmit} className="border-t px-5 pb-5 pt-4 space-y-4" style={{ borderColor: "var(--border)" }}>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                Room Type Name
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Deluxe Suite, Standard Room"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="w-full"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                Description
              </label>
              <textarea
                rows={2}
                placeholder="Spacious room with ocean view, modern furnishings, and a private balcony..."
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                Price per Night (GHS)
              </label>
              <input
                type="number"
                min={0}
                step={0.01}
                placeholder="e.g. 850"
                value={form.base_price_per_night}
                onChange={(e) => setForm((f) => ({ ...f, base_price_per_night: e.target.value }))}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                Bed Type
              </label>
              <select
                value={form.bed_type}
                onChange={(e) => setForm((f) => ({ ...f, bed_type: e.target.value }))}
                className="w-full"
              >
                <option value="King">King</option>
                <option value="Queen">Queen</option>
                <option value="Twin">Twin</option>
                <option value="Double">Double</option>
                <option value="Single">Single</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                Max Guests
              </label>
              <input
                type="number"
                min={1}
                value={form.max_occupancy}
                onChange={(e) => setForm((f) => ({ ...f, max_occupancy: Number(e.target.value) }))}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                Number of Rooms
              </label>
              <input
                type="number"
                min={1}
                value={form.room_count}
                onChange={(e) => setForm((f) => ({ ...f, room_count: Number(e.target.value) }))}
                className="w-full"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
                Image URL
              </label>
              <input
                type="url"
                placeholder="https://images.unsplash.com/..."
                value={form.image_url}
                onChange={(e) => setForm((f) => ({ ...f, image_url: e.target.value }))}
                className="w-full"
              />
              <p className="mt-1 text-[11px]" style={{ color: "var(--text-muted)" }}>
                Paste a URL to a photo of this room type. Use Unsplash or your hotel's own photos.
              </p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
              Amenities
            </label>
            <div className="flex flex-wrap gap-1.5">
              {AMENITY_OPTIONS.map((a) => (
                <button
                  key={a}
                  type="button"
                  onClick={() => toggleAmenity(a)}
                  className="rounded-md border px-2.5 py-1 text-[11px] font-medium transition-colors"
                  style={{
                    background: form.amenities.includes(a) ? "var(--accent-muted)" : "var(--bg-input)",
                    borderColor: form.amenities.includes(a) ? "var(--accent)" : "var(--border)",
                    color: form.amenities.includes(a) ? "var(--accent)" : "var(--text-secondary)",
                  }}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg px-5 py-2.5 text-sm font-semibold disabled:opacity-50"
              style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
            >
              {loading ? "Adding..." : "Add Room Type"}
            </button>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-lg border px-5 py-2.5 text-sm font-medium"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
