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
import { UserPlus } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

export const revalidate = 0; // Never cache this page


const AutoRoleForm = dynamic(() => import("@/components/dashboard/autorole-form").then(mod => mod.AutoRoleForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-slate-800/20 rounded-3xl" />
});

export default async function AutoRolePage({ params }: { params: { guildId: string } }) {
  const [config, roles] = await Promise.all([
    api.getAutoRole(params.guildId),
    api.getRoles(params.guildId)
  ]);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <UserPlus className="h-6 w-6 text-primary" />
            Auto Role
          </h2>
          <p className="text-slate-400 mt-1">Automatically assign roles to new members and bots.</p>
        </div>
      </div>

      <AutoRoleForm 
        initialConfig={config} 
        roles={roles} 
        guildId={params.guildId} 
      />
    </div>
  );
}
