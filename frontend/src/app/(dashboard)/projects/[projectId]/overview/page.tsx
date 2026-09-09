import {ProjectShell as LabShell} from "@/platform/projects/project-shell";
import {ProjectOverview} from "@/platform/projects/project-overview";

export default async function ProjectOverviewPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><ProjectOverview projectId={projectId} /></LabShell>;
}
