import {redirect} from "next/navigation";

export default async function ProjectEvaluationPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  redirect(`/projects/${projectId}/results`);
}
