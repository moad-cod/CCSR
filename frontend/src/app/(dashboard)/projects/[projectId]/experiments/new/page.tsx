import {ProjectShell as LabShell} from "@/platform/projects/project-shell";
import {NewExperiment} from "@/platform/projects/experiment-editor";

export default async function NewExperimentPage({params}: {params: Promise<{projectId: string}>}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><NewExperiment projectId={projectId} /></LabShell>;
}
