import {
  Archive,
  BarChart3,
  BookOpenText,
  Building2,
  Database,
  FlaskConical,
  FolderKanban,
  Gauge,
  History,
  Home,
  RotateCcw,
  Settings,
  Sparkles,
  TestTube2,
  UserRound,
  Workflow,
} from "lucide-react";
import type {LucideIcon} from "lucide-react";
import type {Project, ProjectPermissions, User} from "@/lib/types";

export type NavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

export type NavigationGroup = {
  label: string;
  items: NavigationItem[];
};

export function hasProjectCapability(project: Project | undefined, capability: string) {
  if (!project) return false;
  // During a rolling backend deploy the omitted field represents the legacy
  // RAGForge-only project contract. An explicit empty list remains authoritative.
  return project.capabilities === undefined
    ? capability === "ragforge"
    : project.capabilities.includes(capability);
}

export function projectPermissions(
  project: Project | undefined,
  user: User | undefined,
): ProjectPermissions {
  if (!project) return {read: false, write: false, manage: false};
  if (project.permissions) return project.permissions;
  const mayManage = user?.global_role === "admin" || project.created_by === user?.user_id;
  return {read: true, write: mayManage, manage: mayManage};
}

export function projectNavigation(
  project: Project,
  user?: User,
): NavigationGroup[] {
  const projectId = project.project_id;
  const permissions = projectPermissions(project, user);
  const groups: NavigationGroup[] = [
    {
      label: "Platform",
      items: [
        {label: "Overview", href: `/projects/${projectId}/overview`, icon: Home},
        {label: "Research", href: `/projects/${projectId}/research`, icon: BookOpenText},
        {label: "Experiments", href: `/projects/${projectId}/experiments`, icon: FlaskConical},
        {label: "Results", href: `/projects/${projectId}/results`, icon: BarChart3},
        {label: "Artifacts", href: `/projects/${projectId}/artifacts`, icon: Archive},
        {label: "Reproduce", href: `/projects/${projectId}/reproduce`, icon: RotateCcw},
      ],
    },
  ];
  if (hasProjectCapability(project, "ragforge")) {
    groups.push({
      label: "RAGForge",
      items: [
        {label: "Sources", href: `/projects/${projectId}/sources`, icon: Database},
        {label: "Playground", href: `/projects/${projectId}/playground`, icon: TestTube2},
        {label: "Pipelines", href: `/projects/${projectId}/pipelines`, icon: Workflow},
        {label: "Observability", href: `/projects/${projectId}/observability`, icon: Gauge},
      ],
    });
  }
  const manageItems: NavigationItem[] = [
    {label: "All projects", href: "/projects", icon: FolderKanban},
  ];
  if (permissions.write) {
    manageItems.push({label: "Settings", href: `/projects/${projectId}/settings`, icon: Settings});
  }
  groups.push({label: "Manage", items: manageItems});
  return groups;
}

export function workspaceNavigation(projects: Project[]): NavigationGroup[] {
  const hasRAGForge = projects.some((project) => hasProjectCapability(project, "ragforge"));
  const groups: NavigationGroup[] = [
    {
      label: "Workspace",
      items: [
        {label: "Home", href: "/home", icon: Home},
        {label: "Labs", href: "/labs", icon: FlaskConical},
        {label: "Projects", href: "/projects", icon: FolderKanban},
      ],
    },
    {
      label: "Research",
      items: [
        {label: "Experiments", href: "/experiments", icon: Sparkles},
        {label: "Comparisons", href: "/comparisons", icon: BarChart3},
      ],
    },
  ];
  if (hasRAGForge) {
    groups.push({
      label: "RAGForge",
      items: [
        {label: "Sources", href: "/documents", icon: Database},
        {label: "History", href: "/history", icon: History},
        {label: "Runs", href: "/runs", icon: Workflow},
        {label: "Observability", href: "/observability", icon: Gauge},
      ],
    });
  }
  groups.push({
    label: "Manage",
    items: [
      {label: "Organization", href: "/organization", icon: Building2},
      {label: "Settings", href: "/settings/profile", icon: Settings},
      {label: "Profile", href: "/settings/profile", icon: UserRound},
    ],
  });
  return groups;
}
