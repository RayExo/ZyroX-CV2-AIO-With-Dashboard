/**
 * Server-only authorization helpers.
 *
 * SECURITY: this module reads ADMIN_IDS (a server-only env var, no NEXT_PUBLIC_)
 * and must ONLY be imported from Server Components / Route Handlers. Never
 * import from a Client Component — that would inline the admin IDs into the
 * browser bundle (audit finding H4).
 */

const ADMINISTRATOR = BigInt(0x8);
const MANAGE_GUILD = BigInt(0x20);

export function isAdmin(userId?: string | null): boolean {
  if (!userId) return false;
  const ids = (process.env.ADMIN_IDS || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  return ids.includes(userId);
}

/**
 * Returns true if the Discord user (via their OAuth access token) is a member
 * of `guildId` with ADMINISTRATOR or MANAGE_GUILD permissions, or owns it.
 * Result is cached briefly via fetch's revalidate to limit Discord API calls.
 */
export async function userCanManageGuild(
  accessToken: string | undefined,
  guildId: string
): Promise<boolean> {
  if (!accessToken) return false;
  try {
    const res = await fetch("https://discord.com/api/users/@me/guilds", {
      headers: { Authorization: `Bearer ${accessToken}` },
      next: { revalidate: 30 },
    });
    if (!res.ok) return false;
    const guilds: Array<{ id: string; permissions: string; owner: boolean }> =
      await res.json();
    const g = guilds.find((x) => x.id === guildId);
    if (!g) return false;
    let perms = 0n;
    try {
      perms = BigInt(g.permissions ?? "0");
    } catch {
      perms = 0n;
    }
    return (
      (perms & ADMINISTRATOR) === ADMINISTRATOR ||
      (perms & MANAGE_GUILD) === MANAGE_GUILD ||
      !!g.owner
    );
  } catch {
    return false;
  }
}
