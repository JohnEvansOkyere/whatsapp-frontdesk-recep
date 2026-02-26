import { api } from "@/lib/api";
import { BookingsTable } from "./BookingsTable";

export default async function BookingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let bookings: Awaited<ReturnType<typeof api.businesses.bookings.list>> = [];
  try {
    bookings = await api.businesses.bookings.list(id);
  } catch {}

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          Bookings
        </h2>
        <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
          All reservations for your property. Bookings made via Telegram appear here automatically.
        </p>
      </div>

      <BookingsTable bookings={bookings} />
    </div>
  );
}
