"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "", label: "Overview" },
  { href: "bookings", label: "Bookings" },
  { href: "faqs", label: "FAQs" },
  { href: "services", label: "Services" },
  { href: "settings", label: "Settings" },
];

export function BusinessNav({ businessId, businessName }: { businessId: string; businessName: string }) {
  const pathname = usePathname();
  const base = `/businesses/${businessId}`;

  return (
    <div className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6">
        <div className="flex items-center gap-4">
          <Link href="/businesses" className="text-sm text-slate-500 hover:text-slate-700">
            Businesses
          </Link>
          <span className="text-slate-400">/</span>
          <span className="font-medium text-slate-900">{businessName}</span>
        </div>
        <nav className="mt-3 flex gap-1">
          {tabs.map(({ href, label }) => {
            const path = href ? `${base}/${href}` : base;
            const active = pathname === path;
            return (
              <Link
                key={href}
                href={path}
                className={
                  "rounded-md px-3 py-2 text-sm font-medium " +
                  (active
                    ? "bg-slate-100 text-slate-900"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900")
                }
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}