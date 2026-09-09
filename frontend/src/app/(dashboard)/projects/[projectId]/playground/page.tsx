import {WorkspaceEntry} from "@/modules/ragforge/workspace-entry";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";

export default async function PlaygroundPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <RAGForgeCapabilityGate projectId={projectId}><WorkspaceEntry projectId={projectId} /></RAGForgeCapabilityGate>;
}
