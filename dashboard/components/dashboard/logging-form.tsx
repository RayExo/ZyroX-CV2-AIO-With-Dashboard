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
  MessageSquare,
  UserPlus,
  ShieldAlert,
  Mic,
  Settings,
  Hash,
  ChevronRight,
  BellRing,
  Info
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { LoggingConfig, DiscordChannel } from "@/types/api";

const LOG_CATEGORIES = [
  { id: "message_events", name: "Message Events", icon: MessageSquare, description: "Log message deletions, edits, and bulk removals." },
  { id: "join_leave_events", name: "Join & Leave Events", icon: UserPlus, description: "Track when members join or leave the server." },
  { id: "member_moderation", name: "Moderation Events", icon: ShieldAlert, description: "Log kicks, bans, and timeout updates." },
  { id: "voice_events", name: "Voice Events", icon: Mic, description: "Track members joining, leaving, or moving voice channels." },
  { id: "role_events", name: "Role Changes", icon: Settings, description: "Log role creation, deletion, and permission updates." },
  { id: "channel_events", name: "Channel Changes", icon: Hash, description: "Track channel creation, deletion, and settings updates." },
];

interface LoggingFormProps {
  initialConfig: LoggingConfig;
  channels: DiscordChannel[];
  guildId: string;
}

export function LoggingForm({ initialConfig, channels, guildId }: LoggingFormProps) {
  const [config, setConfig] = useState<LoggingConfig>(initialConfig);
  const [saving, setSaving] = useState(false);

  const handleToggle = async (categoryId: string, enabled: boolean) => {
    // Optimistic update
    const newLogEnabled = { ...config.log_enabled, [categoryId]: enabled };
    setConfig({ ...config, log_enabled: newLogEnabled });

    try {
      await api.updateLogging(guildId, {
        log_enabled: { [categoryId]: enabled }
      });
      toast.success(`${enabled ? 'Enabled' : 'Disabled'} ${categoryId.replace('_', ' ')} logging`);
    } catch (err: any) {
      setConfig(config);
      toast.error("Failed to update logging setting.");
    }
  };

  const handleChannelChange = async (categoryId: string, channelId: string) => {
    // Optimistic update
    const newLogChannels = { ...config.log_channels, [categoryId]: parseInt(channelId) };
    setConfig({ ...config, log_channels: newLogChannels });

    setSaving(true);
    const promise = api.updateLogging(guildId, {
      log_channels: { [categoryId]: parseInt(channelId) }
    });

    toast.promise(promise, {
      loading: 'Updating log channel...',
      success: 'Log channel updated successfully',
      error: 'Failed to update log channel',
    });

    try {
      await promise;
    } catch (err: any) {
      setConfig(config);
    } finally {
      setSaving(false);
    }
  };

  const channelOptions = channels.map(c => ({
    value: c.id.toString(),
    label: `#${c.name}`
  }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <div className="lg:col-span-3 space-y-4">
         {LOG_CATEGORIES.map((cat) => (
            <div key={cat.id} className="bg-[#141B2D] border border-slate-800 p-8 rounded-[40px] shadow-xl hover:border-primary/20 transition-all group">
               <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
                  <div className="flex items-start gap-5">
                     <div className="h-14 w-14 rounded-2xl bg-slate-800/50 flex items-center justify-center text-slate-400 group-hover:text-primary transition-colors border border-white/5 shrink-0">
                        <cat.icon className="h-7 w-7" />
                     </div>
                     <div className="flex flex-col">
                        <h3 className="text-lg font-black text-white tracking-tight">{cat.name}</h3>
                        <p className="text-[12px] text-slate-500 font-medium leading-relaxed max-w-sm mt-1">
                          {cat.description}
                        </p>
                     </div>
                  </div>

                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 md:gap-8 lg:min-w-[320px]">
                     <div className="w-full sm:w-48 lg:w-56">
                        <p className="text-[10px] font-black uppercase text-slate-600 mb-2 tracking-widest pl-1">Destination</p>
                        <Select 
                          value={config.log_channels[cat.id]?.toString() || ""}
                          onValueChange={(val) => handleChannelChange(cat.id, val)}
                          options={channelOptions}
                          placeholder="Select channel..."
                          className="bg-black/20 border-slate-800 rounded-xl"
                        />
                     </div>

                     <div className="flex items-center gap-4 border-l border-slate-800/50 pl-4 md:pl-8">
                        <div className="flex-col items-end hidden sm:flex">
                           <span className={cn(
                             "text-[10px] font-black uppercase tracking-widest",
                             config.log_enabled[cat.id] ? "text-emerald-500" : "text-slate-600"
                           )}>
                             {config.log_enabled[cat.id] ? "Active" : "Silent"}
                           </span>
                        </div>
                        <Switch 
                          checked={!!config.log_enabled[cat.id]} 
                          onCheckedChange={(val) => handleToggle(cat.id, val)}
                        />
                     </div>
                  </div>
               </div>
            </div>
         ))}
      </div>

      <div className="space-y-6">
         <section className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-[40px] p-8 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <BellRing className="h-32 w-32 text-white" />
            </div>
            <div className="flex items-center gap-2 mb-6">
              <Info className="h-5 w-5 text-primary" />
              <h3 className="font-bold text-white text-lg tracking-tight">Logging Engine</h3>
            </div>
            <div className="space-y-4 relative z-10">
               <div className="p-4 bg-black/20 rounded-2xl border border-white/5 space-y-2">
                  <p className="text-[10px] uppercase font-bold text-slate-500">Intelligent Routing</p>
                  <p className="text-xs text-slate-300 leading-relaxed font-medium">Assign specific channels to different event types for better organization.</p>
               </div>
               <div className="p-4 bg-black/20 rounded-2xl border border-white/5 space-y-2">
                  <p className="text-[10px] uppercase font-bold text-slate-500">Webhooks</p>
                  <p className="text-xs text-slate-300 leading-relaxed font-medium">Coming soon: Export audit logs to external webhooks and elastic systems.</p>
               </div>
            </div>
            <Button variant="secondary" className="w-full mt-8 py-6 rounded-[24px] font-black uppercase tracking-tighter text-xs">
               Save Global Config
            </Button>
         </section>

         <div className="bg-[#141B2D] border border-slate-800 rounded-[40px] p-8 shadow-xl">
           <h3 className="text-xs font-black uppercase text-slate-500 tracking-[0.15em] mb-6 flex items-center gap-2">
             <ShieldAlert className="h-4 w-4 text-amber-500" />
             Audit Protection
           </h3>
           <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-900/40 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors">
                 <span className="text-xs font-bold text-slate-400">Protect Roles</span>
                 <span className="bg-slate-800 text-slate-300 px-2 py-1 rounded-md text-[10px] font-black">{config.ignore_roles.length}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-900/40 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors">
                 <span className="text-xs font-bold text-slate-400">Secure Channels</span>
                 <span className="bg-slate-800 text-slate-300 px-2 py-1 rounded-md text-[10px] font-black">{config.ignore_channels.length}</span>
              </div>
           </div>
           <p className="text-[10px] text-slate-600 mt-6 leading-relaxed italic text-center">
             Events from these entities are currently bypassed by the audit logger.
           </p>
         </div>
      </div>
    </div>
  );
}
