import {describe, expect, it} from "vitest";
import type {Project, User} from "@/lib/types";
import {hasProjectCapability, projectNavigation, workspaceNavigation} from "./navigation";

const user = {user_id: "user-1", global_role: "member"} as User;
const project = {
  project_id: "project-1",
  created_by: "user-2",
  capabilities: ["ragforge"],
  permissions: {read: true, write: false, manage: false},
} as Project;

describe("capability navigation", () => {
  it("shows RAGForge screens only for enabled projects", () => {
    expect(projectNavigation(project, user).map((group) => group.label)).toContain("RAGForge");
    expect(workspaceNavigation([{...project, capabilities: []}]).map((group) => group.label)).not.toContain("RAGForge");
  });

  it("hides project settings without write permission", () => {
    const labels = projectNavigation(project, user).flatMap((group) => group.items.map((item) => item.label));
    expect(labels).not.toContain("Settings");
  });

  it("keeps legacy projects RAGForge-enabled during rolling deploys", () => {
    expect(hasProjectCapability({...project, capabilities: undefined}, "ragforge")).toBe(true);
  });
});
