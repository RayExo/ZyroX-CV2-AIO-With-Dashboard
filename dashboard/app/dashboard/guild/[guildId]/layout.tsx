import React from "react";
import Image from "next/image";
import Link from "next/link";
import { 
  Users, 
  ShieldCheck, 
  Ticket, 
  BarChart4, 
  FileText, 
  Settings,
  Hash,
  Shield,
  Layers,
  ArrowLeft,
  ShieldAlert
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export const revalidate = 0; // Never cache any guild dashboard page

import { Button } from "@/components/ui/button";
import { GuildTabs } from "@/components/guild-tabs";

interface GuildLayoutProps {
  children: React.ReactNode;
  params: { guildId: string };
}

export default async function GuildLayout({
  children,
  params,
}: GuildLayoutProps) {
  const guildId = params.guildId;
  let guild;
  let error = null;

  try {
    guild = await api.getGuildDetails(guildId);
  } catch (err: any) {
    console.error("Failed to fetch guild details:", err);
    error = err.message || "Failed to load guild data.";
  }

  if (error || !guild) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] border-2 border-dashed border-red-500/20 rounded-3xl bg-red-500/5 p-12 text-center">
        <ShieldAlert className="h-16 w-16 text-red-500 mb-6 opacity-50" />
        <h2 className="text-2xl font-bold text-white">Access Denied</h2>
        <p className="text-slate-400 mt-2 max-w-md">{error || "This guild does not exist or you do not have permission to manage it."}</p>
        <Link href="/dashboard/guilds" className="mt-8">
          <Button variant="outline">Back to Servers</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Breadcrumb / Back button */}
      <Link href="/dashboard/guilds" className="inline-flex items-center gap-2 text-slate-500 hover:text-white transition-colors text-sm font-medium group">
        <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
        Back to all servers
      </Link>

      {/* Guild Header */}
      <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-8 shadow-xl shadow-black/20">
        <div className="flex flex-col lg:flex-row lg:items-center gap-8">
          <div className="relative">
            {guild.icon ? (
              <Image 
                src={guild.icon} 
                alt={guild.name}
                width={120}
                height={120}
                className="rounded-3xl border-4 border-slate-800 shadow-2xl"
              />
            ) : (
              <div className="h-[120px] w-[120px] bg-primary rounded-3xl flex items-center justify-center text-4xl font-bold text-white shadow-2xl border-4 border-slate-800">
                {guild.name.charAt(0)}
              </div>
            )}
            <div className="absolute -bottom-2 -right-2 bg-emerald-500 text-white p-2 rounded-xl shadow-lg border-2 border-[#141B2D]" title="Active">
              <div className="h-3 w-3 rounded-full bg-white animate-pulse" />
            </div>
          </div>

          <div className="flex-1 space-y-4">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-4xl font-black text-white tracking-tight">{guild.name}</h1>
                <span className="px-3 py-1 bg-slate-800 rounded-lg text-[10px] uppercase font-black text-slate-500 tracking-tighter border border-white/5">
                  ID: {guildId}
                </span>
              </div>
              <p className="text-slate-400 mt-1 italic opacity-80">Server Owner Dashboard</p>
            </div>

            <div className="flex flex-wrap gap-4">
              {[
                { label: "Members", value: guild.member_count, icon: Users, color: "text-blue-400" },
                { label: "Roles", value: guild.role_count, icon: Shield, color: "text-emerald-400" },
                { label: "Channels", value: guild.channel_count, icon: Hash, color: "text-purple-400" },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-3 bg-slate-800/50 px-5 py-3 rounded-2xl border border-white/5 shadow-inner">
                  <div className={cn("p-2 rounded-lg bg-slate-900/50", item.color)}>
                    <item.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider leading-none mb-1">{item.label}</p>
                    <p className="text-xl font-bold text-white leading-none">{item.value.toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row lg:flex-col gap-3">
            <Link href={`/dashboard/guild/${guildId}`} className="w-full">
             <Button className="w-full">
               Refresh 
             </Button>
            </Link>
             <Link href={`/dashboard/guild/${guildId}/settings`} className="w-full">
              <Button variant="secondary" className="w-full">
                Server Settings
              </Button>
             </Link>
          </div>
        </div>
      </div>

      {/* Modern Tab Navigation */}
      <GuildTabs guildId={guildId} />

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {children}
      </div>
    </div>
  );
}
