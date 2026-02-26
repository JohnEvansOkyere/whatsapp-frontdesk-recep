"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Building2, LayoutDashboard, Settings, HelpCircle } from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/businesses", label: "Properties", icon: Building2 },
];

const bottomItems = [
  { href: "/help", label: "Help", icon: HelpCircle },
  { href: "/account", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="flex h-screen w-[240px] flex-col border-r"
      style={{
        background: "var(--bg-secondary)",
        borderColor: "var(--border)",
      }}
    >
      <div className="flex h-16 items-center gap-3 px-5">
        <div
          className="flex h-8 w-8 items-center justify-center rounded-lg text-sm font-bold"
          style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
        >
          FD
        </div>
        <div>
          <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
            Front Desk
          </p>
          <p className="text-[11px]" style={{ color: "var(--text-muted)" }}>
            Hotel Management
          </p>
        </div>
      </div>

      <nav className="mt-4 flex flex-1 flex-col gap-1 px-3">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active =
            href === "/"
              ? pathname === "/"
              : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
              style={{
                background: active ? "var(--accent-muted)" : "transparent",
                color: active ? "var(--accent)" : "var(--text-secondary)",
              }}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t px-3 py-3" style={{ borderColor: "var(--border)" }}>
        {bottomItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
            style={{ color: "var(--text-muted)" }}
          >
            <Icon size={16} />
            {label}
          </Link>
        ))}
      </div>
    </aside>
  );
}
