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
import { ShieldCheck, RefreshCcw, Save, Hash, Settings, User } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { VerificationConfig, DiscordChannel } from "@/types/api";

interface VerificationFormProps {
  initialConfig: VerificationConfig;
  channels: DiscordChannel[];
  roles: any[]; // We don't have a rigid Role interface but they have id, name.
  guildId: string;
}

export function VerificationForm({ initialConfig, channels, roles, guildId }: VerificationFormProps) {
  const [config, setConfig] = useState<VerificationConfig>(initialConfig);
  const [saving, setSaving] = useState(false);

  const textChannels = channels.filter((c) => c.type === "0");

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateVerification(guildId, config);

    toast.promise(promise, {
      loading: 'Saving Verification configuration...',
      success: 'Verification settings saved successfully!',
      error: 'Failed to update Verification config',
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
          
          {/* Main Toggle */}
          <div className="flex items-center justify-between p-6 bg-slate-900/40 rounded-2xl border border-slate-800">
            <div>
              <h3 className="text-lg font-black text-white">Verification System</h3>
              <p className="text-sm text-slate-400 mt-1">Enable or disable server verification.</p>
            </div>
            <Switch 
              checked={config.enabled} 
              onCheckedChange={(val) => setConfig({ ...config, enabled: val })}
              className="scale-125"
            />
          </div>

          <div className={`space-y-6 transition-all duration-300 ${!config.enabled && "opacity-50 pointer-events-none"}`}>
            {/* Channel Setup */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              <div className="space-y-3">
                <label className="text-sm font-bold text-slate-300 flex items-center gap-2">
                  <Hash className="h-4 w-4 text-slate-400" />
                  Verification Channel
                </label>
                <Select
                  value={config.verification_channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, verification_channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select a channel..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Not Set</SelectItem>
                    {textChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id.toString()} className="focus:bg-slate-800">
                        # {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500">The channel where verifying users will use the command/buttons.</p>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-bold text-slate-300 flex items-center gap-2">
                  <Hash className="h-4 w-4 text-slate-400" />
                  Log Channel
                </label>
                <Select
                  value={config.log_channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, log_channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select log channel..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Not Set</SelectItem>
                    {textChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id.toString()} className="focus:bg-slate-800">
                        # {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500">Channel to send verification success/fail logs.</p>
              </div>

            </div>

            {/* Role Setup & Method */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              <div className="space-y-3">
                <label className="text-sm font-bold text-slate-300 flex items-center gap-2">
                  <User className="h-4 w-4 text-slate-400" />
                  Verified Role
                </label>
                <Select
                  value={config.verified_role_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, verified_role_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select verified role..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800">
                    <SelectItem value="none" className="text-slate-400 focus:bg-slate-800">Not Set</SelectItem>
                    {roles.map((r) => (
                      <SelectItem key={r.id} value={r.id.toString()} className="focus:bg-slate-800">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: `#${r.color.toString(16).padStart(6, '0')}` }} />
                          {r.name}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500">The role given upon successful verification.</p>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-bold text-slate-300 flex items-center gap-2">
                  <Settings className="h-4 w-4 text-slate-400" />
                  Verification Method
                </label>
                <Select
                  value={config.verification_method || "both"}
                  onValueChange={(val) => setConfig({ ...config, verification_method: val })}
                >
                  <SelectTrigger className="w-full h-12 bg-slate-900 border-slate-800 font-medium">
                    <SelectValue placeholder="Select method..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800">
                    <SelectItem value="captcha" className="focus:bg-slate-800">CAPTCHA Only</SelectItem>
                    <SelectItem value="button" className="focus:bg-slate-800">Button Click Only</SelectItem>
                    <SelectItem value="both" className="focus:bg-slate-800">Both Choices Setup</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500">Select how users will be verified.</p>
              </div>

            </div>

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
        <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
            <ShieldCheck className="h-32 w-32 text-primary" />
          </div>
          <h3 className="text-sm font-bold text-primary mb-2">How It Works</h3>
          <p className="text-xs text-slate-400 leading-relaxed mb-4">
            Zyrox Verification ensures that no unauthorized bots or malicious users enter your server unverified.
          </p>
          <ul className="text-xs text-slate-500 space-y-2">
             <li>• The bot will create a panel in your Verification Channel.</li>
             <li>• Unverified members must click &quot;Verify&quot;.</li>
             <li>• Captcha presents a unique image sequence.</li>
             <li>• Upon success, role is assigned.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
