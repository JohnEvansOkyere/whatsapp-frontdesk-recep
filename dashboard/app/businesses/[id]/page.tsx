import { api } from "@/lib/api";
import { CopyIdButton } from "./CopyIdButton";

export default async function BusinessOverviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const business = await api.businesses.get(id);
  const [bookings, services, faqs] = await Promise.all([
    api.bookings.list({ business_id: id }).catch(() => []),
    api.businesses.services.list(id).catch(() => []),
    api.faqs.list(id).catch(() => []),
  ]);

  const upcoming = bookings.filter(
    (b) => new Date(`${b.booking_date}T${b.booking_time}`) >= new Date()
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Overview</h2>
        <p className="mt-1 text-sm text-slate-500">
          Use the business ID when setting up the webhook and in API calls.
        </p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <label className="block text-sm font-medium text-slate-700">Business ID</label>
        <div className="mt-1 flex items-center gap-2">
          <code className="flex-1 truncate rounded bg-slate-100 px-2 py-1.5 text-sm text-slate-800">
            {business.id}
          </code>
          <CopyIdButton id={business.id} />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-sm font-medium text-slate-500">Upcoming bookings</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{upcoming.length}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-sm font-medium text-slate-500">Services</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{services.length}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="text-sm font-medium text-slate-500">FAQs</p>
          <p className="mt-1 text-2xl font-semibold text-slate-900">{faqs.length}</p>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h3 className="font-medium text-slate-900">Details</h3>
        </div>
        <dl className="divide-y divide-slate-200 px-4">
          <div className="py-3">
            <dt className="text-sm text-slate-500">Type</dt>
            <dd className="mt-0.5 text-slate-900">{business.type}</dd>
          </div>
          <div className="py-3">
            <dt className="text-sm text-slate-500">Channel</dt>
            <dd className="mt-0.5 text-slate-900">{business.active_channel}</dd>
          </div>
          {business.timezone && (
            <div className="py-3">
              <dt className="text-sm text-slate-500">Timezone</dt>
              <dd className="mt-0.5 text-slate-900">{business.timezone}</dd>
            </div>
          )}
          {business.location && (
            <div className="py-3">
              <dt className="text-sm text-slate-500">Location</dt>
              <dd className="mt-0.5 text-slate-900">{business.location}</dd>
            </div>
          )}
          {business.phone && (
            <div className="py-3">
              <dt className="text-sm text-slate-500">Phone</dt>
              <dd className="mt-0.5 text-slate-900">{business.phone}</dd>
            </div>
          )}
        </dl>
      </div>
    </div>
  );
}
