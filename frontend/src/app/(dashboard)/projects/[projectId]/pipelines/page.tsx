import {ProjectShell as LabShell} from "@/platform/projects/project-shell";
import {ProjectPipelinesPage} from "@/modules/ragforge/project-pipelines-page";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";

export default async function PipelinesPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><RAGForgeCapabilityGate projectId={projectId}><ProjectPipelinesPage projectId={projectId} /></RAGForgeCapabilityGate></LabShell>;
}
