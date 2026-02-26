import Link from "next/link";
import { api } from "@/lib/api";
import { Building2, Calendar, Plus } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  let businesses: Awaited<ReturnType<typeof api.businesses.list>> = [];
  try {
    businesses = await api.businesses.list();
  } catch {
    // API unreachable
  }

  const totalProperties = businesses.length;
  const activeProperties = businesses.filter((b) => b.is_active).length;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold" style={{ color: "var(--text-primary)" }}>
          Welcome back
        </h1>
        <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
          Here is an overview of your properties and activity.
        </p>
      </div>

      <div className="mb-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Total Properties"
          value={totalProperties}
          icon={<Building2 size={20} />}
          accent="var(--accent)"
        />
        <StatCard
          label="Active Properties"
          value={activeProperties}
          icon={<Building2 size={20} />}
          accent="var(--success)"
        />
        <StatCard
          label="Channels"
          value="Telegram"
          icon={<Calendar size={20} />}
          accent="var(--info)"
        />
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          Your Properties
        </h2>
        <Link
          href="/businesses/new"
          className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors"
          style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
        >
          <Plus size={16} />
          Add Property
        </Link>
      </div>

      {businesses.length === 0 ? (
        <div
          className="rounded-xl border-2 border-dashed p-12 text-center"
          style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}
        >
          <Building2 size={48} className="mx-auto mb-4 opacity-40" />
          <p className="text-lg font-medium mb-1">No properties yet</p>
          <p className="text-sm mb-6">Add your first hotel or restaurant to get started.</p>
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
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {businesses.map((b) => (
            <Link
              key={b.id}
              href={`/businesses/${b.id}`}
              className="group rounded-xl border p-5 transition-all hover:border-[var(--accent)]"
              style={{
                background: "var(--bg-card)",
                borderColor: "var(--border)",
              }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold" style={{ color: "var(--text-primary)" }}>
                    {b.name}
                  </p>
                  <p className="mt-1 text-xs uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
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
              <div className="mt-4 flex items-center gap-4 text-xs" style={{ color: "var(--text-secondary)" }}>
                <span className="capitalize">{b.active_channel}</span>
                {b.timezone && <span>{b.timezone}</span>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  accent: string;
}) {
  return (
    <div
      className="rounded-xl border p-5"
      style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
          {label}
        </p>
        <div
          className="flex h-9 w-9 items-center justify-center rounded-lg"
          style={{ background: `${accent}15`, color: accent }}
        >
          {icon}
        </div>
      </div>
      <p className="mt-3 text-2xl font-bold" style={{ color: "var(--text-primary)" }}>
        {value}
      </p>
    </div>
  );
}
