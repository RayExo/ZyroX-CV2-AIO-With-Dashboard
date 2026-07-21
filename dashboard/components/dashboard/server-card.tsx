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
import { Users, Hash, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ServerCardProps {
  id: string | number;
  name: string;
  iconUrl?: string | null;
  memberCount: number;
  isActive?: boolean;
  className?: string;
}

export const ServerCard = ({ 
  id, 
  name, 
  iconUrl, 
  memberCount, 
  isActive = true,
  className 
}: ServerCardProps) => {
  return (
    <div className={cn(
      "bg-[#141B2D] border border-slate-800 rounded-[40px] group hover:border-primary/50 transition-all duration-500 overflow-hidden shadow-2xl hover:shadow-primary/10 shadow-black/40 h-full flex flex-col",
      className
    )}>
      <div className="p-8 flex-grow">
        <div className="flex items-start justify-between mb-8">
          <div className="relative">
            {iconUrl ? (
              <Image 
                src={iconUrl} 
                alt={name}
                width={80}
                height={80}
                className="rounded-3xl border-4 border-slate-800 shadow-2xl group-hover:scale-105 transition-transform duration-500"
              />
            ) : (
              <div className="h-20 w-20 bg-primary/20 rounded-3xl flex items-center justify-center border-4 border-slate-800 text-primary font-black text-3xl shadow-2xl group-hover:scale-105 transition-transform duration-500">
                {name.charAt(0)}
              </div>
            )}
            {isActive && (
              <div className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-emerald-500 border-4 border-[#141B2D] shadow-lg animate-pulse" title="Online" />
            )}
          </div>
          
          <div className="flex flex-col items-end text-right">
            <span className="text-[10px] uppercase font-black text-slate-500 tracking-[0.2em] mb-1 opacity-50">ID Reference</span>
            <span className="text-[11px] font-mono font-bold text-slate-400 bg-black/20 px-3 py-1.5 rounded-xl border border-white/5 truncate max-w-[140px]">
              {id}
            </span>
          </div>
        </div>

        <div>
          <h3 className="text-2xl font-black text-white truncate group-hover:text-primary transition-colors tracking-tight">
            {name}
          </h3>
          <div className="flex items-center gap-4 mt-6">
            <div className="flex items-center gap-2 bg-slate-800/50 px-4 py-2 rounded-2xl border border-white/5 shadow-inner">
              <Users className="h-4 w-4 text-primary" />
              <span className="text-xs font-black text-slate-200 tabular-nums">
                {memberCount.toLocaleString()}
              </span>
            </div>
            <div className="flex items-center gap-2 bg-slate-800/50 px-4 py-2 rounded-2xl border border-white/5">
              <Hash className="h-4 w-4 text-slate-500" />
              <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                Managed
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="px-8 py-6 bg-slate-900/40 border-t border-slate-800/50 group-hover:bg-primary/5 transition-all">
        <Link href={`/dashboard/guild/${id}`} className="block">
          <Button className="w-full justify-between group/btn py-7 rounded-2xl border-slate-700 font-black uppercase tracking-tighter text-xs" variant="secondary">
            <span>Access Dashboard</span>
            <ChevronRight className="h-4 w-4 group-hover/btn:translate-x-1 transition-transform" />
          </Button>
        </Link>
      </div>
    </div>
  );
};
