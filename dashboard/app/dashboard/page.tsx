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
import { 
  Users, 
  MessageSquare, 
  Zap, 
  Activity,
  Server as ServerIcon,
  ShieldAlert,
  Settings,
  LifeBuoy,
  FileText
} from "lucide-react";
import { api } from "@/lib/api";

export default async function DashboardPage() {
  let botInfo;
  let error = null;

  try {
    botInfo = await api.getBotInfo();
  } catch (err: any) {
    console.error("Failed to fetch bot info:", err);
    error = err.message || "Failed to connect to the bot API.";
    // Fallback data for UI structure if API fails
    botInfo = {
      name: "ZyroX Bot",
      guilds: 0,
      users: 0,
      commands: 0,
      latency: "0ms"
    };
  }

  const stats = [
    { name: "Total Guilds", value: botInfo.guilds.toLocaleString(), icon: ServerIcon },
    { name: "Total Users", value: botInfo.users.toLocaleString(), icon: Users },
    { name: "System Uptime", value: "99.9%", icon: Activity },
    { name: "API Latency", value: botInfo.latency, icon: Activity },
  ];

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-white font-outfit tracking-tight">System <span className="text-red-500 italic">Core.</span></h1>
          <p className="text-slate-400 mt-3 font-medium flex items-center gap-2">
            Status and live metrics for <span className="text-red-500 font-bold px-2 py-0.5 rounded-lg bg-red-500/10 border border-red-500/20">{botInfo.name}</span>
          </p>
        </div>
        
        {error && (
          <div className="flex items-center gap-2 px-5 py-2.5 glass-red rounded-2xl text-red-500 text-xs font-bold uppercase tracking-widest animate-pulse">
            <ShieldAlert className="h-4 w-4" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.name} className="group glass border-white/5 p-7 rounded-[32px] relative overflow-hidden hover:border-red-500/30 transition-all duration-500 shadow-2xl">
              {/* Animated Glow Overlay */}
              <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              
             <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-2">{stat.name}</p>
                  <p className="text-3xl font-bold text-white font-outfit tracking-tight">{stat.value}</p>
                </div>
                <div className="p-4 bg-red-500/10 rounded-2xl border border-red-500/20 group-hover:scale-110 group-hover:bg-red-500/20 transition-all duration-500">
                  <stat.icon className="h-6 w-6 text-red-500" />
                </div>
             </div>
             
             <div className="absolute bottom-0 left-12 right-12 h-[1px] bg-red-500/50 blur-[1px] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          </div>
        ))}
      </div>

      {/* Featured Modules & Support */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass border-white/5 rounded-[40px] p-10 relative group overflow-hidden shadow-2xl">
          <div className="absolute inset-0 bg-gradient-to-br from-red-500/[0.03] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
          
          <div className="flex items-center justify-between mb-8 relative z-10">
            <h2 className="text-2xl font-bold text-white font-outfit tracking-tight">Quick Actions</h2>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20">
               <Zap className="h-3 w-3 text-red-500" />
               <span className="text-[10px] font-black text-red-500 uppercase tracking-widest">Efficiency</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-10">
            {[
              { title: "Manage Servers", desc: "View and configure your Discord guilds.", icon: ServerIcon, href: "/dashboard/guilds" },
              { title: "Global Settings", desc: "Adjust your personal dashboard preferences.", icon: Settings, href: "/dashboard" },
              { title: "Support Matrix", desc: "Get help from our neural support team.", icon: LifeBuoy, href: "#" },
              { title: "Documentation", desc: "Learn how to master the ZyroX engine.", icon: FileText, href: "#" },
            ].map((item) => (
              <a key={item.title} href={item.href} className="flex items-center gap-5 p-4 rounded-2xl bg-white/[0.02] border border-white/[0.03] group/item hover:bg-white/[0.05] hover:border-red-500/20 transition-all">
                <div className="h-12 w-12 rounded-2xl bg-red-500/5 border border-red-500/10 flex items-center justify-center group-hover/item:bg-red-500/10 transition-colors">
                   <item.icon className="h-5 w-5 text-red-500/60 group-hover/item:text-red-500 transition-colors" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover/item:text-red-500 transition-colors">{item.title}</h4>
                  <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">{item.desc}</p>
                </div>
              </a>
            ))}
          </div>
        </div>

        <div className="glass border-white/5 rounded-[40px] p-10 flex flex-col justify-between relative group shadow-2xl overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-bl from-red-500/[0.05] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
          
          <div className="relative z-10">
            <h2 className="text-2xl font-bold text-white mb-3 font-outfit">Module Status</h2>
            <p className="text-slate-500 text-sm mb-10 font-medium">Global operational health of ZyroX core.</p>
            
            <div className="space-y-4">
              {[
                { name: 'Neural Gateway', status: 'Optimal' },
                { name: 'Database Cluster', status: 'Synchronized' },
                { name: 'Edge Shards', status: 'Operational' }
              ].map((service) => (
                <div key={service.name} className="flex items-center justify-between p-4 bg-white/[0.02] rounded-2xl border border-white/[0.05] hover:border-red-500/20 transition-colors">
                  <span className="text-xs font-bold text-slate-300">{service.name}</span>
                  <div className="flex items-center gap-3">
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                    <span className="text-[9px] uppercase font-black text-emerald-500 tracking-widest">{service.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <button className="mt-12 w-full py-4 glass-red hover:bg-red-500/10 text-red-500 rounded-[20px] text-[11px] font-black uppercase tracking-[0.2em] transition-all border border-red-500/20 relative z-10">
            System Diagnostics
          </button>
          {/* Abstract Design Element */}
          <div className="absolute -bottom-10 -right-10 h-32 w-32 bg-red-500/10 blur-3xl rounded-full" />
        </div>
      </div>
    </div>
  );
}
