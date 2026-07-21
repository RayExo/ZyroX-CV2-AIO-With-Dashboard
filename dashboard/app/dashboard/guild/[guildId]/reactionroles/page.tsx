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
import { MousePointer2, RefreshCcw, Plus, Trash2, BellRing, Info, Save } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";

export default function ReactionRolesPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [loadingAction, setLoadingAction] = useState(false);
  const [config, setConfig] = useState<any>({ dm_enabled: true, roles: [] });
  const [roles, setRoles] = useState<any[]>([]);
  const [newRR, setNewRR] = useState({ message_id: "", emoji: "", role_id: "" });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [configData, rolesData] = await Promise.all([
        api.getRR(params.guildId),
        api.getRoles(params.guildId),
      ]);
      setConfig(configData);
      setRoles(rolesData);
    } catch (error) {
      console.error("Failed to load RR:", error);
      toast.error("Failed to load reaction roles configuration");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [params.guildId]);

  const filteredRoles = roles.filter(r => r.name !== "@everyone");

  const toggleDM = async (val: boolean) => {
    try {
      await api.updateRR(params.guildId, { dm_enabled: val });
      setConfig({ ...config, dm_enabled: val });
      toast.success(`DM notifications ${val ? "enabled" : "disabled"}`);
    } catch {
      toast.error("Failed to update DM setting");
    }
  };

  const handleAdd = async () => {
    if (!newRR.message_id || !newRR.emoji || !newRR.role_id) {
      toast.error("Please fill in all fields");
      return;
    }
    setLoadingAction(true);
    try {
      await api.updateRR(params.guildId, {
        add_role: { message_id: newRR.message_id, emoji: newRR.emoji, role_id: newRR.role_id },
      });
      setConfig({
        ...config,
        roles: [...config.roles, { message_id: newRR.message_id, emoji: newRR.emoji, role_id: newRR.role_id }]
      });
      toast.success("Reaction role added");
      setNewRR({ message_id: "", emoji: "", role_id: "" });
    } catch {
      toast.error("Failed to add reaction role");
    } finally {
      setLoadingAction(false);
    }
  };

  const handleDelete = async (messageId: string, emoji: string) => {
    setLoadingAction(true);
    try {
      await api.updateRR(params.guildId, {
        remove_role_message_id: messageId,
        remove_role_emoji: emoji,
      });
      setConfig({
        ...config,
        roles: config.roles.filter((r: any) => !(String(r.message_id) === String(messageId) && r.emoji === emoji))
      });
      toast.success("Reaction role removed");
    } catch {
      toast.error("Failed to remove reaction role");
    } finally {
      setLoadingAction(false);
    }
  };

  const formatColor = (decimal: number) => {
    if (!decimal || decimal === 0) return "#94a3b8";
    return `#${decimal.toString(16).padStart(6, '0')}`;
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
            <MousePointer2 className="h-6 w-6 text-primary" />
            Reaction Roles
          </h2>
          <p className="text-slate-400 mt-1">Allow members to self-assign roles by reacting to a message.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl p-8 space-y-8">
            
            {/* DM Toggle */}
            <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-primary/20 text-primary rounded-xl"><BellRing className="w-5 h-5" /></div>
                <div>
                  <h3 className="text-lg font-black text-white">DM Notifications</h3>
                  <p className="text-sm text-slate-400 mt-1">Send a DM when a user gets/loses a role.</p>
                </div>
              </div>
              <Switch
                checked={config.dm_enabled}
                onCheckedChange={toggleDM}
                className="scale-125"
              />
            </div>

            {/* Add New */}
            <div className="pt-6 border-t border-slate-800 space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-primary/10 text-primary"><Plus className="h-5 w-5" /></div>
                <h4 className="font-bold text-white text-base">Create New Reaction Role</h4>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-400">Message ID</label>
                  <Input
                    placeholder="e.g. 1234567890"
                    value={newRR.message_id}
                    onChange={(e) => setNewRR({ ...newRR, message_id: e.target.value })}
                    className="bg-slate-900/50 border-slate-800 h-12"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-400">Emoji</label>
                  <Input
                    placeholder="e.g. ✅ or custom emoji"
                    value={newRR.emoji}
                    onChange={(e) => setNewRR({ ...newRR, emoji: e.target.value })}
                    className="bg-slate-900/50 border-slate-800 h-12"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-400">Role to Assign</label>
                  <Select
                    value={newRR.role_id || ""}
                    onValueChange={(val) => setNewRR({ ...newRR, role_id: val })}
                  >
                    <SelectTrigger className="w-full h-12 bg-slate-900/50 border-slate-800">
                      <SelectValue placeholder="Select a role..." />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-800 max-h-[250px]">
                      {filteredRoles.map((role) => (
                        <SelectItem key={role.id} value={role.id} className="focus:bg-slate-800">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: formatColor(role.color) }} />
                            {role.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button onClick={handleAdd} disabled={loadingAction} className="w-full gap-2" variant="secondary">
                {loadingAction ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                Add to Active Listeners
              </Button>
            </div>

            {/* Active roles */}
            <div className="pt-6 border-t border-slate-800 space-y-3">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <MousePointer2 className="h-5 w-5 text-primary" /> Active Reaction Roles
              </h4>

              {config.roles.length === 0 ? (
                <div className="text-center p-8 bg-slate-900/20 rounded-2xl border border-dashed border-slate-700">
                  <p className="text-sm text-slate-500 italic">No reaction roles configured.</p>
                </div>
              ) : (
                config.roles.map((rr: any, idx: number) => {
                  const roleName = filteredRoles.find(r => String(r.id) === String(rr.role_id))?.name || "Unknown Role";
                  return (
                    <div key={idx} className="flex items-center justify-between p-4 bg-slate-900/40 rounded-xl border border-slate-800">
                      <div className="flex items-center gap-6">
                        <div className="flex flex-col">
                          <span className="text-[10px] uppercase font-bold text-slate-500">Message ID</span>
                          <span className="text-sm font-mono text-slate-300">{rr.message_id}</span>
                        </div>
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] uppercase font-bold text-slate-500">Emoji</span>
                          <span className="text-lg">{rr.emoji}</span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[10px] uppercase font-bold text-slate-500">Role</span>
                          <span className="text-sm font-medium text-primary">{roleName}</span>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(String(rr.message_id), rr.emoji)}
                        disabled={loadingAction}
                        className="text-red-400 hover:text-red-300 hover:bg-red-400/10 h-8 w-8 p-0"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <MousePointer2 className="h-32 w-32 text-primary" />
            </div>
            <div className="flex items-center gap-2 mb-4">
              <Info className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-bold text-white">Usage Guide</h3>
            </div>
            <ul className="text-xs text-slate-500 space-y-2">
              <li>• The bot must have access to the message you specify.</li>
              <li>• The bot role must be above the role being assigned.</li>
              <li>• The bot auto-reacts to the message once added.</li>
              <li>• Users react to get the role, un-react to remove it.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
