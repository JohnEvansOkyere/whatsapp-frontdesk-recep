import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4">
      <p className="text-lg font-medium text-slate-900">Page not found</p>
      <Link href="/businesses" className="mt-4 text-sm text-slate-600 hover:text-slate-900">
        Back to Businesses
      </Link>
    </div>
  );
}
