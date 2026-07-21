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

"use client";

import React, { useState, useEffect } from "react";
import { 
  Trophy, 
  User, 
  Zap, 
  RefreshCcw, 
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Medal,
  Crown,
  Search
} from "lucide-react";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { LeaderboardEntry } from "@/types/api";

export default function LeaderboardPage({ params }: { params: { guildId: string } }) {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function fetchLeaderboard() {
      try {
        const data = await api.getLeaderboard(params.guildId);
        setLeaderboard(data);
      } catch (err) {
        console.error("Failed to fetch leaderboard:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchLeaderboard();
  }, [params.guildId]);

  const filteredData = leaderboard.filter(entry => 
    entry.name.toLowerCase().includes(search.toLowerCase()) || 
    entry.user_id.toString().includes(search)
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <RefreshCcw className="h-10 w-10 text-primary animate-spin" />
        <p className="text-slate-400 animate-pulse font-medium tracking-tight">Syncing global rankings...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500 pb-20">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h2 className="text-3xl font-black text-white flex items-center gap-3 tracking-tight">
            <Trophy className="h-8 w-8 text-amber-500 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]" />
            Social Leaderboard
          </h2>
          <p className="text-slate-400 mt-1 font-medium italic">Top contributors by experience and activity.</p>
        </div>
        
        <div className="relative w-full md:w-80 group">
           <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 group-focus-within:text-primary transition-colors" />
           <Input 
              placeholder="Search members..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-12 bg-slate-900/50 border-slate-800 rounded-2xl h-12 focus:ring-primary/20 transition-all"
           />
        </div>
      </div>

      {/* Top 3 Podium */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
         {leaderboard.slice(0, 3).map((user, i) => (
            <div key={user.user_id} className={cn(
               "relative p-8 rounded-[40px] border flex flex-col items-center text-center overflow-hidden transition-all hover:scale-[1.02]",
               i === 0 ? "bg-gradient-to-b from-amber-500/20 to-transparent border-amber-500/30 md:-translate-y-4 order-1 md:order-2" : 
               i === 1 ? "bg-gradient-to-b from-slate-300/10 to-transparent border-slate-500/20 order-2 md:order-1" : 
               "bg-gradient-to-b from-amber-800/20 to-transparent border-amber-900/20 order-3"
            )}>
               <div className="absolute top-0 right-0 p-4">
                   {i === 0 ? <Crown className="h-8 w-8 text-amber-500 fill-amber-500/20" /> : 
                    i === 1 ? <Medal className="h-8 w-8 text-slate-300 fill-slate-300/20" /> : 
                    <Medal className="h-8 w-8 text-amber-800 fill-amber-800/10" />}
               </div>
               
               <div className="h-20 w-20 rounded-full bg-slate-800 border-4 border-slate-700 mb-4 flex items-center justify-center relative shadow-2xl">
                  <User className="h-10 w-10 text-slate-500" />
                  <div className={cn(
                    "absolute -bottom-1 -right-1 h-8 w-8 rounded-full border-4 border-[#141B2D] flex items-center justify-center text-[10px] font-black",
                    i === 0 ? "bg-amber-500 text-black" : i === 1 ? "bg-slate-300 text-black" : "bg-amber-800 text-white"
                  )}>
                    #{i + 1}
                  </div>
               </div>
               
               <h3 className="text-xl font-black text-white truncate max-w-full">{user.name}</h3>
               <p className="text-sm font-bold text-slate-500 flex items-center gap-1 mt-1">
                 LEVEL {user.level}
               </p>
               
               <div className="mt-6 flex items-center gap-2 px-4 py-2 bg-black/20 rounded-2xl border border-white/5">
                  <Zap className="h-3 w-3 text-primary" />
                  <span className="text-sm font-black text-slate-200">{user.xp.toLocaleString()} XP</span>
               </div>
            </div>
         ))}
      </div>

      {/* Main Leaderboard Table */}
      <div className="bg-[#141B2D] border border-slate-800 rounded-[40px] overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/30">
                <th className="px-8 py-6 text-[10px] font-black uppercase text-slate-500 tracking-[0.2em]">Rank</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase text-slate-500 tracking-[0.2em]">User</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase text-slate-500 tracking-[0.2em]">Level</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase text-slate-500 tracking-[0.2em] text-right">Total XP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filteredData.slice(3).map((entry, i) => (
                <tr key={entry.user_id} className="group hover:bg-white/[0.02] transition-colors">
                  <td className="px-8 py-6">
                    <span className="text-sm font-black text-slate-500 group-hover:text-white transition-colors">
                       #{i + 4}
                    </span>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex items-center gap-4">
                       <div className="h-10 w-10 rounded-xl bg-slate-800/50 border border-slate-700/50 flex items-center justify-center">
                          <User className="h-5 w-5 text-slate-600" />
                       </div>
                       <div className="flex flex-col">
                          <span className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors">{entry.name}</span>
                          <span className="text-[10px] text-slate-600 font-mono tracking-tighter">{entry.user_id}</span>
                       </div>
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex items-center gap-2">
                       <div className="px-3 py-1 bg-primary/10 rounded-lg border border-primary/20">
                          <span className="text-xs font-black text-primary italic">LVL {entry.level}</span>
                       </div>
                    </div>
                  </td>
                  <td className="px-8 py-6 text-right">
                    <div className="flex items-center justify-end gap-2">
                       <TrendingUp className="h-3 w-3 text-emerald-500 opacity-50" />
                       <span className="text-sm font-black text-slate-200 tabular-nums">{entry.xp.toLocaleString()}</span>
                    </div>
                  </td>
                </tr>
              ))}
              
              {filteredData.length === 3 && (
                <tr>
                   <td colSpan={4} className="px-8 py-20 text-center">
                      <p className="text-slate-500 italic font-medium">No additional members ranked yet...</p>
                   </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Overlay (Simulation) */}
        <div className="p-6 border-t border-slate-800 bg-slate-900/20 flex items-center justify-between">
           <p className="text-xs text-slate-500 font-medium">
             Showing <span className="text-white">{filteredData.length}</span> active competitors
           </p>
           <div className="flex items-center gap-2">
              <Button size="icon" variant="outline" className="h-8 w-8 rounded-lg border-slate-800" disabled>
                 <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button size="icon" variant="outline" className="h-8 w-8 rounded-lg border-slate-800" disabled>
                 <ChevronRight className="h-4 w-4" />
              </Button>
           </div>
        </div>
      </div>
    </div>
  );
}
