import { api } from "@/lib/api";

function formatDate(d: string) {
  return new Date(d).toLocaleDateString(undefined, {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatTime(t: string) {
  const [h, m] = t.split(":");
  const hh = parseInt(h, 10);
  const am = hh < 12;
  const hour = hh % 12 || 12;
  return `${hour}:${m} ${am ? "AM" : "PM"}`;
}

export default async function BookingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let bookings: Awaited<ReturnType<typeof api.bookings.list>> = [];
  try {
    bookings = await api.bookings.list({ business_id: id });
  } catch {
    // show empty
  }

  const sorted = [...bookings].sort(
    (a, b) =>
      new Date(`${a.booking_date}T${a.booking_time}`).getTime() -
      new Date(`${b.booking_date}T${b.booking_time}`).getTime()
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Bookings</h2>
        <p className="mt-1 text-sm text-slate-500">
          Reservations and orders for this business.
        </p>
      </div>

      {sorted.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50/50 py-12 text-center text-slate-600">
          No bookings yet.
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
          <table className="min-w-full divide-y divide-slate-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Reference
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Time
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Party size
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {sorted.map((b) => (
                <tr key={b.id}>
                  <td className="whitespace-nowrap px-4 py-3 font-mono text-sm text-slate-900">
                    {b.booking_reference}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                    {formatDate(b.booking_date)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                    {formatTime(b.booking_time)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                    {b.party_size ?? "—"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                    {b.status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
