/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
 * ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
 * ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
 * ║                                                                  ║
 * ║           © 2026 CodeX Devs — All Rights Reserved               ║
 * ║                                                                  ║
 * ║   discord  ──  https://discord.gg/codexdev                      ║
 * ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
 * ║   github   ──  https://github.com/RayExo                        ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { Users, ShieldCheck, ChevronRight, Hash } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

import { GuildSummary } from "@/types/api";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function GuildsPage() {
  const session = await getServerSession(authOptions);
  
  if (!session || !session.accessToken) {
    redirect("/");
  }

  let botGuilds: GuildSummary[] = [];
  let userGuilds: any[] = [];
  let userDiscordError: string | null = null;
  let botError: string | null = null;

  try {
    botGuilds = await api.listGuilds();
  } catch (err: any) {
    console.error("Failed to fetch bot guilds:", err);
    botError = err.message || "Failed to load bot servers.";
  }

  try {
    const res = await fetch("https://discord.com/api/users/@me/guilds", {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
      next: { revalidate: 300 } // Cache for 5 mins
    });
    
    if (res.ok) {
      userGuilds = await res.json();
    } else {
      userDiscordError = "Failed to fetch your Discord servers.";
    }
  } catch (err) {
    console.error("Discord API Error:", err);
    userDiscordError = "Error connecting to Discord.";
  }

  // Filter out guilds that the user is an admin of (permission flag 0x8 or MANAGE_GUILD 0x20)
  // Manage Server is 0x20, Admin is 0x8
  const MANAGE_GUILD = BigInt(0x20);
  const ADMINISTRATOR = BigInt(0x8);
  const adminUserGuilds = userGuilds.filter(g => {
    try {
      const perms = BigInt(g.permissions);
      return (perms & ADMINISTRATOR) === ADMINISTRATOR || 
             (perms & MANAGE_GUILD) === MANAGE_GUILD || 
             g.owner === true;
    } catch {
      return g.owner === true;
    }
  });

  const adminGuildIds = new Set(adminUserGuilds.map(g => String(g.id)));
  
  // The intersecting guilds we can manage
  const guilds = botGuilds.filter(g => adminGuildIds.has(String(g.id)));
  const error = botError || userDiscordError;


  return (
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white">Your Servers</h1>
          <p className="text-slate-400 mt-2">
            Select a server to manage its unique configuration and modules.
          </p>
        </div>
        <div className="text-sm font-medium px-4 py-2 bg-slate-800 rounded-xl border border-slate-700 text-slate-300">
          Showing <span className="text-white">{guilds.length}</span> active guilds
        </div>
      </div>

      {error ? (
        <div className="bg-red-500/10 border border-red-500/20 p-8 rounded-2xl text-center">
          <ShieldCheck className="h-12 w-12 text-red-500 mx-auto mb-4 opacity-50" />
          <h3 className="text-white font-bold text-lg">Connection Error</h3>
          <p className="text-slate-400 mt-2">{error}</p>
          <Button variant="outline" className="mt-6">Retry Connection</Button>
        </div>
      ) : guilds.length === 0 ? (
        <div className="bg-slate-800/30 border border-slate-800 border-dashed p-16 rounded-3xl text-center">
          <div className="h-16 w-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6">
            <Users className="h-8 w-8 text-slate-600" />
          </div>
          <h3 className="text-white font-bold text-xl">No Servers Found</h3>
          <p className="text-slate-400 mt-2 max-w-sm mx-auto">
            The bot hasn&apos;t joined any servers yet, or you don&apos;t have permission.
          </p>
          <div className="mt-8 bg-slate-900/50 p-4 rounded-xl text-left font-mono text-sm text-slate-300 max-w-2xl mx-auto overflow-auto max-h-48 whitespace-pre">
            <p className="font-bold text-red-400 mb-2">Diagnostic Data:</p>
            <p>1. Bot&apos;s Cache Total Servers: {botGuilds.length}</p>
            <p>2. Your Discord Profile Total Servers: {userGuilds.length}</p>
            <p>3. Your Discord Profile Admin/Manage Servers: {adminUserGuilds.length}</p>
            {botGuilds.length > 0 && adminUserGuilds.length > 0 && (
               <div className="mt-4 pt-4 border-t border-white/10">
                 <p className="text-emerald-400 mb-1">Bot First Server ID: {botGuilds[0].id} (Type: {typeof botGuilds[0].id})</p>
                 <p className="text-blue-400">Your First Admin Server ID: {adminUserGuilds[0].id} (Type: {typeof adminUserGuilds[0].id})</p>
               </div>
            )}
            <hr className="my-2 border-white/10" />
            <p>Intersection Mappings found: {guilds.length}</p>
            {userDiscordError && <p className="text-red-400">User Error: {userDiscordError}</p>}
            {botError && <p className="text-red-400">Bot Error: {botError}</p>}
          </div>
          <Button className="mt-8">Invite to Discord</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {guilds.map((guild) => (
            <div 
              key={guild.id} 
              className="bg-[#141B2D] border border-slate-800 rounded-3xl group hover:border-primary/50 hover:bg-[#202c3f] transition-all duration-300 overflow-hidden shadow-sm hover:shadow-primary/5 shadow-black/20"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="relative">
                    {guild.icon_url ? (
                      <Image 
                        src={guild.icon_url} 
                        alt={guild.name}
                        width={64}
                        height={64}
                        className="rounded-2xl border-2 border-slate-800 shadow-xl group-hover:scale-105 transition-transform"
                      />
                    ) : (
                      <div className="h-16 w-16 bg-primary/20 rounded-2xl flex items-center justify-center border-2 border-slate-800 text-primary font-bold text-2xl shadow-xl group-hover:scale-105 transition-transform">
                        {guild.name.charAt(0)}
                      </div>
                    )}
                    <div className="absolute -bottom-1 -right-1 h-4 w-4 rounded-full bg-emerald-500 border-2 border-[#141B2D]" title="Bot Online" />
                  </div>
                  
                  <div className="flex flex-col items-end text-right">
                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mb-1">Guild ID</span>
                    <span className="text-xs font-mono text-slate-400 bg-black/20 px-2 py-1 rounded-lg border border-white/5 truncate max-w-[120px]">
                      {guild.id}
                    </span>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold text-white truncate group-hover:text-primary transition-colors">
                    {guild.name}
                  </h3>
                  <div className="flex items-center gap-4 mt-4 text-slate-400">
                    <div className="flex items-center gap-1.5 bg-slate-800/50 px-3 py-1.5 rounded-xl border border-white/5">
                      <Users className="h-4 w-4 text-slate-500" />
                      <span className="text-sm font-semibold text-slate-300">{guild.member_count.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1.5 bg-slate-800/50 px-3 py-1.5 rounded-xl border border-white/5">
                      <Hash className="h-4 w-4 text-slate-500" />
                      <span className="text-sm font-semibold text-slate-300">Active</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="px-6 py-4 bg-slate-800/20 border-t border-slate-800/80 group-hover:bg-primary/5 transition-colors">
                <Button className="w-full justify-between group/btn py-6" variant="secondary" asChild>
                  <Link href={`/dashboard/guild/${guild.id}`}>
                    <span>Manage Server</span>
                    <ChevronRight className="h-4 w-4 group-hover/btn:translate-x-1 transition-transform" />
                  </Link>
                </Button>
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
}
