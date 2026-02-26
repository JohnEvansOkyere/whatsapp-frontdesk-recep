"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, type Service } from "@/lib/api";
import { Bed, Users, Wifi, Tv, Car, Coffee, Waves, Wind, Edit, Trash2, X, Check } from "lucide-react";

const amenityIcons: Record<string, React.ReactNode> = {
  wifi: <Wifi size={12} />,
  tv: <Tv size={12} />,
  parking: <Car size={12} />,
  "mini bar": <Coffee size={12} />,
  pool: <Waves size={12} />,
  "air conditioning": <Wind size={12} />,
};

export function RoomTypeCard({ service: s, businessId }: { service: Service; businessId: string }) {
  const router = useRouter();
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [form, setForm] = useState({
    name: s.name,
    description: s.description ?? "",
    base_price_per_night: s.base_price_per_night ? Number(s.base_price_per_night) : 0,
    max_occupancy: s.max_occupancy ?? 2,
    bed_type: s.bed_type ?? "",
    room_count: s.room_count ?? 1,
    image_url: s.image_url ?? "",
    amenities: s.amenities ?? [],
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.businesses.services.update(businessId, s.id, {
        name: form.name,
        description: form.description || null,
        base_price_per_night: form.base_price_per_night || null,
        max_occupancy: form.max_occupancy,
        bed_type: form.bed_type || null,
        room_count: form.room_count,
        image_url: form.image_url || null,
        amenities: form.amenities.length > 0 ? form.amenities : null,
      });
      setEditing(false);
      router.refresh();
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.businesses.services.delete(businessId, s.id);
      router.refresh();
    } finally {
      setDeleting(false);
    }
  };

  const toggleAmenity = (amenity: string) => {
    setForm((f) => ({
      ...f,
      amenities: f.amenities.includes(amenity)
        ? f.amenities.filter((a) => a !== amenity)
        : [...f.amenities, amenity],
    }));
  };

  if (editing) {
    return (
      <div
        className="rounded-xl border p-5 space-y-3"
        style={{ background: "var(--bg-card)", borderColor: "var(--accent)" }}
      >
        <input
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          className="w-full text-sm"
          placeholder="Room type name"
        />
        <textarea
          value={form.description}
          onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          rows={2}
          className="w-full text-sm"
          placeholder="Description"
        />
        <input
          value={form.image_url}
          onChange={(e) => setForm((f) => ({ ...f, image_url: e.target.value }))}
          className="w-full text-sm"
          placeholder="Image URL (https://...)"
        />
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-[11px]" style={{ color: "var(--text-muted)" }}>Price/night (GHS)</label>
            <input
              type="number"
              min={0}
              value={form.base_price_per_night}
              onChange={(e) => setForm((f) => ({ ...f, base_price_per_night: Number(e.target.value) }))}
              className="w-full text-sm"
            />
          </div>
          <div>
            <label className="text-[11px]" style={{ color: "var(--text-muted)" }}>Bed Type</label>
            <select
              value={form.bed_type}
              onChange={(e) => setForm((f) => ({ ...f, bed_type: e.target.value }))}
              className="w-full text-sm"
            >
              <option value="">Select...</option>
              <option value="King">King</option>
              <option value="Queen">Queen</option>
              <option value="Twin">Twin</option>
              <option value="Double">Double</option>
              <option value="Single">Single</option>
            </select>
          </div>
          <div>
            <label className="text-[11px]" style={{ color: "var(--text-muted)" }}>Max Guests</label>
            <input
              type="number"
              min={1}
              value={form.max_occupancy}
              onChange={(e) => setForm((f) => ({ ...f, max_occupancy: Number(e.target.value) }))}
              className="w-full text-sm"
            />
          </div>
          <div>
            <label className="text-[11px]" style={{ color: "var(--text-muted)" }}>Room Count</label>
            <input
              type="number"
              min={1}
              value={form.room_count}
              onChange={(e) => setForm((f) => ({ ...f, room_count: Number(e.target.value) }))}
              className="w-full text-sm"
            />
          </div>
        </div>
        <div>
          <label className="text-[11px] block mb-1" style={{ color: "var(--text-muted)" }}>Amenities</label>
          <div className="flex flex-wrap gap-1.5">
            {["WiFi", "TV", "Air Conditioning", "Mini Bar", "Pool", "Gym", "Parking", "Room Service", "Balcony", "Sea View", "City View", "Breakfast"].map((a) => (
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
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-1.5 rounded-lg px-4 py-2 text-xs font-semibold disabled:opacity-50"
            style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
          >
            <Check size={14} />
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            onClick={() => setEditing(false)}
            className="flex items-center gap-1.5 rounded-lg border px-4 py-2 text-xs font-medium"
            style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
          >
            <X size={14} />
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="group rounded-xl border overflow-hidden transition-all hover:border-[var(--border-light)]"
      style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <div
        className="relative h-40 flex items-center justify-center"
        style={{
          background: s.image_url
            ? `url(${s.image_url}) center/cover no-repeat`
            : "linear-gradient(135deg, var(--bg-card-hover) 0%, var(--bg-secondary) 100%)",
        }}
      >
        {!s.image_url && <Bed size={36} style={{ color: "var(--text-muted)" }} />}
        {!s.is_active && (
          <div
            className="absolute top-3 left-3 rounded-md px-2 py-0.5 text-[11px] font-medium"
            style={{ background: "var(--error-bg)", color: "var(--error)" }}
          >
            Inactive
          </div>
        )}
        <div className="absolute top-3 right-3 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => setEditing(true)}
            className="rounded-lg p-2 backdrop-blur-sm"
            style={{ background: "rgba(0,0,0,0.6)", color: "var(--text-primary)" }}
          >
            <Edit size={14} />
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="rounded-lg p-2 backdrop-blur-sm"
            style={{ background: "rgba(0,0,0,0.6)", color: "var(--error)" }}
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold" style={{ color: "var(--text-primary)" }}>
              {s.name}
            </h3>
            {s.description && (
              <p className="mt-0.5 text-xs line-clamp-2" style={{ color: "var(--text-secondary)" }}>
                {s.description}
              </p>
            )}
          </div>
          {s.base_price_per_night && (
            <div className="text-right">
              <p className="text-lg font-bold" style={{ color: "var(--accent)" }}>
                GHS {Number(s.base_price_per_night).toLocaleString()}
              </p>
              <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
                per night
              </p>
            </div>
          )}
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {s.bed_type && (
            <DetailTag icon={<Bed size={12} />}>{s.bed_type}</DetailTag>
          )}
          {s.max_occupancy && (
            <DetailTag icon={<Users size={12} />}>Up to {s.max_occupancy}</DetailTag>
          )}
          {s.room_count && (
            <DetailTag>{s.room_count} room{s.room_count > 1 ? "s" : ""}</DetailTag>
          )}
        </div>

        {s.amenities && s.amenities.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {s.amenities.slice(0, 6).map((a) => (
              <span
                key={a}
                className="rounded-md px-2 py-0.5 text-[11px]"
                style={{ background: "var(--bg-input)", color: "var(--text-secondary)" }}
              >
                {amenityIcons[a.toLowerCase()] ?? null} {a}
              </span>
            ))}
            {s.amenities.length > 6 && (
              <span
                className="rounded-md px-2 py-0.5 text-[11px]"
                style={{ background: "var(--bg-input)", color: "var(--text-muted)" }}
              >
                +{s.amenities.length - 6} more
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function DetailTag({ icon, children }: { icon?: React.ReactNode; children: React.ReactNode }) {
  return (
    <span
      className="flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-medium"
      style={{ background: "var(--bg-input)", color: "var(--text-secondary)" }}
    >
      {icon}
      {children}
    </span>
  );
}
