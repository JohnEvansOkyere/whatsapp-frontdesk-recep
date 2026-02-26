"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Calendar, Bed, HelpCircle, Settings } from "lucide-react";

const tabs = [
  { href: "", label: "Overview", icon: LayoutDashboard },
  { href: "bookings", label: "Bookings", icon: Calendar },
  { href: "rooms", label: "Rooms", icon: Bed },
  { href: "faqs", label: "FAQs", icon: HelpCircle },
  { href: "settings", label: "Settings", icon: Settings },
];

export function BusinessNav({
  businessId,
  businessName,
}: {
  businessId: string;
  businessName: string;
}) {
  const pathname = usePathname();
  const base = `/businesses/${businessId}`;

  return (
    <div
      className="border-b"
      style={{ background: "var(--bg-secondary)", borderColor: "var(--border)" }}
    >
      <div className="px-8 pt-6 pb-0">
        <div className="flex items-center gap-2 mb-1">
          <Link
            href="/businesses"
            className="text-xs transition-colors"
            style={{ color: "var(--text-muted)" }}
          >
            Properties
          </Link>
          <span style={{ color: "var(--text-muted)" }}>/</span>
        </div>
        <h1 className="text-xl font-semibold" style={{ color: "var(--text-primary)" }}>
          {businessName}
        </h1>

        <nav className="mt-4 flex gap-1">
          {tabs.map(({ href, label, icon: Icon }) => {
            const path = href ? `${base}/${href}` : base;
            const active = pathname === path;
            return (
              <Link
                key={href}
                href={path}
                className="flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors"
                style={{
                  borderColor: active ? "var(--accent)" : "transparent",
                  color: active ? "var(--accent)" : "var(--text-secondary)",
                }}
              >
                <Icon size={15} />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
