import {DocumentDetail} from "@/components/document-detail";
import {RAGForgeCapabilityGate} from "@/modules/ragforge/capability-gate";
export default async function VersionsPage({params}: {params: Promise<{projectId: string; documentId: string}>}) {const {projectId, documentId} = await params; return <RAGForgeCapabilityGate projectId={projectId}><DocumentDetail projectId={projectId} documentId={documentId} initialTab="versions" /></RAGForgeCapabilityGate>;}
