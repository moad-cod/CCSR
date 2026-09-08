import {describe, expect, it} from "vitest";
import {isPublicBackendRequest} from "@/lib/backend-proxy-access";


describe("public backend proxy allowlist", () => {
  it("allows only publication reads without a session", () => {
    expect(isPublicBackendRequest("GET", "/publications")).toBe(true);
    expect(isPublicBackendRequest("GET", "/publications/retrieval-results")).toBe(true);
    expect(isPublicBackendRequest("POST", "/publications")).toBe(false);
    expect(isPublicBackendRequest("GET", "/publications/slug/revisions")).toBe(false);
    expect(isPublicBackendRequest("GET", "/artifacts")).toBe(false);
  });
});
