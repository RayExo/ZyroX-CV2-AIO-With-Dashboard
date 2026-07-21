/**
 * Discord guild permission helpers for dashboard access control.
 */

export interface DiscordGuild {
  id: string;
  permissions: string;
  owner?: boolean;
}

const MANAGE_GUILD = BigInt(0x20);
const ADMINISTRATOR = BigInt(0x8);

export function canManageGuild(guild: DiscordGuild): boolean {
  if (guild.owner) return true;
  try {
    const perms = BigInt(guild.permissions);
    return (
      (perms & ADMINISTRATOR) === ADMINISTRATOR ||
      (perms & MANAGE_GUILD) === MANAGE_GUILD
    );
  } catch {
    return false;
  }
}

export async function fetchUserGuilds(
  accessToken: string
): Promise<DiscordGuild[]> {
  const res = await fetch("https://discord.com/api/users/@me/guilds", {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}

export async function userCanManageGuild(
  accessToken: string,
  guildId: string
): Promise<boolean> {
  const guilds = await fetchUserGuilds(accessToken);
  const guild = guilds.find((g) => String(g.id) === String(guildId));
  return guild ? canManageGuild(guild) : false;
}
