import {IngestionRunDetail} from "@/components/ingestion-run-detail";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";
export default async function RunDetailPage({params}: {params: Promise<{projectId: string; runId: string}>}) {const {projectId, runId} = await params; return <RAGForgeCapabilityGate projectId={projectId}><IngestionRunDetail projectId={projectId} runId={runId} /></RAGForgeCapabilityGate>;}
