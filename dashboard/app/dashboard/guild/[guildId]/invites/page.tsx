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
import { TrendingUp, RefreshCcw, Medal, User, LogOut, UserMinus, UserPlus, Info } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function InvitesPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any[]>([]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const res = await api.getInvites(params.guildId);
      setData(res.data || []);
    } catch (error) {
      console.error("Failed to fetch invites leaderboard:", error);
      toast.error("Failed to load invites leaderboard");
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLeaderboard(); }, [params.guildId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCcw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="h-6 w-6 text-primary" />
            Invite Leaderboard
          </h2>
          <p className="text-slate-400 mt-1">Top inviters in the server based on tracked join events.</p>
        </div>
        <button onClick={fetchLeaderboard} className="text-slate-400 hover:text-white transition-colors">
          <RefreshCcw className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl p-8 space-y-8">
            
            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-5 bg-primary/5 border border-primary/20 rounded-2xl flex flex-col gap-1">
                <div className="text-xs font-bold uppercase text-primary flex items-center gap-2"><UserPlus className="w-3.5 h-3.5" /> Total</div>
                <span className="text-2xl font-black text-white">{data.reduce((acc, curr) => acc + (curr.total || 0), 0)}</span>
              </div>
              <div className="p-5 bg-red-500/5 border border-red-500/20 rounded-2xl flex flex-col gap-1">
                <div className="text-xs font-bold uppercase text-red-500 flex items-center gap-2"><LogOut className="w-3.5 h-3.5" /> Left</div>
                <span className="text-2xl font-black text-white">{data.reduce((acc, curr) => acc + (curr.left || 0), 0)}</span>
              </div>
              <div className="p-5 bg-yellow-500/5 border border-yellow-500/20 rounded-2xl flex flex-col gap-1">
                <div className="text-xs font-bold uppercase text-yellow-500 flex items-center gap-2"><UserMinus className="w-3.5 h-3.5" /> Fake</div>
                <span className="text-2xl font-black text-white">{data.reduce((acc, curr) => acc + (curr.fake || 0), 0)}</span>
              </div>
              <div className="p-5 bg-emerald-500/5 border border-emerald-500/20 rounded-2xl flex flex-col gap-1">
                <div className="text-xs font-bold uppercase text-emerald-500 flex items-center gap-2"><TrendingUp className="w-3.5 h-3.5" /> Top</div>
                <span className="text-2xl font-black text-white">{data.length > 0 ? data[0].total : 0}</span>
              </div>
            </div>

            {/* Leaderboard */}
            <div className="pt-6 border-t border-slate-800 space-y-3">
              <h4 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
                <Medal className="h-5 w-5 text-yellow-500" /> Rankings
              </h4>

              {data.length === 0 ? (
                <div className="text-center p-12 bg-slate-900/20 rounded-2xl border border-dashed border-slate-700">
                  <TrendingUp className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                  <p className="text-sm text-slate-500">No invite data found yet.</p>
                </div>
              ) : (
                data.map((row, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-slate-900/40 rounded-xl border border-slate-800 hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-sm font-black border border-slate-700">
                        {index === 0 ? "🥇" : index === 1 ? "🥈" : index === 2 ? "🥉" : <span className="text-slate-500">#{index + 1}</span>}
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 border border-slate-700">
                          <User className="w-4 h-4" />
                        </div>
                        <span className="text-sm text-slate-300 font-mono">{row.user_id}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-6 text-sm">
                      <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-slate-500">Total</div>
                        <div className="font-black text-primary">{row.total}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-slate-500">Real</div>
                        <div className="font-medium text-emerald-400">{row.total - row.left - row.fake - row.rejoin}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-slate-500">Left</div>
                        <div className="text-red-400">{row.left}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-slate-500">Fake</div>
                        <div className="text-yellow-400">{row.fake}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-[10px] uppercase font-bold text-slate-500">Rejoin</div>
                        <div className="text-blue-400">{row.rejoin}</div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <TrendingUp className="h-32 w-32 text-primary" />
            </div>
            <div className="flex items-center gap-2 mb-4">
              <Info className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-bold text-white">About Tracking</h3>
            </div>
            <ul className="text-xs text-slate-500 space-y-2">
              <li>• Invite tracking is automatic for all members.</li>
              <li>• &quot;Real&quot; = Total minus Left, Fake, and Rejoins.</li>
              <li>• Use <span className="text-primary">,invitelogging #channel</span> to enable live logs.</li>
              <li>• Admins can manually adjust invite counts.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
