"use client";

import {useQuery} from "@tanstack/react-query";
import {apiFetch} from "@/lib/api";
import type {ProjectOverviewContract, RAGWorkspaceOverview} from "@/lib/types";

export function useWorkspaceOverview(options: {documents?: boolean; runs?: boolean; history?: boolean; enabled?: boolean} = {}) {
  const includes = [
    options.documents === false ? null : "documents",
    options.runs ? "runs" : null,
    options.history ? "history" : null,
  ].filter((value): value is string => Boolean(value));
  const include = includes.join(",");
  const projectsQuery = useQuery({
    queryKey: ["project-overviews"],
    queryFn: () => apiFetch<ProjectOverviewContract[]>("/projects/overview"),
    enabled: options.enabled !== false,
  });
  const overviewQuery = useQuery({
    queryKey: ["ragforge", "workspace-overview", include],
    queryFn: () => apiFetch<RAGWorkspaceOverview>(`/rag/workspace/overview?include=${include}`),
    enabled: options.enabled !== false,
  });
  const projectOverviews = projectsQuery.data ?? [];
  const projects = projectOverviews.map((item) => item.project);
  const platformSummaries = new Map(projectOverviews.map((item) => [item.project.project_id, item.counts]));
  const projectMap = new Map(projects.map((project) => [project.project_id, project]));
  const documents = (overviewQuery.data?.documents ?? []).map((document) => ({...document, project: projectMap.get(document.project_id)}));
  const runs = (overviewQuery.data?.runs ?? []).map((run) => ({...run, project: projectMap.get(run.project_id)}));
  const history = (overviewQuery.data?.history ?? []).map((item) => ({...item, project: projectMap.get(item.project_id)}));
  const summaries = new Map((overviewQuery.data?.summaries ?? []).map((summary) => [summary.project_id, summary]));
  return {
    projects,
    projectMap,
    summaries,
    platformSummaries,
    documents,
    runs,
    history,
    pending: options.enabled !== false && (projectsQuery.isLoading || overviewQuery.isLoading),
    error: projectsQuery.isError || overviewQuery.isError,
    refetch: async () => {
      await Promise.all([projectsQuery.refetch(), overviewQuery.refetch()]);
    },
  };
}
