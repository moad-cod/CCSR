import {ProjectOnboarding} from "@/components/onboarding/project-onboarding";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";

export default async function ProjectOnboardingPage({params}: {params: Promise<{projectId: string}>}) {
  const {projectId} = await params;
  return <RAGForgeCapabilityGate projectId={projectId}><ProjectOnboarding projectId={projectId} /></RAGForgeCapabilityGate>;
}
