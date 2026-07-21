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
  Shield, Users, Server, Activity, Database, Cpu, Globe, Lock, Settings, RefreshCw
} from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { AdminStats, AdminConfig } from "@/types/api";
import { toast } from "sonner";

export function AdminContent() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [config, setConfig] = useState<AdminConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [notification, setNotification] = useState("");

  const fetchData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    try {
      const [statsData, configData] = await Promise.all([
        api.getAdminStats(),
        api.getAdminConfig()
      ]);
      setStats(statsData);
      setConfig(configData);
      setNotification(configData.global_notification || "");
    } catch (err) {
      console.error("Failed to fetch admin data:", err);
      toast.error("Failed to load real-time data");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(true), 30000); // Auto refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const handleToggleMaintenance = async () => {
    if (!config) return;
    setSaving(true);
    try {
      const newStatus = !config.maintenance_mode;
      await api.updateAdminConfig({ maintenance_mode: newStatus });
      setConfig({ ...config, maintenance_mode: newStatus });
      toast.success(`Maintenance mode ${newStatus ? 'enabled' : 'disabled'}`);
    } catch (err) {
      toast.error("Failed to update maintenance mode");
    } finally {
      setSaving(false);
    }
  };

  const handleBroadcast = async () => {
    setSaving(true);
    try {
      await api.updateAdminConfig({ global_notification: notification });
      if (config) setConfig({ ...config, global_notification: notification });
      toast.success("Broadcast message updated");
    } catch (err) {
      toast.error("Failed to update broadcast message");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCw className="h-10 w-10 text-red-500 animate-spin opacity-20" />
      </div>
    );
  }

  const statItems = [
    { name: "Total Users", value: stats?.total_users || "0", icon: Users, color: "text-blue-500" },
    { name: "Active Servers", value: stats?.active_servers || "0", icon: Server, color: "text-emerald-500" },
    { name: "API Latency", value: stats?.api_latency || "0ms", icon: Activity, color: "text-amber-500" },
    { name: "Database Size", value: stats?.db_size || "0 MB", icon: Database, color: "text-purple-500" },
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      {/* Header */}
      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-red-500 to-indigo-500 rounded-3xl blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
        <div className="relative bg-[#0f172a] border border-white/10 rounded-3xl p-8 lg:p-12 flex flex-col lg:flex-row lg:items-center justify-between gap-8">
          <div className="flex items-center gap-6">
            <div className="h-16 w-16 rounded-2xl bg-red-500/20 flex items-center justify-center border border-red-500/30 shadow-2xl shadow-red-500/20">
              <Shield className="h-8 w-8 text-red-500" />
            </div>
            <div>
              <h1 className="text-4xl font-black text-white tracking-tight font-outfit">Admin Control Panel</h1>
              <p className="text-slate-400 mt-2 font-medium">Restricted access for ZyroX administrators only.</p>
            </div>
          </div>
          <button 
            onClick={() => fetchData(true)}
            className="flex items-center gap-3 bg-red-500/5 px-6 py-3 rounded-2xl border border-red-500/10 hover:bg-red-500/10 transition-all active:scale-95 group/refresh"
          >
            <RefreshCw className={cn("h-4 w-4 text-red-500 transition-all", refreshing && "animate-spin")} />
            <span className="text-xs font-black uppercase tracking-widest text-red-500">
              {refreshing ? "Refreshing..." : "Real-time Mode"}
            </span>
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statItems.map((stat) => (
          <div key={stat.name} className="glass border border-white/5 rounded-3xl p-6 hover:border-white/10 transition-all group">
            <div className="flex items-center justify-between mb-4">
              <div className={cn("p-3 rounded-xl bg-white/[0.03] group-hover:scale-110 transition-transform", stat.color)}>
                <stat.icon className="h-6 w-6" />
              </div>
              <span className="text-[10px] font-black uppercase tracking-widest text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded-lg">
                Live
              </span>
            </div>
            <p className="text-slate-500 text-xs font-bold uppercase tracking-widest">{stat.name}</p>
            <h3 className="text-2xl font-black text-white mt-1 font-outfit">{stat.value}</h3>
          </div>
        ))}
      </div>

      {/* System Status Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* API Health */}
        <div className="lg:col-span-2 glass border border-white/5 rounded-[2.5rem] overflow-hidden">
          <div className="p-8 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
            <div className="flex items-center gap-4">
              <Activity className="h-5 w-5 text-red-500" />
              <h3 className="text-lg font-bold text-white">System Nodes Status</h3>
            </div>
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Auto-Polling Active</span>
          </div>
          <div className="p-8 space-y-6">
            {stats?.nodes.map((node) => {
              const Icon = node.icon === "Globe" ? Globe : node.icon === "Database" ? Database : node.icon === "Cpu" ? Cpu : Lock;
              const isHealthy = node.status === "Healthy";
              return (
                <div key={node.name} className="flex items-center justify-between p-4 bg-white/[0.02] rounded-2xl border border-white/5 group hover:bg-white/[0.04] transition-all">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center group-hover:bg-slate-700 transition-colors">
                      <Icon className="h-5 w-5 text-slate-400" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white">{node.name}</h4>
                      <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Load: {node.load}</p>
                    </div>
                  </div>
                  <div className={cn(
                    "flex items-center gap-2 px-3 py-1.5 rounded-full border",
                    isHealthy ? "bg-emerald-500/10 border-emerald-500/20" : "bg-amber-500/10 border-amber-500/20"
                  )}>
                    <div className={cn("h-1.5 w-1.5 rounded-full", isHealthy ? "bg-emerald-500" : "bg-amber-500")} />
                    <span className={cn("text-[10px] font-bold uppercase", isHealthy ? "text-emerald-500" : "text-amber-500")}>
                      {node.status}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Global Config */}
        <div className="glass border border-white/5 rounded-[2.5rem] overflow-hidden flex flex-col">
          <div className="p-8 border-b border-white/5 flex items-center gap-4 bg-white/[0.01]">
            <Settings className="h-5 w-5 text-indigo-500" />
            <h3 className="text-lg font-bold text-white">Global Settings</h3>
          </div>
          <div className="p-8 flex-1 space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 pl-1">Maintenance Mode</label>
              <button 
                onClick={handleToggleMaintenance}
                disabled={saving}
                className={cn(
                  "w-full flex items-center justify-between p-4 rounded-2xl border transition-all",
                  config?.maintenance_mode 
                    ? "bg-red-500/10 border-red-500/30 text-red-500" 
                    : "bg-white/[0.03] border-white/5 text-slate-300 hover:bg-white/[0.05]"
                )}
              >
                <span className="text-sm font-medium">
                  {config?.maintenance_mode ? "Restricting Access" : "Standard Operations"}
                </span>
                <div className={cn(
                  "h-6 w-11 rounded-full relative transition-colors duration-300",
                  config?.maintenance_mode ? "bg-red-500" : "bg-slate-700"
                )}>
                  <div className={cn(
                    "absolute top-1 h-4 w-4 bg-white rounded-full transition-all duration-300 shadow-sm",
                    config?.maintenance_mode ? "left-6" : "left-1"
                  )} />
                </div>
              </button>
            </div>
            
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 pl-1">Global Notification</label>
              <textarea 
                value={notification}
                onChange={(e) => setNotification(e.target.value)}
                className="w-full h-32 bg-white/[0.03] border border-white/5 rounded-2xl p-4 text-xs font-medium text-slate-300 focus:outline-none focus:ring-1 focus:ring-red-500/30 transition-all placeholder:text-slate-600"
                placeholder="Message to display across all dashboards..."
              />
            </div>

            <button 
              onClick={handleBroadcast}
              disabled={saving}
              className="w-full py-4 bg-primary rounded-2xl font-black uppercase tracking-widest text-xs shadow-xl shadow-primary/20 hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {saving ? "Processing..." : "Broadcast Message"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
