import {QueryDetail} from "@/components/query-detail";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";
export default async function QueryPage({params}: {params: Promise<{projectId: string; queryId: string}>}) {const {projectId, queryId} = await params; return <RAGForgeCapabilityGate projectId={projectId}><QueryDetail projectId={projectId} queryId={queryId} /></RAGForgeCapabilityGate>;}
