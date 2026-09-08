import {PublicationDetailPage} from "@/platform/publication/publication-detail-page";


export default async function Page({params}: {params: Promise<{slug: string}>}) {
  const {slug} = await params;
  return <PublicationDetailPage slug={slug} />;
}
