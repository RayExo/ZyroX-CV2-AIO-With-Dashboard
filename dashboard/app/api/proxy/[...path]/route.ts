/**
 * Same-origin API proxy (audit C1, C3, H3).
 *
 * Client Components call /api/proxy/<backend-path> instead of the bot backend
 * directly. This handler:
 *   1. Attaches the server-only DASHBOARD_API_KEY (never shipped to browser).
 *   2. Requires an authenticated NextAuth session.
 *   3. Enforces authorization:
 *        - /admin/*           → server admins only
 *        - /guilds/{id}/*     → caller must MANAGE_GUILD / ADMINISTRATOR on it
 *
 * Server Components do NOT go through this proxy — they call the backend
 * directly (lib/api.ts dual mode) and must perform their own membership check
 * (see app/dashboard/guild/[guildId]/layout.tsx).
 */

import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { isAdmin, userCanManageGuild } from "@/lib/auth-utils";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const API_KEY = process.env.DASHBOARD_API_KEY;

type Ctx = { params: { path: string[] } };

async function handle(req: NextRequest, ctx: Ctx, method: string) {
  if (!API_KEY) {
    return NextResponse.json({ detail: "Backend API key not configured." }, { status: 500 });
  }

  const session = (await getServerSession(authOptions)) as any;
  if (!session?.user) {
    return NextResponse.json({ detail: "Unauthorized" }, { status: 401 });
  }
  const accessToken: string | undefined = session.accessToken;

  const path = (ctx.params.path || []).join("/");
  const segments = path.split("/").filter(Boolean);

  // --- Authorization ---
  if (segments[0] === "admin") {
    if (!isAdmin(session.user.id)) {
      return NextResponse.json({ detail: "Forbidden: administrators only." }, { status: 403 });
    }
  } else if (segments[0] === "guilds" && segments[1]) {
    if (!(await userCanManageGuild(accessToken, segments[1]))) {
      return NextResponse.json(
        { detail: "Forbidden: you do not manage this server." },
        { status: 403 }
      );
    }
  }

  const url = `${BACKEND_URL}/${path}${req.nextUrl.search}`;
  const headers: Record<string, string> = {
    Authorization: `Bearer ${API_KEY}`,
  };
  const init: RequestInit = { method, headers };

  if (method !== "GET" && method !== "HEAD") {
    headers["Content-Type"] = "application/json";
    init.body = await req.text();
  }

  try {
    const backend = await fetch(url, init);
    const text = await backend.text();
    return new NextResponse(text, {
      status: backend.status,
      headers: {
        "Content-Type": backend.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (err: any) {
    return NextResponse.json(
      { detail: `Backend unreachable: ${err?.message || "unknown error"}` },
      { status: 502 }
    );
  }
}

export async function GET(req: NextRequest, ctx: Ctx) {
  return handle(req, ctx, "GET");
}
export async function POST(req: NextRequest, ctx: Ctx) {
  return handle(req, ctx, "POST");
}
export async function PATCH(req: NextRequest, ctx: Ctx) {
  return handle(req, ctx, "PATCH");
}
export async function DELETE(req: NextRequest, ctx: Ctx) {
  return handle(req, ctx, "DELETE");
}
