import { api } from "@/lib/api";
import { FAQForm } from "./FAQForm";
import { FAQList } from "./FAQList";

export default async function FAQsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let faqs: Awaited<ReturnType<typeof api.faqs.list>> = [];
  try {
    faqs = await api.faqs.list(id);
  } catch {}

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          FAQs
        </h2>
        <p className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>
          The AI uses these to answer guest questions. Add common questions about your property.
        </p>
      </div>

      <FAQForm businessId={id} />

      {faqs.length === 0 ? (
        <div
          className="rounded-xl border-2 border-dashed p-12 text-center"
          style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}
        >
          <p className="font-medium mb-1">No FAQs yet</p>
          <p className="text-sm">Add frequently asked questions to help the AI assist guests.</p>
        </div>
      ) : (
        <FAQList faqs={faqs} />
      )}
    </div>
  );
}
