import { api } from "@/lib/api";
import { RoomTypeCard } from "./RoomTypeCard";
import { AddRoomTypeForm } from "./AddRoomTypeForm";

export default async function RoomsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let services: Awaited<ReturnType<typeof api.businesses.services.list>> = [];
  try {
    services = await api.businesses.services.list(id);
  } catch {}

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
            Room Types
          </h2>
          <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
            Define your room categories. Guests will choose from these when making a reservation.
          </p>
        </div>
      </div>

      <AddRoomTypeForm businessId={id} />

      {services.length === 0 ? (
        <div
          className="rounded-xl border-2 border-dashed p-12 text-center"
          style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}
        >
          <p className="text-base font-medium mb-1">No room types configured</p>
          <p className="text-sm">Add your first room type above so guests can start booking.</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {services.map((s) => (
            <RoomTypeCard key={s.id} service={s} businessId={id} />
          ))}
        </div>
      )}
    </div>
  );
}
