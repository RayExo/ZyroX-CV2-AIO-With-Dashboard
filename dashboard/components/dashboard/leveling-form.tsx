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

import React, { useState } from "react";
import { 
  Save, 
  RefreshCcw, 
  Zap,
  Clock,
  Hash,
  Palette,
  Layout,
  Info
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { LevelingConfig } from "@/types/api";

interface LevelingFormProps {
  initialConfig: LevelingConfig;
  guildId: string;
}

export function LevelingForm({ initialConfig, guildId }: LevelingFormProps) {
  const [config, setConfig] = useState<LevelingConfig>(initialConfig);
  const [saving, setSaving] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    const promise = api.updateLeveling(guildId, {
      enabled: config.enabled,
      xp_per_message: config.xp_per_message,
      cooldown: config.cooldown,
      level_up_channel: config.level_up_channel,
      embed_color: config.embed_style.color
    });

    toast.promise(promise, {
      loading: 'Saving leveling settings...',
      success: 'Leveling settings updated successfully!',
      error: 'Failed to update leveling settings',
    });

    try {
      await promise;
    } catch (err: any) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-20">
      <div className="lg:col-span-2 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl shadow-black/20">
          <div className="p-8 space-y-8">
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-4">
               <span className="text-sm font-bold text-slate-300">Social Economy Status</span>
               <Switch 
                  checked={config.enabled} 
                  onCheckedChange={() => setConfig({...config, enabled: !config.enabled})}
               />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
                  <Zap className="h-3 w-3" />
                  XP Weight
                </label>
                <Input 
                  type="number"
                  value={config.xp_per_message}
                  onChange={(e) => setConfig({...config, xp_per_message: parseInt(e.target.value) || 0})}
                  placeholder="20"
                  disabled={!config.enabled}
                  className="py-6 text-lg font-bold"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
                  <Clock className="h-3 w-3" />
                  Cooldown
                </label>
                <div className="relative">
                  <Input 
                    type="number"
                    value={config.cooldown}
                    onChange={(e) => setConfig({...config, cooldown: parseInt(e.target.value) || 0})}
                    placeholder="60"
                    disabled={!config.enabled}
                    className="py-6 text-lg font-bold pr-12"
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-700">SEC</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
                <Hash className="h-3 w-3" />
                Level Up Channel
              </label>
              <Input 
                value={config.level_up_channel || ""}
                onChange={(e) => setConfig({...config, level_up_channel: e.target.value ? parseInt(e.target.value.replace(/\D/g, "")) : null})}
                placeholder="Discord Channel ID"
                disabled={!config.enabled}
                className="py-6 font-mono"
              />
            </div>

            <Button 
              type="submit"
              disabled={saving}
              className="w-full h-14 text-base font-bold gap-2"
            >
              {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
              {saving ? "Updating System..." : "Update Leveling Engine"}
            </Button>
          </div>
        </div>

        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-8 relative overflow-hidden group">
          <div className="absolute right-0 top-0 h-full w-1 bg-primary/20" />
           <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest mb-6 flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Cosmetic Defaults
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 relative z-10">
             <div className="space-y-2">
                <p className="text-xs text-slate-500 font-bold px-1">Rank Card Color</p>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl border border-slate-700 shadow-inner" style={{ backgroundColor: config.embed_style.color }} />
                  <Input 
                    value={config.embed_style.color}
                    onChange={(e) => setConfig({...config, embed_style: {...config.embed_style, color: e.target.value}})}
                    className="font-mono h-10"
                    disabled={!config.enabled}
                  />
                </div>
             </div>
             <div className="flex items-center justify-between p-4 bg-slate-900/40 rounded-2xl border border-slate-800">
                <div className="flex items-center gap-3">
                  <Layout className="h-4 w-4 text-slate-500" />
                  <span className="text-sm font-bold text-slate-300">Thumbnail</span>
                </div>
                <Switch 
                  checked={config.embed_style.thumbnail}
                  onCheckedChange={(val) => setConfig({...config, embed_style: {...config.embed_style, thumbnail: val}})}
                  disabled={!config.enabled}
                />
             </div>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-6 relative overflow-hidden group shadow-lg">
           <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <Info className="h-32 w-32 text-white" />
           </div>
           <h3 className="text-xs font-black uppercase text-slate-500 tracking-widest mb-4">Leveling Logic</h3>
           <div className="space-y-4 text-sm leading-relaxed text-slate-400">
              <p>Members earn <span className="text-white font-bold italic">XP</span> by chatting.</p>
              <div className="p-4 bg-primary/5 rounded-2xl border border-primary/10 text-[10px] font-mono">
                 5 * (level ^ 2) + (50 * level) + 100
              </div>
           </div>
        </div>
      </div>
    </form>
  );
}
