import {BrainCircuit, Camera, Cpu, Database, FlaskConical, Layers3, Network, Sigma} from "lucide-react";
import type {IngestionRun, Project} from "@/lib/types";

export const labDomains = [
  {id: "all", label: "All labs", shortLabel: "All", color: "var(--ink-muted)", icon: FlaskConical, keywords: []},
  {id: "rag", label: "RAG / Retrieval", shortLabel: "RAG", color: "var(--domain-rag)", icon: Network, keywords: ["rag", "retrieval", "search", "ground", "citation", "chunk", "qdrant"]},
  {id: "nlp", label: "NLP / LLM", shortLabel: "NLP", color: "var(--domain-nlp)", icon: BrainCircuit, keywords: ["nlp", "llm", "language", "text", "qwen", "llama", "prompt"]},
  {id: "cv", label: "Computer Vision", shortLabel: "CV", color: "var(--domain-cv)", icon: Camera, keywords: ["vision", "image", "cv", "ocr", "visual", "camera"]},
  {id: "ml", label: "Machine Learning", shortLabel: "ML", color: "var(--domain-ml)", icon: Cpu, keywords: ["ml", "learning", "model", "training", "classifier", "regression"]},
  {id: "multimodal", label: "Multimodal", shortLabel: "Multi", color: "var(--domain-multimodal)", icon: Layers3, keywords: ["multimodal", "audio", "video", "vision-language", "vlm"]},
  {id: "systems", label: "AI Systems", shortLabel: "Systems", color: "var(--domain-ai-systems)", icon: Database, keywords: ["system", "agent", "pipeline", "infra", "serving", "benchmark"]},
  {id: "math", label: "Mathematics", shortLabel: "Math", color: "var(--domain-math)", icon: Sigma, keywords: ["math", "proof", "optimization", "algebra", "theorem"]},
] as const;

export type LabDomain = (typeof labDomains)[number];
export type LabDomainId = LabDomain["id"];
export type LabStats = {documents: number | null; active: number | null; indexed: number | null; latestRun: IngestionRun | null};

export function inferDomain(project: Project): LabDomain {
  const haystack = `${project.name} ${project.qdrant_collection ?? ""} ${project.collection ?? ""}`.toLowerCase();
  return labDomains.find((domain) => domain.id !== "all" && domain.keywords.some((keyword) => haystack.includes(keyword))) ?? labDomains[1];
}

export function readiness(stats: LabStats) {
  if (stats.active) return "processing";
  if (stats.indexed) return "ready";
  if (stats.documents) return "sources added";
  return "draft";
}
