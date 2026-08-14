import {LabResearchPage} from "@/components/labs/lab-research-page";
import {LabShell} from "@/components/labs/lab-shell";

export default async function ResearchPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabResearchPage projectId={projectId} /></LabShell>;
}
