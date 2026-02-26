import { api } from "@/lib/api";
import { FAQForm } from "../FAQForm";
import { FAQImport } from "../FAQImport";
import { DeleteFAQButton } from "../DeleteFAQButton";

export default async function FAQsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let faqs: Awaited<ReturnType<typeof api.faqs.list>> = [];
  try {
    faqs = await api.faqs.list(id);
  } catch {
    // show empty
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">FAQs</h2>
          <p className="mt-1 text-sm text-slate-500">
            Questions and answers the bot uses to respond to customers.
          </p>
        </div>
        <div className="flex gap-2">
          <FAQImport businessId={id} />
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-medium text-slate-700">Add FAQ</h3>
        <FAQForm businessId={id} />
      </div>

      {faqs.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50/50 py-12 text-center text-slate-600">
          No FAQs yet. Add one above or import from file.
        </div>
      ) : (
        <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
          {faqs.map((faq) => (
            <li key={faq.id} className="px-4 py-4 sm:px-6">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-slate-900">{faq.question}</p>
                  <p className="mt-1 text-sm text-slate-600">{faq.answer}</p>
                  {faq.keywords?.length > 0 && (
                    <p className="mt-1 text-xs text-slate-400">
                      Keywords: {faq.keywords.join(", ")}
                    </p>
                  )}
                </div>
                <DeleteFAQButton faqId={faq.id} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
