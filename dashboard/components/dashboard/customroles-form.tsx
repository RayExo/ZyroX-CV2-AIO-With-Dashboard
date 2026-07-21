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
import { Shield, Save, RefreshCcw, Star, Crown, Heart, Ghost, Settings } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface CustomRolesFormProps {
  initialConfig: any;
  roles: any[];
  guildId: string;
}

const ROLE_INPUTS = [
  { label: "Staff Role", key: "staff", icon: Shield, color: "text-blue-500", bg: "bg-blue-500/20" },
  { label: "Girl Role", key: "girl", icon: Heart, color: "text-pink-500", bg: "bg-pink-500/20" },
  { label: "VIP Role", key: "vip", icon: Crown, color: "text-yellow-500", bg: "bg-yellow-500/20" },
  { label: "Guest Role", key: "guest", icon: Ghost, color: "text-gray-400", bg: "bg-gray-400/20" },
  { label: "Friend Role", key: "frnd", icon: Star, color: "text-green-500", bg: "bg-green-500/20" },
];

export function CustomRolesForm({ initialConfig, roles, guildId }: CustomRolesFormProps) {
  const [config, setConfig] = useState<any>(initialConfig);
  const [saving, setSaving] = useState(false);

  const filteredRoles = roles.filter(r => r.name !== "@everyone");

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateCustomRoles(guildId, config);

    toast.promise(promise, {
      loading: 'Saving Custom Roles configuration...',
      success: 'Custom Roles settings saved successfully!',
      error: 'Failed to update Custom Roles config',
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
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <div className="lg:col-span-3 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl shadow-xl p-8 space-y-8">
          
          <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/20 text-primary rounded-xl">
                <Settings className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-black text-white">Required Permission Role</h3>
                <p className="text-sm text-slate-400 mt-1">Users need this role to assign the custom roles below.</p>
              </div>
            </div>
            
            <div className="w-64">
              <Select
                value={config.reqrole?.toString() || "none"}
                onValueChange={(val) => setConfig({ ...config, reqrole: val === "none" ? null : parseInt(val) })}
              >
                <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                  <SelectValue placeholder="Select required role..." />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                  <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">None required / Admins only</SelectItem>
                  {filteredRoles.map((role) => (
                    <SelectItem key={role.id} value={role.id.toString()} className="focus:bg-slate-800">
                      {role.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {ROLE_INPUTS.map((input) => (
              <div key={input.key} className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4 hover:border-slate-700 transition-all duration-300">
                <div className="flex items-center gap-3">
                  <div className={cn("p-3 rounded-xl", input.bg, input.color)}>
                    <input.icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white">{input.label}</h4>
                    <p className="text-xs text-slate-400 mt-1">Role assigned via .{input.key} command</p>
                  </div>
                </div>
                
                <Select
                  value={config[input.key]?.toString() || "none"}
                  onValueChange={(val) => setConfig({ ...config, [input.key]: val === "none" ? null : parseInt(val) })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select a role..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Not Set</SelectItem>
                    {filteredRoles.map((role) => (
                      <SelectItem key={role.id} value={role.id.toString()} className="focus:bg-slate-800">
                        {role.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ))}
          </div>

          <Button 
            onClick={handleSave}
            disabled={saving}
            className="w-full h-14 text-base font-bold gap-2"
          >
            {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
            Save Configuration
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        <div className="bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20 rounded-3xl p-6 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
            <Crown className="h-32 w-32 text-blue-500" />
          </div>
          <h3 className="text-sm font-bold text-blue-400 mb-2">Command Usage</h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-4">
            Allows your trusted server managers to grant specific preset roles with simple prefix commands.
          </p>
          <ul className="text-xs text-slate-500 space-y-2">
             <li>• <code>.staff @user</code> - Assigns/Removes Staff role</li>
             <li>• <code>.girl @user</code> - Assigns/Removes Girl role</li>
             <li>• <code>.vip @user</code> - Assigns/Removes VIP role</li>
             <li>• Ensure Zyrox is placed higher than these roles in server settings!</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
