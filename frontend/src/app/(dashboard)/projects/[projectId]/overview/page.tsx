import {LabShell} from "@/components/labs/lab-shell";
import {ProjectOverview} from "@/components/project-overview";

export default async function ProjectOverviewPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><ProjectOverview projectId={projectId} /></LabShell>;
}
