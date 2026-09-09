import {ObservabilityDashboard} from "@/modules/ragforge/observability-dashboard";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";
export default async function ProjectObservabilityPage({params}: {params: Promise<{projectId: string}>}) {const {projectId} = await params; return <RAGForgeCapabilityGate projectId={projectId}><ObservabilityDashboard projectId={projectId} /></RAGForgeCapabilityGate>;}
