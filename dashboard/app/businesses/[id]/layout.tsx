import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { BusinessNav } from "@/app/components/BusinessNav";

export const dynamic = "force-dynamic";

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
      <div className="p-8">{children}</div>
    </>
  );
}
