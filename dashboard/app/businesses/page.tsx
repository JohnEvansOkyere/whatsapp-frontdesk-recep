import Link from "next/link";
import { api } from "@/lib/api";

export default async function BusinessesPage() {
  let businesses: Awaited<ReturnType<typeof api.businesses.list>> = [];
  let error: string | null = null;
  try {
    businesses = await api.businesses.list();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load businesses";
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">Businesses</h1>
        <Link
          href="/businesses/new"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Add business
        </Link>
      </div>

      {error && (
        <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          {error}. Ensure the API is running and NEXT_PUBLIC_API_URL is set.
        </div>
      )}

      <div className="mt-6">
        {businesses.length === 0 && !error && (
          <p className="rounded-lg border border-dashed border-slate-300 bg-slate-50/50 py-12 text-center text-slate-600">
            No businesses yet. Add one to get started.
          </p>
        )}
        <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
          {businesses.map((b) => (
            <li key={b.id}>
              <Link
                href={`/businesses/${b.id}`}
                className="flex items-center justify-between px-4 py-4 hover:bg-slate-50 sm:px-6"
              >
                <div>
                  <p className="font-medium text-slate-900">{b.name}</p>
                  <p className="text-sm text-slate-500">
                    {b.type} · {b.active_channel}
                  </p>
                </div>
                <span className="text-slate-400">View</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
