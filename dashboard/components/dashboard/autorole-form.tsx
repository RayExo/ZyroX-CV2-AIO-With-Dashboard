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
import { UserPlus, Save, RefreshCcw, User, Bot, Trash2, ShieldCheck, Info } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AutoRoleConfig, DiscordRole } from "@/types/api";
import { cn } from "@/lib/utils";

interface AutoRoleFormProps {
  initialConfig: AutoRoleConfig;
  roles: DiscordRole[];
  guildId: string;
}

export function AutoRoleForm({ initialConfig, roles, guildId }: AutoRoleFormProps) {
  const [config, setConfig] = useState<AutoRoleConfig>(initialConfig);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    // Be explicit about fields to send to match AutoRoleUpdate schema
    const data = {
      bots: config.bots,
      humans: config.humans
    };
    const promise = api.updateAutoRole(guildId, data);

    toast.promise(promise, {
      loading: 'Saving AutoRole configuration...',
      success: 'Settings saved successfully!',
      error: 'Failed to update AutoRole config',
    });

    try {
      await promise;
    } catch (err: any) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const addRole = (type: "humans" | "bots", roleId: string) => {
    if (config[type].includes(roleId)) return;
    if (config[type].length >= 10) {
      toast.error(`You can only add up to 10 roles for ${type === "humans" ? "Members" : "Bots"}.`);
      return;
    }
    setConfig({ ...config, [type]: [...config[type], roleId] });
  };

  const removeRole = (type: "humans" | "bots", roleId: string) => {
    setConfig({ ...config, [type]: config[type].filter(r => r !== roleId) });
  };

  const formatColor = (decimal: number) => {
    if (!decimal || decimal === 0) return "#94a3b8";
    return `#${decimal.toString(16).padStart(6, '0')}`;
  };

  const renderRoleList = (type: "humans" | "bots") => {
    const title = type === "humans" ? "Member Roles" : "Bot Roles";
    const Icon = type === "humans" ? User : Bot;
    const accentColor = type === "humans" ? "text-primary" : "text-blue-400";
    const bgColor = type === "humans" ? "bg-primary/10" : "bg-blue-400/10";

    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <div className={cn("p-2.5 rounded-xl", bgColor, accentColor)}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <h4 className="font-bold text-white text-base">{title}</h4>
            <p className="text-xs text-slate-400">Roles given to newly joined {type}.</p>
          </div>
        </div>
        
        <Select value="" onValueChange={(val) => addRole(type, val)}>
          <SelectTrigger className="w-full h-12 bg-slate-900/50 border-slate-800 hover:border-slate-700 transition-all">
            <SelectValue placeholder={`Add a ${type === "humans" ? "member" : "bot"} role...`} />
          </SelectTrigger>
          <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
            {roles
              .filter(r => !config[type].includes(r.id))
              .sort((a, b) => (b.position || 0) - (a.position || 0))
              .map((r) => (
                <SelectItem key={r.id} value={r.id} className="focus:bg-slate-800 group">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full" 
                      style={{ backgroundColor: formatColor(r.color) }}
                    />
                    <span>{r.name}</span>
                  </div>
                </SelectItem>
              ))}
          </SelectContent>
        </Select>

        <div className="grid grid-cols-1 gap-2 min-h-[100px] p-4 bg-slate-900/40 rounded-2xl border border-slate-800/50 relative overflow-hidden">
          {config[type].length === 0 ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center opacity-20">
              <ShieldCheck className="h-8 w-8 mb-2" />
              <span className="text-xs font-medium">No roles selected</span>
            </div>
          ) : (
            <div className="flex flex-wrap gap-2 relative z-10">
              {config[type].map((roleId) => {
                const role = roles.find(r => r.id === roleId);
                const color = role ? formatColor(role.color) : "#94a3b8";
                return (
                  <div 
                    key={roleId} 
                    className="flex items-center gap-2 bg-slate-800/80 border border-slate-700/50 px-3 py-1.5 rounded-lg text-sm group animate-in zoom-in-95 duration-200"
                  >
                    <div 
                      className="w-2 h-2 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)]" 
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-slate-200 font-medium">{role ? role.name : `Unknown (${roleId})`}</span>
                    <button 
                      onClick={() => removeRole(type, roleId)}
                      className="ml-1 text-slate-500 hover:text-red-400 transition-colors p-0.5 rounded-md hover:bg-red-400/10"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <div className="lg:col-span-3 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-[32px] shadow-2xl p-8 space-y-10 relative">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {renderRoleList("humans")}
            {renderRoleList("bots")}
          </div>

          <div className="pt-6 border-t border-slate-800">
            <Button 
              onClick={handleSave}
              disabled={saving}
              className="w-full h-14 text-base font-bold gap-3 shadow-lg shadow-primary/20 hover:shadow-primary/30 active:scale-[0.98] transition-all"
            >
              {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
              Save AutoRole Settings
            </Button>
          </div>

        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-gradient-to-br from-[#141B2D] to-slate-900 border border-slate-800 rounded-3xl p-6 relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 opacity-[0.05] group-hover:scale-110 transition-transform duration-500">
            <UserPlus className="h-40 w-40 text-primary" />
          </div>
          
          <div className="flex items-center gap-2 mb-4">
            <Info className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-bold text-white">Guidelines</h3>
          </div>
          
          <p className="text-xs text-slate-400 leading-relaxed mb-6">
            AutoRole ensures every new member is welcomed with the right sets of roles immediately upon joining.
          </p>
          
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
              <p className="text-[11px] text-slate-400 leading-relaxed">
                <span className="text-slate-200 font-bold">Hierarchy Matter:</span> Ensure ZyroX&apos;s top role is <span className="text-primary italic">higher</span> than any role you select here.
              </p>
            </div>
            <div className="flex gap-3">
              <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
              <p className="text-[11px] text-slate-400 leading-relaxed">
                <span className="text-slate-200 font-bold">Bot Detection:</span> We automatically separate bots from human members for precise role assignment.
              </p>
            </div>
            <div className="flex gap-3">
              <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 shrink-0" />
              <p className="text-[11px] text-slate-400 leading-relaxed">
                <span className="text-slate-200 font-bold">Limits:</span> We has limits on roles. We support up to 10 roles per category for stability.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
