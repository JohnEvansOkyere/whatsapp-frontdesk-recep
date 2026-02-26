import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex h-screen items-center justify-center p-8">
      <div className="text-center">
        <p className="text-6xl font-bold" style={{ color: "var(--accent)" }}>404</p>
        <p className="mt-4 text-lg font-medium" style={{ color: "var(--text-primary)" }}>
          Page not found
        </p>
        <p className="mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
          The page you are looking for does not exist.
        </p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-lg px-5 py-2.5 text-sm font-medium"
          style={{ background: "var(--accent)", color: "var(--bg-primary)" }}
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
