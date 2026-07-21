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
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  name: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: string;
    isUp: boolean;
  };
  className?: string;
}

export const MetricCard = ({ 
  name, 
  value, 
  icon: Icon, 
  description,
  trend,
  className 
}: MetricCardProps) => {
  return (
    <div className={cn(
      "bg-[#141B2D] border border-slate-800 p-6 rounded-3xl relative overflow-hidden group hover:border-primary/50 transition-all shadow-xl hover:shadow-primary/5 shadow-black/20",
      className
    )}>
      <div className="flex items-center justify-between relative z-10">
        <div>
          <p className="text-xs font-black uppercase text-slate-500 tracking-widest">{name}</p>
          <div className="flex items-baseline gap-2 mt-1">
            <p className="text-3xl font-black text-white tracking-tighter">{value}</p>
            {trend && (
              <span className={cn(
                "text-[10px] font-black px-1.5 py-0.5 rounded-lg",
                trend.isUp ? "bg-emerald-500/10 text-emerald-500" : "bg-red-500/10 text-red-500"
              )}>
                {trend.isUp ? "+" : ""}{trend.value}
              </span>
            )}
          </div>
          {description && (
             <p className="text-[10px] text-slate-500 mt-2 italic font-medium">{description}</p>
          )}
        </div>
        <div className="p-4 bg-slate-800/50 rounded-2xl group-hover:scale-110 group-hover:bg-primary/10 transition-all border border-white/5">
          <Icon className="h-6 w-6 text-primary" />
        </div>
      </div>
      
      {/* Decorative Gradient Line */}
      <div className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-primary/50 to-transparent w-full opacity-0 group-hover:opacity-100 transition-opacity" />
      
      {/* Glow Effect */}
      <div className="absolute -right-8 -bottom-8 h-24 w-24 bg-primary/5 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
    </div>
  );
};
