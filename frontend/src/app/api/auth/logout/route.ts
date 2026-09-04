import {NextResponse} from "next/server";
import {cookies} from "next/headers";
import {AUTH_COOKIE, backendUrl} from "@/lib/server-auth";

export async function POST() {
  const cookieStore = await cookies();
  const token = cookieStore.get(AUTH_COOKIE)?.value;
  if (token) {
    await fetch(backendUrl("/auth/logout"), {
      method: "POST",
      headers: {Authorization: `Bearer ${token}`},
      cache: "no-store",
    }).catch(() => undefined);
  }
  const response = NextResponse.json({authenticated: false});
  response.cookies.set(AUTH_COOKIE, "", {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    expires: new Date(0),
  });
  return response;
}
