"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, type FAQ } from "@/lib/api";
import { Trash2 } from "lucide-react";

export function FAQList({ faqs }: { faqs: FAQ[] }) {
  return (
    <div className="space-y-3">
      {faqs.map((faq) => (
        <FAQItem key={faq.id} faq={faq} />
      ))}
    </div>
  );
}

function FAQItem({ faq }: { faq: FAQ }) {
  const router = useRouter();
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.faqs.delete(faq.id);
      router.refresh();
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div
      className="group rounded-xl border p-5 transition-all"
      style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
            {faq.question}
          </p>
          <p className="mt-2 text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            {faq.answer}
          </p>
        </div>
        <button
          onClick={handleDelete}
          disabled={deleting}
          className="mt-1 rounded-lg p-2 opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ color: "var(--error)" }}
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
}
