"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Plus, ChevronDown, ChevronUp } from "lucide-react";

export function FAQForm({ businessId }: { businessId: string }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || !answer.trim()) return;
    setLoading(true);
    try {
      await api.faqs.add(businessId, {
        question: question.trim(),
        answer: answer.trim(),
      });
      setQuestion("");
      setAnswer("");
      setOpen(false);
      router.refresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="rounded-xl border"
      style={{ background: "var(--bg-card)", borderColor: "var(--border)" }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between p-5 text-left"
      >
        <div className="flex items-center gap-3">
          <div
            className="flex h-9 w-9 items-center justify-center rounded-lg"
            style={{ background: "var(--accent-muted)", color: "var(--accent)" }}
          >
            <Plus size={18} />
          </div>
          <div>
            <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
              Add FAQ
            </p>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              Add a question and answer for the AI to use
            </p>
          </div>
        </div>
        {open ? (
          <ChevronUp size={18} style={{ color: "var(--text-muted)" }} />
        ) : (
          <ChevronDown size={18} style={{ color: "var(--text-muted)" }} />
        )}
      </button>

      {open && (
        <form
          onSubmit={handleSubmit}
          className="border-t px-5 pb-5 pt-4 space-y-4"
          style={{ borderColor: "var(--border)" }}
        >
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
              Question
            </label>
            <input
              type="text"
              placeholder="e.g. What is check-in time?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
              Answer
            </label>
            <textarea
              rows={3}
              placeholder="Check-in is from 2:00 PM. Early check-in may be available upon request."
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              className="w-full"
              required
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg px-5 py-2 text-sm font-semibold disabled:opacity-50"
              style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
            >
              {loading ? "Adding..." : "Add FAQ"}
            </button>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-lg border px-5 py-2 text-sm font-medium"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
