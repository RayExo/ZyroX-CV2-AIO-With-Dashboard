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
import { Zap, Save, RefreshCcw, Plus, Trash2, Smile, Info } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export default function AutoReactPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<any>({ triggers: [] });

  const fetchData = async () => {
    try {
      setLoading(true);
      const configData = await api.getAutoReact(params.guildId);
      setConfig(configData);
    } catch (error) {
      console.error("Failed to fetch auto react data:", error);
      toast.error("Failed to load auto react configuration");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [params.guildId]);

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateAutoReact(params.guildId, { triggers: config.triggers });
    toast.promise(promise, {
      loading: 'Saving auto react configuration...',
      success: 'Auto react settings saved!',
      error: 'Failed to save auto react config',
    });
    try { await promise; } catch {} finally { setSaving(false); }
  };

  const addTrigger = () => {
    if (config.triggers.length >= 10) {
      toast.error("Maximum 10 triggers allowed");
      return;
    }
    setConfig({ ...config, triggers: [...config.triggers, { trigger: "", emojis: "" }] });
  };

  const removeTrigger = (index: number) => {
    const newTriggers = [...config.triggers];
    newTriggers.splice(index, 1);
    setConfig({ ...config, triggers: newTriggers });
  };

  const updateTrigger = (index: number, field: string, value: string) => {
    const newTriggers = [...config.triggers];
    newTriggers[index] = { ...newTriggers[index], [field]: value };
    setConfig({ ...config, triggers: newTriggers });
  };

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
            <Zap className="h-6 w-6 text-primary" />
            Auto React
          </h2>
          <p className="text-slate-400 mt-1">Automatically react with emojis when specific trigger words are sent.</p>
        </div>
        <Button onClick={addTrigger} disabled={config.triggers.length >= 10} variant="secondary" className="gap-2">
          <Plus className="w-4 h-4" /> Add Trigger
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl p-8 space-y-6">
            
            {config.triggers.length === 0 ? (
              <div className="text-center p-12 bg-slate-900/20 rounded-2xl border border-dashed border-slate-700">
                <Smile className="w-14 h-14 text-slate-600 mx-auto mb-4" />
                <p className="text-lg font-medium text-slate-400">No triggers configured</p>
                <p className="text-sm text-slate-500 mb-6">Start by adding your first auto-reaction trigger.</p>
                <Button variant="outline" onClick={addTrigger} className="gap-2">
                  <Plus className="w-4 h-4" /> Add Your First Trigger
                </Button>
              </div>
            ) : (
              <>
                {config.triggers.map((item: any, index: number) => (
                  <div key={index} className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4 animate-in zoom-in-95 duration-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-yellow-500/10 text-yellow-500">
                          <Zap className="h-4 w-4" />
                        </div>
                        <h4 className="font-bold text-white">Trigger #{index + 1}</h4>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => removeTrigger(index)} className="text-red-400 hover:text-red-300 hover:bg-red-400/10 h-8 w-8 p-0">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-400">Trigger Word (single word)</label>
                        <Input
                          placeholder="e.g. hello"
                          value={item.trigger}
                          onChange={(e) => updateTrigger(index, "trigger", e.target.value)}
                          className="bg-slate-900/50 border-slate-800 h-12"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-400">Emojis (space separated)</label>
                        <Input
                          placeholder="e.g. 👋 ✨ ❤️"
                          value={item.emojis}
                          onChange={(e) => updateTrigger(index, "emojis", e.target.value)}
                          className="bg-slate-900/50 border-slate-800 h-12"
                        />
                      </div>
                    </div>
                  </div>
                ))}

                <Button onClick={handleSave} disabled={saving} className="w-full h-14 text-base font-bold gap-2">
                  {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
                  Save All Triggers
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-yellow-500/10 to-transparent border border-yellow-500/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <Zap className="h-32 w-32 text-yellow-500" />
            </div>
            <div className="flex items-center gap-2 mb-4">
              <Info className="h-4 w-4 text-yellow-500" />
              <h3 className="text-sm font-bold text-white">How It Works</h3>
            </div>
            <ul className="text-xs text-slate-500 space-y-2">
              <li>• Triggers are single words that the bot watches for.</li>
              <li>• When a message contains a trigger, the bot reacts with the configured emojis.</li>
              <li>• Up to 10 emojis per trigger, and 10 triggers max per guild.</li>
              <li>• Custom emojis must be from this server.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
