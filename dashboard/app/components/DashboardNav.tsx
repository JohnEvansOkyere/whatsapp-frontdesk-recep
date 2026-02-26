import Link from "next/link";

export function DashboardNav() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-14 max-w-7xl items-center px-4 sm:px-6">
        <Link href="/" className="text-lg font-semibold text-slate-900">
          Front Desk
        </Link>
        <nav className="ml-8 flex gap-6">
          <Link
            href="/businesses"
            className="text-sm font-medium text-slate-600 hover:text-slate-900"
          >
            Businesses
          </Link>
        </nav>
      </div>
    </header>
  );
}
