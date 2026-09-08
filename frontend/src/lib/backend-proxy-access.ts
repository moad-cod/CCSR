const PUBLIC_GET_PATH = /^\/publications(?:\/[^/]+)?$/;


export function isPublicBackendRequest(method: string, path: string) {
  return method === "GET" && PUBLIC_GET_PATH.test(path);
}
