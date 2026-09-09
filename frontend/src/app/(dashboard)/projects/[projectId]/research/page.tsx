import {LabResearchPage} from "@/components/labs/lab-research-page";
import {ProjectShell as LabShell} from "@/platform/projects/project-shell";

export default async function ResearchPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabResearchPage projectId={projectId} /></LabShell>;
}
