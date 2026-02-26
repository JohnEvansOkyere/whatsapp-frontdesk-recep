import Link from "next/link";
import { api } from "@/lib/api";
import { Plus, Building2, MapPin, Phone } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function BusinessesPage() {
  let businesses: Awaited<ReturnType<typeof api.businesses.list>> = [];
  try {
    businesses = await api.businesses.list();
  } catch {
    // show empty
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold" style={{ color: "var(--text-primary)" }}>
            Properties
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
            Manage your hotels, restaurants, and hostels.
          </p>
        </div>
        <Link
          href="/businesses/new"
          className="flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors"
          style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
        >
          <Plus size={16} />
          Add Property
        </Link>
      </div>

      {businesses.length === 0 ? (
        <div
          className="rounded-xl border-2 border-dashed p-16 text-center"
          style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}
        >
          <Building2 size={48} className="mx-auto mb-4 opacity-40" />
          <p className="text-lg font-medium mb-1">No properties</p>
          <p className="text-sm mb-6">Create your first property to start accepting bookings.</p>
          <Link
            href="/businesses/new"
            className="inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-medium"
            style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
          >
            <Plus size={16} />
            Add Property
          </Link>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {businesses.map((b) => (
            <Link
              key={b.id}
              href={`/businesses/${b.id}`}
              className="group flex flex-col rounded-xl border transition-all hover:border-[var(--accent)]"
              style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
            >
              <div
                className="flex h-32 items-center justify-center rounded-t-xl"
                style={{
                  background: `linear-gradient(135deg, var(--bg-card-hover) 0%, var(--bg-secondary) 100%)`,
                }}
              >
                <Building2 size={40} style={{ color: "var(--text-muted)" }} />
              </div>
              <div className="flex flex-1 flex-col p-5">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
                      {b.name}
                    </p>
                    <p
                      className="text-xs font-medium uppercase tracking-wider"
                      style={{ color: "var(--accent)" }}
                    >
                      {b.type}
                    </p>
                  </div>
                  <span
                    className="rounded-full px-2.5 py-0.5 text-[11px] font-medium"
                    style={{
                      background: b.is_active ? "var(--success-bg)" : "var(--error-bg)",
                      color: b.is_active ? "var(--success)" : "var(--error)",
                    }}
                  >
                    {b.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="mt-auto flex flex-wrap gap-3 pt-3 text-xs" style={{ color: "var(--text-secondary)" }}>
                  {b.location && (
                    <span className="flex items-center gap-1">
                      <MapPin size={12} />
                      {b.location}
                    </span>
                  )}
                  {b.phone && (
                    <span className="flex items-center gap-1">
                      <Phone size={12} />
                      {b.phone}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
