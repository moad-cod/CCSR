import {ProjectShell as LabShell} from "@/platform/projects/project-shell";
import {LabTestPage} from "@/components/labs/lab-test-page";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";

export default async function TestPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><RAGForgeCapabilityGate projectId={projectId}><LabTestPage projectId={projectId} /></RAGForgeCapabilityGate></LabShell>;
}
