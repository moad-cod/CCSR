import {LabArtifactsPage} from "@/components/labs/lab-artifacts-page";
import {ProjectShell as LabShell} from "@/platform/projects/project-shell";

export default async function ArtifactsPage({
  params,
}: {
  params: Promise<{projectId: string}>;
}) {
  const {projectId} = await params;
  return <LabShell projectId={projectId}><LabArtifactsPage projectId={projectId} /></LabShell>;
}
