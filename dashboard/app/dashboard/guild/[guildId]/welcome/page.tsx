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
import { SmilePlus } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

const WelcomeForm = dynamic(() => import("@/components/dashboard/welcome-form").then(mod => mod.WelcomeForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-slate-800/20 rounded-3xl" />
});

export default async function WelcomePage({ params }: { params: { guildId: string } }) {
  const [welcomeData, channelsData] = await Promise.all([
    api.getWelcome(params.guildId),
    api.getChannels(params.guildId)
  ]);

  if (!welcomeData) return null;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <SmilePlus className="h-6 w-6 text-primary" />
            Welcomer
          </h2>
          <p className="text-slate-400 mt-1">Greet new members to your server.</p>
        </div>
      </div>

      <WelcomeForm initialConfig={welcomeData} channels={channelsData} guildId={params.guildId} />
    </div>
  );
}
