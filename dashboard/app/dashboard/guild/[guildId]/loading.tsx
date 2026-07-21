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

export default function GuildLoading() {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="h-8 w-64 bg-slate-800 rounded-lg animate-pulse" />
          <div className="h-4 w-96 bg-slate-800/50 rounded-lg animate-pulse" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-4">
           {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 w-full bg-[#141B2D] border border-slate-800 rounded-[40px] animate-pulse" />
           ))}
        </div>
        <div className="space-y-6">
           <div className="h-64 w-full bg-[#141B2D] border border-slate-800 rounded-[40px] animate-pulse" />
           <div className="h-48 w-full bg-[#141B2D] border border-slate-800 rounded-[40px] animate-pulse" />
        </div>
      </div>
    </div>
  );
}
