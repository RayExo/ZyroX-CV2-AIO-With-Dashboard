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
import { Volume2, Save, RefreshCcw, ShieldCheck, Info, Power } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";

export default function InvcRolePage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [roles, setRoles] = useState<any[]>([]);
  const [config, setConfig] = useState<any>({ role_id: null, enabled: false });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [configData, rolesData] = await Promise.all([
        api.getInvcRole(params.guildId),
        api.getRoles(params.guildId),
      ]);
      setConfig(configData);
      setRoles(rolesData);
    } catch (error) {
      console.error("Failed to fetch InvcRole data:", error);
      toast.error("Failed to load Voice Role configuration");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [params.guildId]);

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateInvcRole(params.guildId, { 
      role_id: config.role_id,
      enabled: config.enabled
    });
    toast.promise(promise, {
      loading: 'Saving Voice Role configuration...',
      success: 'Voice Role settings saved!',
      error: 'Failed to save Voice Role config',
    });
    try { await promise; } catch {} finally { setSaving(false); }
  };

  const filteredRoles = roles.filter(r => r.name !== "@everyone");

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCcw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const formatColor = (decimal: number) => {
    if (!decimal || decimal === 0) return "#94a3b8";
    return `#${decimal.toString(16).padStart(6, '0')}`;
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Volume2 className="h-6 w-6 text-primary" />
            Voice Role
          </h2>
          <p className="text-slate-400 mt-1">Automatically assign a role when members join a voice channel.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl p-8 space-y-8">
            
            {/* Status & Toggle */}
            <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
              <div className="flex items-center gap-4">
                <div className={cn("p-3 rounded-xl transition-colors", config.enabled ? "bg-emerald-500/20 text-emerald-500" : "bg-red-500/20 text-red-500")}>
                  <Power className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-white">Voice Role System</h3>
                  <p className="text-sm text-slate-400 mt-1">{config.enabled ? "The system is active and monitoring channels." : "The system is currently disabled."}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="px-3 py-1 rounded-full bg-slate-900 border border-slate-800 flex items-center gap-2">
                  <div className={cn("w-2 h-2 rounded-full", config.enabled ? 'bg-emerald-500 animate-pulse' : 'bg-red-500')} />
                  <span className="text-[10px] font-bold uppercase text-slate-400">
                    {config.enabled ? 'Live' : 'Off'}
                  </span>
                </div>
                <Switch 
                  checked={config.enabled} 
                  onCheckedChange={(checked) => setConfig({ ...config, enabled: checked })}
                  className="data-[state=checked]:bg-emerald-500"
                />
              </div>
            </div>

            {/* Role Selector */}
            <div className={cn("p-6 border rounded-2xl space-y-4 transition-all duration-300", 
              config.enabled ? "bg-slate-900/40 border-slate-800 opacity-100" : "bg-slate-900/10 border-slate-900 opacity-50 pointer-events-none grayscale")}>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-primary/20 text-primary rounded-xl">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-white">Voice State Role</h4>
                  <p className="text-xs text-slate-400 mt-1">Choose the role to be assigned automatically to voice participants.</p>
                </div>
              </div>
              <Select
                value={config.role_id || "none"}
                onValueChange={(val) => setConfig({ ...config, role_id: val === "none" ? null : val })}
                disabled={!config.enabled}
              >
                <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                  <SelectValue placeholder="Select a role..." />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                  <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">No Role Selected</SelectItem>
                  {filteredRoles.map((r) => (
                    <SelectItem key={r.id} value={r.id} className="focus:bg-slate-800">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: formatColor(r.color) }} />
                        {r.name}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button onClick={handleSave} disabled={saving} className="w-full h-14 text-base font-bold gap-2 shadow-lg shadow-primary/20 transition-all hover:scale-[1.01] active:scale-[0.99]">
              {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
              Save All Changes
            </Button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <Volume2 className="h-32 w-32 text-primary" />
            </div>
            <div className="flex items-center gap-2 mb-4">
              <Info className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-bold text-white">How It Works</h3>
            </div>
            <ul className="text-xs text-slate-500 space-y-3 leading-relaxed">
              <li className="flex gap-2">
                <span className="text-primary font-bold">01</span>
                <span>Role is added when a user joins any voice channel.</span>
              </li>
              <li className="flex gap-2">
                <span className="text-primary font-bold">02</span>
                <span>Role is removed when they disconnect from all channels.</span>
              </li>
              <li className="flex gap-2">
                <span className="text-primary font-bold">03</span>
                <span>Make sure the bot role is higher than the selected role.</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
