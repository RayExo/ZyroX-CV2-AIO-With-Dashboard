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
import { Shield, Save, RefreshCcw, Power, Fingerprint, Bell, Hash, UserCheck, Info } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";

export default function VerificationPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [channels, setChannels] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [config, setConfig] = useState<any>({
    verification_channel_id: null,
    verified_role_id: null,
    log_channel_id: null,
    verification_method: "both",
    enabled: true,
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [configData, channelsData, rolesData] = await Promise.all([
        api.getVerification(params.guildId),
        api.getChannels(params.guildId),
        api.getRoles(params.guildId),
      ]);
      setConfig(configData);
      setChannels(channelsData);
      setRoles(rolesData);
    } catch (error) {
      console.error("Failed to fetch verification data:", error);
      toast.error("Failed to load verification configuration");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [params.guildId]);

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateVerification(params.guildId, {
      verification_channel_id: config.verification_channel_id,
      verified_role_id: config.verified_role_id,
      log_channel_id: config.log_channel_id,
      verification_method: config.verification_method,
      enabled: config.enabled,
    });
    toast.promise(promise, {
      loading: 'Saving verification configuration...',
      success: 'Verification settings saved!',
      error: 'Failed to save verification config',
    });
    try { await promise; } catch {} finally { setSaving(false); }
  };

  const textChannels = channels.filter(c => c.type === "0" || c.type === 0);
  const filteredRoles = roles.filter(r => r.name !== "@everyone");

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
            <Shield className="h-6 w-6 text-primary" />
            Verification
          </h2>
          <p className="text-slate-400 mt-1">Set up a gatekeeper system to verify new members.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl p-8 space-y-8">
            
            {/* Enable/Disable Toggle */}
            <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
              <div className="flex items-center gap-4">
                <div className={cn("p-3 rounded-xl transition-colors", config.enabled ? "bg-emerald-500/20 text-emerald-500" : "bg-red-500/20 text-red-500")}>
                  <Power className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-white">System Status</h3>
                  <p className="text-sm text-slate-400 mt-1">Enable or disable the verification module.</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="px-4 py-2 rounded-full bg-slate-900 border border-slate-800 flex items-center gap-2">
                  <div className={cn("w-2 h-2 rounded-full", config.enabled ? 'bg-emerald-500 animate-pulse' : 'bg-red-500')} />
                  <span className="text-xs font-bold uppercase text-slate-300">
                    {config.enabled ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <Switch 
                  checked={config.enabled} 
                  onCheckedChange={(val) => setConfig({ ...config, enabled: val })}
                  className="scale-125 data-[state=checked]:bg-emerald-500"
                />
              </div>
            </div>

            {/* Selectors Grid */}
            <div className={cn("grid grid-cols-1 md:grid-cols-2 gap-6 transition-all duration-300", !config.enabled && "opacity-50 pointer-events-none")}>
              {/* Verification Channel */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary/20 text-primary rounded-xl"><Hash className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Verification Channel</h4>
                    <p className="text-xs text-slate-400 mt-1">Channel where verification happens</p>
                  </div>
                </div>
                <Select
                  value={config.verification_channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, verification_channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select a channel..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Not Set</SelectItem>
                    {textChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id} className="focus:bg-slate-800">#{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Verified Role */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-emerald-500/20 text-emerald-500 rounded-xl"><UserCheck className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Verified Role</h4>
                    <p className="text-xs text-slate-400 mt-1">Role given after verification</p>
                  </div>
                </div>
                <Select
                  value={config.verified_role_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, verified_role_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select a role..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Not Set</SelectItem>
                    {filteredRoles.map((r) => (
                      <SelectItem key={r.id} value={r.id} className="focus:bg-slate-800">{r.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Verification Method */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-purple-500/20 text-purple-500 rounded-xl"><Fingerprint className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Verification Method</h4>
                    <p className="text-xs text-slate-400 mt-1">How users verify themselves</p>
                  </div>
                </div>
                <Select
                  value={config.verification_method || "both"}
                  onValueChange={(val) => setConfig({ ...config, verification_method: val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select method..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800">
                    <SelectItem value="button" className="focus:bg-slate-800">Button Click</SelectItem>
                    <SelectItem value="captcha" className="focus:bg-slate-800">CAPTCHA Image</SelectItem>
                    <SelectItem value="both" className="focus:bg-slate-800">Both (Combined)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Log Channel */}
              <div className="p-6 bg-slate-900/40 border border-slate-800 rounded-2xl space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-500/20 text-blue-500 rounded-xl"><Bell className="w-5 h-5" /></div>
                  <div>
                    <h4 className="font-bold text-white">Log Channel</h4>
                    <p className="text-xs text-slate-400 mt-1">Where verification logs are sent</p>
                  </div>
                </div>
                <Select
                  value={config.log_channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, log_channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select a channel..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800 max-h-[300px]">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Disabled</SelectItem>
                    {textChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id} className="focus:bg-slate-800">#{c.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button onClick={handleSave} disabled={saving} className="w-full h-14 text-base font-bold gap-2">
              {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
              Save Configuration
            </Button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <Shield className="h-32 w-32 text-primary" />
            </div>
            <div className="flex items-center gap-2 mb-4">
              <Info className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-bold text-white">Important</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Ensure @everyone does NOT have &quot;Send Messages&quot; in non-verification channels.
            </p>
            <ul className="text-xs text-slate-500 space-y-2">
              <li>• Assign the Verified Role only to members who pass.</li>
              <li>• The bot role must be above the Verified Role.</li>
              <li>• CAPTCHA provides stronger anti-bot protection.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
