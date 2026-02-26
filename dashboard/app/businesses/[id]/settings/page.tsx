import { api } from "@/lib/api";
import { SettingsForm } from "./SettingsForm";

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
        <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          Settings
        </h2>
        <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
          Update your property details, operating hours, and Telegram integration.
        </p>
      </div>

      <div className="max-w-2xl">
        <SettingsForm business={business} />
      </div>
    </div>
  );
}
