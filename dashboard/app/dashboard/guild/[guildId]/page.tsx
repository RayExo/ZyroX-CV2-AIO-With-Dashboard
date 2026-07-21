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
  Plus, 
  Settings2, 
  Terminal, 
  Database,
  Search,
  Zap,
  ShieldCheck,
  Ticket,
  BarChart4,
  FileText,
  Activity
} from "lucide-react";

export default function GuildOverviewPage({ params }: { params: { guildId: string } }) {
  const modules = [
    { title: "Auto Moderation", desc: "Anti-spam, bad words, and links protection.", icon: ShieldCheck, status: "Active" },
    { title: "Ticket System", desc: "Helpdesk for user support and inquiries.", icon: Ticket, status: "Configured" },
    { title: "Leveling", desc: "Gamify your community with XP and ranks.", icon: BarChart4, status: "Active" },
    { title: "Event Logging", desc: "Detailed audit logs for every server event.", icon: FileText, status: "Active" },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Quick Config Column */}
      <div className="space-y-8">
        <section>
          <div className="flex items-center gap-2 mb-6">
            <h2 className="text-xl font-bold text-white tracking-tight">Active Modules</h2>
            <div className="h-[2px] flex-1 bg-slate-800" />
            <Plus className="h-4 w-4 text-slate-600 cursor-pointer hover:text-white transition-colors" />
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {modules.map((mod) => (
              <div key={mod.title} className="bg-[#141B2D] border border-slate-800 p-5 rounded-2xl group hover:border-slate-600 transition-all shadow-sm">
                <div className="flex items-start justify-between mb-4">
                  <div className="h-10 w-10 bg-slate-800 rounded-xl flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                    <mod.icon className="h-5 w-5" />
                  </div>
                  <span className="text-[10px] font-black uppercase text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    {mod.status}
                  </span>
                </div>
                <h3 className="font-bold text-white mb-1">{mod.title}</h3>
                <p className="text-xs text-slate-500 leading-relaxed">{mod.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-6">
            <h2 className="text-xl font-bold text-white tracking-tight">System Console</h2>
            <div className="h-[2px] flex-1 bg-slate-800" />
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 font-mono text-xs overflow-hidden shadow-2xl">
            <div className="flex items-center gap-2 mb-3 border-b border-slate-800 pb-2">
              <Terminal className="h-4 w-4 text-primary" />
              <span className="text-slate-400">guild_event_stream_{params.guildId}</span>
            </div>
            <div className="space-y-1.5 opacity-80">
              <p className="text-slate-500">[{new Date().toLocaleTimeString()}] <span className="text-emerald-500">INIT</span> Dashboard connected to WebSocket pool...</p>
              <p className="text-slate-500">[{new Date().toLocaleTimeString()}] <span className="text-primary">INFO</span> Fetching guild_config from primary database...</p>
              <p className="text-slate-500">[{new Date().toLocaleTimeString()}] <span className="text-emerald-500">DONE</span> Cache synchronized successfully.</p>
              <p className="text-slate-400 animate-pulse">_</p>
            </div>
          </div>
        </section>
      </div>

      {/* Integration Status Column */}
      <div className="space-y-8">
        <section className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-8 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-125 transition-transform">
            <Database className="h-48 w-48 text-white" />
          </div>
          <h2 className="text-2xl font-black text-white mb-2 italic tracking-tighter">Database Status</h2>
          <p className="text-slate-400 text-sm mb-8 max-w-[280px]">All guild data is encrypted and replicated across our high-performance edge network.</p>
          
          <div className="space-y-4 relative z-10">
            {[
              { label: 'Uptime', value: '99.98%', icon: Zap },
              { label: 'Sync Delay', value: '12ms', icon: Activity },
              { label: 'Region', value: 'Global Edges', icon: GlobalizationIcon }
            ].map((stat) => (stat.icon && 
              <div key={stat.label} className="flex items-center justify-between p-4 bg-black/20 backdrop-blur-md rounded-2xl border border-white/5">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 bg-black/40 rounded-lg flex items-center justify-center text-primary">
                    <stat.icon className="h-4 w-4" />
                  </div>
                  <span className="text-sm font-medium text-slate-300">{stat.label}</span>
                </div>
                <span className="text-sm font-bold text-white tracking-widest">{stat.value}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-[#141B2D] border border-slate-800 rounded-3xl p-8">
           <h2 className="text-xl font-bold text-white mb-6">Security Context</h2>
           <div className="flex items-center gap-6">
              <div className="h-20 w-20 rounded-full border-4 border-emerald-500/20 flex items-center justify-center relative shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                <div className="h-16 w-16 rounded-full border-4 border-emerald-500 flex items-center justify-center text-emerald-500 font-black text-xl italic">
                  100%
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Trust Factor</h3>
                <p className="text-slate-400 text-sm">Bot is fully authenticated with administrator privileges.</p>
              </div>
           </div>
        </section>
      </div>
    </div>
  );
}

function GlobalizationIcon({ className }: { className?: string }) {
  return (
    <svg 
      className={className} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  );
}
