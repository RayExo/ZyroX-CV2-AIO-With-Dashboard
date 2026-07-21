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
import { ShieldAlert } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

const AntiNukeForm = dynamic(() => import("@/components/dashboard/antinuke-form").then(mod => mod.AntiNukeForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-slate-800/20 rounded-3xl" />
});

export default async function AntiNukePage({ params }: { params: { guildId: string } }) {
  const config = await api.getAntiNuke(params.guildId);

  if (!config) return null;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="h-6 w-6 text-red-500" />
            Anti-Nuke Protection
          </h2>
          <p className="text-slate-400 mt-1">Protect your server from malicious mass-deletion, mass-banning, and other destructive actions.</p>
        </div>
      </div>

      <AntiNukeForm initialConfig={config} guildId={params.guildId} />
    </div>
  );
}
