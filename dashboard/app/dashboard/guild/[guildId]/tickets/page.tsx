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
import { Ticket, ExternalLink } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

const TicketsForm = dynamic(() => import("@/components/dashboard/tickets-form").then(mod => mod.TicketsForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-slate-800/20 rounded-3xl" />
});

export default async function TicketsPage({ params }: { params: { guildId: string } }) {
  const config = await api.getTickets(params.guildId);

  if (!config) return null;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500 pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Ticket className="h-6 w-6 text-primary" />
            Ticket System
          </h2>
          <p className="text-slate-400 mt-1">Manage private support channels and inquiry categories.</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-2xl flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold text-emerald-500 uppercase">Live System</span>
          </div>
          {/* <Button variant="outline" className="gap-2">
            <ExternalLink className="h-4 w-4" />
            Preview Panel
          </Button> */}
        </div>
      </div>

      <TicketsForm initialConfig={config} guildId={params.guildId} />
    </div>
  );
}
