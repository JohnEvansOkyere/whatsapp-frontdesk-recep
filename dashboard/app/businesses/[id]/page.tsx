import { api } from "@/lib/api";
import { Calendar, Bed, HelpCircle, MapPin, Phone, Clock, Copy } from "lucide-react";
import { CopyIdButton } from "./CopyIdButton";

export default async function BusinessOverviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const business = await api.businesses.get(id);

  let services: Awaited<ReturnType<typeof api.businesses.services.list>> = [];
  let bookings: Awaited<ReturnType<typeof api.businesses.bookings.list>> = [];
  let faqs: Awaited<ReturnType<typeof api.faqs.list>> = [];
  try {
    [services, bookings, faqs] = await Promise.all([
      api.businesses.services.list(id),
      api.businesses.bookings.list(id).catch(() => []),
      api.faqs.list(id).catch(() => []),
    ]);
  } catch {}

  const confirmedBookings = bookings.filter((b) => b.status === "confirmed");
  const pendingBookings = bookings.filter((b) => b.status === "pending");
  const recentBookings = bookings.slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Bookings" value={bookings.length} icon={<Calendar size={18} />} accent="var(--accent)" />
        <StatCard label="Confirmed" value={confirmedBookings.length} icon={<Calendar size={18} />} accent="var(--success)" />
        <StatCard label="Room Types" value={services.length} icon={<Bed size={18} />} accent="var(--info)" />
        <StatCard label="FAQs" value={faqs.length} icon={<HelpCircle size={18} />} accent="var(--warning)" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Property Details */}
        <div
          className="rounded-xl border p-6"
          style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
        >
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
            Property Details
          </h3>
          <div className="space-y-3">
            <DetailRow icon={<Copy size={14} />} label="Business ID">
              <div className="flex items-center gap-2">
                <code
                  className="rounded px-2 py-0.5 text-xs"
                  style={{ background: "var(--bg-input)", color: "var(--text-secondary)" }}
                >
                  {business.id}
                </code>
                <CopyIdButton id={business.id} />
              </div>
            </DetailRow>
            <DetailRow icon={<Bed size={14} />} label="Type">
              <span className="text-sm capitalize" style={{ color: "var(--text-primary)" }}>
                {business.type}
              </span>
            </DetailRow>
            {business.location && (
              <DetailRow icon={<MapPin size={14} />} label="Location">
                <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                  {business.location}
                </span>
              </DetailRow>
            )}
            {business.phone && (
              <DetailRow icon={<Phone size={14} />} label="Phone">
                <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                  {business.phone}
                </span>
              </DetailRow>
            )}
            {business.timezone && (
              <DetailRow icon={<Clock size={14} />} label="Timezone">
                <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                  {business.timezone}
                </span>
              </DetailRow>
            )}
          </div>
        </div>

        {/* Recent Bookings */}
        <div
          className="rounded-xl border p-6"
          style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
        >
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
            Recent Bookings
          </h3>
          {recentBookings.length === 0 ? (
            <p className="text-sm py-8 text-center" style={{ color: "var(--text-muted)" }}>
              No bookings yet. They will appear here once guests start reserving.
            </p>
          ) : (
            <div className="space-y-3">
              {recentBookings.map((b) => (
                <div
                  key={b.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                  style={{ borderColor: "var(--border)", background: "var(--bg-input)" }}
                >
                  <div>
                    <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                      {b.guest_name || "Guest"}
                    </p>
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                      {b.service_name} &middot; {b.booking_reference}
                    </p>
                  </div>
                  <StatusBadge status={b.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Room Types Preview */}
      {services.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
            Room Types
          </h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {services.slice(0, 6).map((s) => (
              <div
                key={s.id}
                className="rounded-xl border overflow-hidden"
                style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
              >
                <div
                  className="h-32 flex items-center justify-center"
                  style={{
                    background: s.image_url
                      ? `url(${s.image_url}) center/cover`
                      : "linear-gradient(135deg, var(--bg-card-hover) 0%, var(--bg-secondary) 100%)",
                  }}
                >
                  {!s.image_url && <Bed size={32} style={{ color: "var(--text-muted)" }} />}
                </div>
                <div className="p-4">
                  <p className="font-semibold text-sm" style={{ color: "var(--text-primary)" }}>
                    {s.name}
                  </p>
                  {s.base_price_per_night && (
                    <p className="text-sm mt-1" style={{ color: "var(--accent)" }}>
                      GHS {Number(s.base_price_per_night).toLocaleString()}/night
                    </p>
                  )}
                  <div className="mt-2 flex flex-wrap gap-1">
                    {s.bed_type && (
                      <Tag>{s.bed_type}</Tag>
                    )}
                    {s.max_occupancy && (
                      <Tag>{s.max_occupancy} guests</Tag>
                    )}
                    {s.room_count && (
                      <Tag>{s.room_count} rooms</Tag>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
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
  value: number;
  icon: React.ReactNode;
  accent: string;
}) {
  return (
    <div
      className="rounded-xl border p-5"
      style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-secondary)" }}>
          {label}
        </p>
        <div
          className="flex h-8 w-8 items-center justify-center rounded-lg"
          style={{ background: `${accent}15`, color: accent }}
        >
          {icon}
        </div>
      </div>
      <p className="mt-2 text-2xl font-bold" style={{ color: "var(--text-primary)" }}>
        {value}
      </p>
    </div>
  );
}

function DetailRow({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5" style={{ color: "var(--text-muted)" }}>{icon}</div>
      <div>
        <p className="text-xs font-medium" style={{ color: "var(--text-muted)" }}>{label}</p>
        {children}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, { bg: string; color: string }> = {
    confirmed: { bg: "var(--success-bg)", color: "var(--success)" },
    pending: { bg: "var(--warning-bg)", color: "var(--warning)" },
    cancelled: { bg: "var(--error-bg)", color: "var(--error)" },
    completed: { bg: "var(--info-bg)", color: "var(--info)" },
    no_show: { bg: "var(--error-bg)", color: "var(--error)" },
  };
  const s = styles[status] ?? styles.pending;
  return (
    <span
      className="rounded-full px-2.5 py-0.5 text-[11px] font-medium capitalize"
      style={{ background: s.bg, color: s.color }}
    >
      {status.replace("_", " ")}
    </span>
  );
}

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="rounded-md px-2 py-0.5 text-[11px]"
      style={{ background: "var(--bg-input)", color: "var(--text-secondary)" }}
    >
      {children}
    </span>
  );
}
