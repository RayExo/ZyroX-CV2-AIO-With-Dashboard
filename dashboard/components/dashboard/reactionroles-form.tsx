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
import { MousePointer2, Save, RefreshCcw, Plus, Trash2, BellRing, Settings } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

interface ReactionRolesFormProps {
  initialConfig: any;
  roles: any[];
  guildId: string;
}

export function ReactionRolesForm({ initialConfig, roles, guildId }: ReactionRolesFormProps) {
  const [config, setConfig] = useState<any>(initialConfig);
  const [saving, setSaving] = useState(false);
  const [loadingAction, setLoadingAction] = useState(false);

  const [newRR, setNewRR] = useState({
    message_id: "",
    emoji: "",
    role_id: "",
  });

  const filteredRoles = roles.filter(r => r.name !== "@everyone");

  const toggleDM = async (val: boolean) => {
    try {
      await api.updateRR(guildId, { dm_enabled: val });
      setConfig({ ...config, dm_enabled: val });
      toast.success(`DM notifications ${val ? "enabled" : "disabled"}`);
    } catch (error) {
      toast.error("Failed to update DM setting");
    }
  };

  const handleAdd = async () => {
    if (!newRR.message_id || !newRR.emoji || !newRR.role_id) {
      toast.error("Please fill in all fields");
      return;
    }

    try {
      setLoadingAction(true);
      await api.updateRR(guildId, {
        add_role: {
          message_id: parseInt(newRR.message_id),
          emoji: newRR.emoji,
          role_id: parseInt(newRR.role_id),
        },
      });
      // Try to optimistically add to the UI
      setConfig({
        ...config,
        roles: [...config.roles, { message_id: newRR.message_id, emoji: newRR.emoji, role_id: newRR.role_id }]
      });
      toast.success("Reaction role added");
      setNewRR({ message_id: "", emoji: "", role_id: "" });
    } catch (error) {
      toast.error("Failed to add reaction role");
    } finally {
      setLoadingAction(false);
    }
  };

  const handleDelete = async (messageId: number, emoji: string) => {
    try {
      setLoadingAction(true);
      await api.updateRR(guildId, {
        remove_role_message_id: messageId,
        remove_role_emoji: emoji,
      });
      setConfig({
        ...config,
        roles: config.roles.filter((r: any) => !(r.message_id === messageId && r.emoji === emoji))
      });
      toast.success("Reaction role removed");
    } catch (error) {
      toast.error("Failed to remove reaction role");
    } finally {
      setLoadingAction(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <div className="lg:col-span-3 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl shadow-xl p-8 space-y-8">
          
          <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/20 text-primary rounded-xl">
                <BellRing className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-black text-white">DM Notifications</h3>
                <p className="text-sm text-slate-400 mt-1">Send a direct message when a user gets/loses a role.</p>
              </div>
            </div>
            <Switch 
              checked={config.dm_enabled} 
              onCheckedChange={toggleDM}
              className="scale-125"
            />
          </div>

          <div className="pt-6 border-t border-slate-800">
            <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <Plus className="h-5 w-5 text-primary" />
              Create New Reaction Role
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400">Message ID</label>
                <Input 
                  placeholder="e.g. 1234567890" 
                  value={newRR.message_id}
                  onChange={(e) => setNewRR({ ...newRR, message_id: e.target.value })}
                  className="bg-slate-900/50 h-10"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400">Emoji</label>
                <Input 
                  placeholder="e.g. ✅" 
                  value={newRR.emoji}
                  onChange={(e) => setNewRR({ ...newRR, emoji: e.target.value })}
                  className="bg-slate-900/50 h-10"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-400">Role to Assign</label>
                <Select
                  value={newRR.role_id ? newRR.role_id.toString() : ""}
                  onValueChange={(val) => setNewRR({ ...newRR, role_id: val })}
                >
                  <SelectTrigger className="w-full h-10 bg-slate-900/50 border-slate-800">
                    <SelectValue placeholder="Select a role..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[250px]">
                    {filteredRoles.map((role) => (
                      <SelectItem key={role.id} value={role.id.toString()} className="focus:bg-slate-800">
                        {role.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Button 
              onClick={handleAdd} 
              disabled={loadingAction} 
              className="w-full gap-2"
              variant="secondary"
            >
              {loadingAction ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              Add to Active Listeners
            </Button>
          </div>

          <div className="pt-6 border-t border-slate-800">
            <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <MousePointer2 className="h-5 w-5 text-primary" />
              Active Reaction Roles
            </h4>

            <div className="space-y-3">
              {config.roles.length === 0 ? (
                <div className="text-center p-8 bg-slate-900/20 rounded-2xl border border-dashed border-slate-700">
                  <p className="text-sm text-slate-500 italic">No reaction roles currently configured.</p>
                </div>
              ) : (
                config.roles.map((rr: any, idx: number) => {
                  const roleName = roles.find(r => r.id === rr.role_id.toString())?.name || "Unknown Role";
                  
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
                        onClick={() => handleDelete(rr.message_id, rr.emoji)}
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
      </div>

      <div className="space-y-6">
        <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
            <MousePointer2 className="h-32 w-32 text-primary" />
          </div>
          <h3 className="text-sm font-bold text-primary mb-2">Usage Guide</h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-4">
            Reaction Roles allow members to self-assign their own roles with a single click.
          </p>
          <ul className="text-xs text-slate-500 space-y-2">
             <li>• The bot must have access to see the message you specify.</li>
             <li>• Make sure the bot role is HIGHER than the role you are attempting to assign.</li>
             <li>• The bot will automatically react to the message once you click &quot;Add to Active Listeners&quot;.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
