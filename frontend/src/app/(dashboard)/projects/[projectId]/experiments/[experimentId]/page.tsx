import {ProjectShell as LabShell} from "@/platform/projects/project-shell";
import {ExperimentDetail} from "@/platform/projects/experiment-editor";

export default async function ExperimentDetailPage({params}: {params: Promise<{projectId: string; experimentId: string}>}) {
  const {projectId, experimentId} = await params;
  return <LabShell projectId={projectId}><ExperimentDetail projectId={projectId} experimentId={experimentId} /></LabShell>;
}
