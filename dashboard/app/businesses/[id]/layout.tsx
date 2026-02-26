import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { BusinessNav } from "@/app/components/BusinessNav";

export default async function BusinessLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let business;
  try {
    business = await api.businesses.get(id);
  } catch {
    notFound();
  }

  return (
    <>
      <BusinessNav businessId={id} businessName={business.name} />
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6">{children}</div>
    </>
  );
}
