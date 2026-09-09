"use client";

import {useQuery} from "@tanstack/react-query";
import {Layers3} from "lucide-react";
import Link from "next/link";
import type {ReactNode} from "react";
import {EmptyState} from "@/components/ui/empty-state";
import {ErrorState} from "@/components/ui/error-state";
import {LoadingState} from "@/components/ui/loading-state";
import {apiFetch} from "@/lib/api";
import type {ProjectOverviewContract} from "@/lib/types";
import {hasProjectCapability} from "@/platform/navigation/navigation";

export function RAGForgeCapabilityGate({projectId, children}: {projectId: string; children: ReactNode}) {
  const overview = useQuery({
    queryKey: ["project-overview", projectId],
    queryFn: () => apiFetch<ProjectOverviewContract>(`/projects/${projectId}/overview`),
  });
  if (overview.isLoading) return <LoadingState label="Checking project capabilities" rows={4} />;
  if (overview.isError || !overview.data) return <ErrorState title="Project could not be loaded" description="The project is unavailable or your access has changed." onRetry={() => void overview.refetch()} />;
  if (!hasProjectCapability(overview.data.project, "ragforge")) {
    return <div className="mx-auto max-w-3xl py-12"><EmptyState icon={Layers3} title="RAGForge is not enabled" description="This route is retained as a compatibility alias, but its screens are available only when the project enables the RAGForge capability." /><div className="mt-4 text-center"><Link href={`/projects/${projectId}/overview`} className="text-xs font-medium text-[var(--accent)]">Return to project overview</Link></div></div>;
  }
  return children;
}
