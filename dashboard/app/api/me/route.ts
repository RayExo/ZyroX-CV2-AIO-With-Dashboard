/**
 * Returns the caller's session + admin status without exposing ADMIN_IDS.
 *
 * Client Components (e.g. the dashboard sidebar) fetch this to decide whether
 * to show the Admin link, instead of reading NEXT_PUBLIC_ADMIN_IDS from the
 * bundle (audit finding H4).
 */

import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { isAdmin } from "@/lib/auth-utils";

export async function GET() {
  const session = (await getServerSession(authOptions)) as any;
  if (!session?.user) {
    return NextResponse.json({ authenticated: false, isAdmin: false }, { status: 200 });
  }
  return NextResponse.json({
    authenticated: true,
    isAdmin: isAdmin(session.user.id),
  });
}
