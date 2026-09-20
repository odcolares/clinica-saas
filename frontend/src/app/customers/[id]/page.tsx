import { notFound } from "next/navigation"
import { CustomerDetailContent } from "@/components/customers/customer-detail-content"

interface CustomerDetailPageProps {
  params: Promise<{ id: string }>
}

export default async function CustomerDetailPage({ params }: CustomerDetailPageProps) {
  const { id } = await params
  return <CustomerDetailContent customerId={id} />
}
