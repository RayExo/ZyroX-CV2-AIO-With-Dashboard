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
import { Ghost } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

const CustomRolesForm = dynamic(() => import("@/components/dashboard/customroles-form").then(mod => mod.CustomRolesForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-slate-800/20 rounded-3xl" />
});

export default async function CustomRolesPage({ params }: { params: { guildId: string } }) {
  const [config, roles] = await Promise.all([
    api.getCustomRoles(params.guildId),
    api.getRoles(params.guildId),
  ]);

  if (!config) return null;

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Ghost className="h-6 w-6 text-primary" />
            Custom Roles
          </h2>
          <p className="text-slate-400 mt-1">Configure predefined roles that can be easily assigned using commands.</p>
        </div>
      </div>

      <CustomRolesForm initialConfig={config} roles={roles} guildId={params.guildId} />
    </div>
  );
}
