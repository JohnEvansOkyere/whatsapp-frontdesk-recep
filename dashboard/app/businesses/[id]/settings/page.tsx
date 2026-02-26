import { api } from "@/lib/api";
import { SettingsForm } from "../SettingsForm";

export default async function SettingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const business = await api.businesses.get(id);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Settings</h2>
        <p className="mt-1 text-sm text-slate-500">
          Update business details, working hours, and channel.
        </p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6">
        <SettingsForm business={business} />
      </div>
    </div>
  );
}
