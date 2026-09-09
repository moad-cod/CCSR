import {LabReproducePage} from "@/components/labs/lab-reproduce-page";
import {ProjectShell as LabShell} from "@/platform/projects/project-shell";

export default async function ReproducePage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabReproducePage projectId={projectId} /></LabShell>;
}
