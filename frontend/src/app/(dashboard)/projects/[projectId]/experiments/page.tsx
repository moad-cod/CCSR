import {ProjectShell as LabShell} from "@/platform/projects/project-shell";
import {LabExperimentsPage} from "@/components/labs/lab-experiments-page";

export default async function ProjectExperimentsPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabExperimentsPage projectId={projectId} /></LabShell>;
}
