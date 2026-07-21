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
import { MessageSquare, Save, RefreshCcw, Send } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

export default function JoinDMPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<any>({
    message: "",
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const configData = await api.getJoinDM(params.guildId);
      setConfig(configData);
    } catch (error) {
      console.error("Failed to fetch JoinDM data:", error);
      toast.error("Failed to load Join DM configuration");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [params.guildId]);

  const handleSave = async () => {
    try {
      setSaving(true);
      await api.updateJoinDM(params.guildId, config);
      toast.success("Join DM configuration saved successfully");
    } catch (error) {
      console.error("Failed to save JoinDM config:", error);
      toast.error("Failed to save Join DM configuration");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <RefreshCcw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Join DM</h2>
        <p className="text-muted-foreground">
          Send a private message to new members when they join your server.
        </p>
      </div>

      <Card className="border-primary/20 bg-background/50 backdrop-blur-xl">
        <CardHeader>
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary" />
            <CardTitle>Welcome Message</CardTitle>
          </div>
          <CardDescription>
            This message will be sent to the user&apos;s DMs. You can use text to welcome them.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Message Content</Label>
            <Textarea
              placeholder="Welcome to the server! Make sure to read the rules..."
              className="min-h-[200px]"
              value={config.message || ""}
              onChange={(e) => setConfig({ ...config, message: e.target.value })}
            />
          </div>

          <div className="flex justify-end pt-4">
            <Button onClick={handleSave} disabled={saving} className="gap-2">
              {saving ? <RefreshCcw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Save Message
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="border-blue-500/20 bg-blue-500/5">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Send className="w-5 h-5 text-blue-500" />
            <CardTitle className="text-blue-500 text-base">Usage Note</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The bot will automatically attach &quot;Sent from [Server Name]&quot; to the end of your message. 
            Ensure your bot has permissions to DM members (usually by being in the same server and not being blocked).
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
