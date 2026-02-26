"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";

export function CopyIdButton({ id }: { id: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="rounded-lg p-1.5 transition-colors"
      style={{ color: copied ? "var(--success)" : "var(--text-muted)" }}
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </button>
  );
}
