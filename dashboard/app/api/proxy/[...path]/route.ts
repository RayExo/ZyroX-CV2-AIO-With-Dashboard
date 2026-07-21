/**
 * Authenticated server-side proxy to the bot FastAPI backend.
 * - Requires Discord OAuth session
 * - Guild routes: user must have Manage Server / Admin on that guild
 * - Admin routes: user must be in ADMIN_IDS
 */

import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { isAdmin } from "@/lib/utils";
import { userCanManageGuild } from "@/lib/guild-auth";

const BOT_API_URL =
  process.env.DASHBOARD_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000/api/v1";

const API_KEY = process.env.DASHBOARD_API_KEY;

type RouteContext = { params: { path: string[] } };

async function authorizeProxyRequest(
  path: string,
  session: { user?: { id?: string }; accessToken?: string }
): Promise<NextResponse | null> {
  if (!session.user) {
    return NextResponse.json({ detail: "Unauthorized — sign in required." }, { status: 401 });
  }

  const accessToken = session.accessToken;
  if (!accessToken) {
    return NextResponse.json({ detail: "Missing Discord access token." }, { status: 401 });
  }

  const normalized = path.replace(/\/$/, "");

  if (normalized.startsWith("admin")) {
    if (!isAdmin(session.user.id)) {
      return NextResponse.json({ detail: "Forbidden — admin access required." }, { status: 403 });
    }
    return null;
  }

  const guildMatch = normalized.match(/^guilds\/(\d+)/);
  if (guildMatch) {
    const guildId = guildMatch[1];
    const allowed = await userCanManageGuild(accessToken, guildId);
    if (!allowed) {
      return NextResponse.json(
        { detail: "Forbidden — you cannot manage this server." },
        { status: 403 }
      );
    }
  }

  return null;
}

async function proxyRequest(request: NextRequest, { params }: RouteContext) {
  if (!API_KEY) {
    return NextResponse.json(
      { detail: "DASHBOARD_API_KEY is not configured on the dashboard server." },
      { status: 500 }
    );
  }

  const session = await getServerSession(authOptions);
  const path = params.path.join("/");

  const authError = await authorizeProxyRequest(path, session ?? {});
  if (authError) return authError;

  const targetUrl = `${BOT_API_URL.replace(/\/$/, "")}/${path}${request.nextUrl.search}`;

  const headers = new Headers();
  headers.set("Authorization", `Bearer ${API_KEY}`);

  if (session?.accessToken) {
    headers.set("X-Discord-Access-Token", session.accessToken);
  }
  if (session?.user?.id) {
    headers.set("X-Discord-User-Id", session.user.id);
  }

  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("Content-Type", contentType);
  }

  const init: RequestInit = {
    method: request.method,
    headers,
    cache: "no-store",
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.text();
  }

  try {
    const response = await fetch(targetUrl, init);
    let body = await response.text();

    // Filter guild list to servers the user can manage (bot guild list ∩ user admin guilds)
    const normalized = path.replace(/\/$/, "");
    if (
      request.method === "GET" &&
      normalized === "guilds" &&
      response.ok &&
      session?.accessToken
    ) {
      try {
        const botGuilds = JSON.parse(body) as Array<{ id: string }>;
        const { fetchUserGuilds, canManageGuild } = await import("@/lib/guild-auth");
        const userGuilds = await fetchUserGuilds(session.accessToken);
        const manageableIds = new Set(
          userGuilds.filter(canManageGuild).map((g) => String(g.id))
        );
        const filtered = botGuilds.filter((g) => manageableIds.has(String(g.id)));
        body = JSON.stringify(filtered);
      } catch {
        // If filtering fails, return original response rather than breaking the dashboard
      }
    }

    return new NextResponse(body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (error) {
    console.error(`[API Proxy] Failed to reach bot API at ${targetUrl}:`, error);
    return NextResponse.json(
      { detail: "Could not connect to the bot API backend." },
      { status: 502 }
    );
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PATCH = proxyRequest;
export const DELETE = proxyRequest;
export const PUT = proxyRequest;
