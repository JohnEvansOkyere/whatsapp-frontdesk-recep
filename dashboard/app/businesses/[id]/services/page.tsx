import { api } from "@/lib/api";
import { ServiceForm } from "../ServiceForm";

export default async function ServicesPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let services: Awaited<ReturnType<typeof api.businesses.services.list>> = [];
  try {
    services = await api.businesses.services.list(id);
  } catch {
    // show empty
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Services</h2>
        <p className="mt-1 text-sm text-slate-500">
          Table types, room types, or bookable options. The bot uses these for reservations.
        </p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-medium text-slate-700">Add service</h3>
        <ServiceForm businessId={id} />
      </div>

      {services.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50/50 py-12 text-center text-slate-600">
          No services yet. Add one so customers can book.
        </div>
      ) : (
        <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
          {services.map((s) => (
            <li key={s.id} className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">{s.name}</p>
                  {s.description && (
                    <p className="mt-0.5 text-sm text-slate-600">{s.description}</p>
                  )}
                  <p className="mt-1 text-xs text-slate-500">
                    {s.duration_minutes} min
                    {s.price != null && ` · ${s.price}`}
                    {s.capacity != null && ` · capacity ${s.capacity}`}
                  </p>
                </div>
                {!s.is_active && (
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                    Inactive
                  </span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
