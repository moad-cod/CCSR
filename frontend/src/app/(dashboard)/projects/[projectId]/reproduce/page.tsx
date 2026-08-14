import {LabReproducePage} from "@/components/labs/lab-reproduce-page";
import {LabShell} from "@/components/labs/lab-shell";

export default async function ReproducePage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabReproducePage projectId={projectId} /></LabShell>;
}
