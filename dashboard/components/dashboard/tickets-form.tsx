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
  Plus, 
  ExternalLink,
  Mail,
  Zap,
  Tag,
  X,
  Save,
  Trash2,
  Settings2,
  Edit3,
  RefreshCcw,
  MessageSquare,
  Hash,
  Shield
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { TicketConfig, TicketCategory, TicketEmbed } from "@/types/api";

interface TicketsFormProps {
  initialConfig: TicketConfig;
  guildId: string;
}

export function TicketsForm({ initialConfig, guildId }: TicketsFormProps) {
  const [config, setConfig] = useState<TicketConfig>(initialConfig);
  const [saving, setSaving] = useState(false);
  const [editingCategory, setEditingCategory] = useState<{index: number, data: TicketCategory} | null>(null);
  const [editingEmbed, setEditingEmbed] = useState<TicketEmbed | null>(null);
  const [isAdding, setIsAdding] = useState(false);

  async function fetchUpdatedConfig() {
    try {
      const data = await api.getTickets(guildId);
      setConfig(data);
    } catch (err) {
      console.error("Failed to fetch ticket config:", err);
    }
  }

  const handleUpdate = async (updateData: any) => {
    setSaving(true);
    const promise = api.updateTickets(guildId, updateData);

    toast.promise(promise, {
      loading: 'Updating ticket settings...',
      success: 'Settings updated successfully',
      error: 'Failed to update settings',
    });

    try {
      await promise;
      await fetchUpdatedConfig();
      setIsAdding(false);
      setEditingCategory(null);
      setEditingEmbed(null);
    } catch (err) {
      console.error("Failed to update settings:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleAddCategory = () => {
    setEditingCategory({ 
      index: -1, 
      data: { name: "", emoji: "📩", staff_roles: [], button_style: 2, discord_category_id: "" } 
    });
    setIsAdding(true);
  };

  const handleRemoveCategory = (index: number) => {
    const newCategories = [...config.categories];
    newCategories.splice(index, 1);
    handleUpdate({ categories: newCategories });
  };

  const handleSaveCategory = () => {
    if (!editingCategory) return;
    const newCategories = [...config.categories];
    if (isAdding) {
      newCategories.push(editingCategory.data);
    } else {
      newCategories[editingCategory.index] = editingCategory.data;
    }
    handleUpdate({ categories: newCategories });
  };

  const handleSaveEmbed = () => {
    if (!editingEmbed) return;
    handleUpdate({
      embed_title: editingEmbed.title,
      embed_description: editingEmbed.description,
      embed_color: editingEmbed.color,
      embed_image_url: editingEmbed.image_url,
      embed_thumbnail_url: editingEmbed.thumbnail_url
    });
  };

  const handleSaveGlobal = () => {
    handleUpdate({
      panel_channel: config.panel_channel,
      logging_channel: config.logging_channel,
      closed_category: config.closed_category,
      panel_type: config.panel_type,
      staff_roles: config.staff_roles
    });
  };

  return (
    <>
      {/* Category Editor Modal */}
      {editingCategory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
           <div className="bg-[#141B2D] border border-slate-800 rounded-3xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
              <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
                <h3 className="font-bold text-lg text-white flex items-center gap-2">
                   {isAdding ? <Plus className="h-5 w-5 text-primary" /> : <Edit3 className="h-5 w-5 text-primary" />}
                   {isAdding ? "Add Category" : "Edit Category"}
                </h3>
                <button onClick={() => setEditingCategory(null)} className="text-slate-500 hover:text-white transition-colors">
                   <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-8 space-y-6">
                <div className="space-y-2">
                   <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Category Name</label>
                   <Input 
                      value={editingCategory.data.name} 
                      onChange={(e) => setEditingCategory({...editingCategory, data: {...editingCategory.data, name: e.target.value}})}
                      placeholder="e.g. Bug Reports"
                   />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Emoji Icon</label>
                    <Input 
                        value={editingCategory.data.emoji || ""} 
                        onChange={(e) => setEditingCategory({...editingCategory, data: {...editingCategory.data, emoji: e.target.value}})}
                        placeholder="e.g. 🐛"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Staff Roles (IDs)</label>
                    <Input 
                        value={editingCategory.data.staff_roles.join(", ")} 
                        onChange={(e) => {
                          const roles = e.target.value.split(",").map(id => id.trim()).filter(id => id && !isNaN(Number(id))).map(Number);
                          setEditingCategory({
                            ...editingCategory, 
                            data: { ...editingCategory.data, staff_roles: roles }
                          })
                        }}
                        placeholder="ID1, ID2..."
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Button Style</label>
                    <Select 
                      value={String(editingCategory.data.button_style || 2)}
                      onValueChange={(val) => setEditingCategory({
                        ...editingCategory,
                        data: { ...editingCategory.data, button_style: parseInt(val) }
                      })}
                    >
                      <SelectTrigger className="bg-slate-900/50 border-slate-800">
                        <SelectValue placeholder="Select Style" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-900 border-slate-800">
                        <SelectItem value="2">Blurple</SelectItem>
                        <SelectItem value="1">Grey</SelectItem>
                        <SelectItem value="3">Green</SelectItem>
                        <SelectItem value="4">Red</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Discord Category ID</label>
                    <Input 
                        value={editingCategory.data.discord_category_id || ""} 
                        onChange={(e) => setEditingCategory({
                          ...editingCategory, 
                          data: { ...editingCategory.data, discord_category_id: e.target.value }
                        })}
                        placeholder="Created tickets go here"
                    />
                  </div>
                </div>
                
                <div className="pt-4 flex gap-3">
                   <Button variant="outline" className="flex-1" onClick={() => setEditingCategory(null)}>Cancel</Button>
                   <Button className="flex-1 gap-2" onClick={handleSaveCategory} disabled={saving || !editingCategory.data.name}>
                     {saving ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                     Save Category
                   </Button>
                </div>
              </div>
           </div>
        </div>
      )}

      {/* Embed Appearance Editor Modal */}
      {editingEmbed && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
           <div className="bg-[#141B2D] border border-slate-800 rounded-3xl w-full max-w-xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
              <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
                <h3 className="font-bold text-lg text-white flex items-center gap-2">
                   <Edit3 className="h-5 w-5 text-primary" />
                   Customize Panel Appearance
                </h3>
                <button onClick={() => setEditingEmbed(null)} className="text-slate-500 hover:text-white transition-colors">
                   <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-8 space-y-6 max-h-[70vh] overflow-y-auto custom-scrollbar">
                <div className="space-y-2">
                   <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Embed Title</label>
                   <Input 
                      value={editingEmbed.title || ""} 
                      onChange={(e) => setEditingEmbed({...editingEmbed, title: e.target.value})}
                      placeholder="e.g. Support Department"
                   />
                </div>
                <div className="space-y-2">
                   <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Embed Description</label>
                   <Textarea 
                      value={editingEmbed.description || ""} 
                      onChange={(e) => setEditingEmbed({...editingEmbed, description: e.target.value})}
                      placeholder="Open a ticket below to talk to our staff..."
                      className="h-24"
                   />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Color (Decimal)</label>
                    <Input 
                        value={editingEmbed.color || ""} 
                        onChange={(e) => setEditingEmbed({...editingEmbed, color: e.target.value ? parseInt(e.target.value) : null})}
                        placeholder="e.g. 16711680 for Red"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Thumbnail URL</label>
                    <Input 
                        value={editingEmbed.thumbnail_url || ""} 
                        onChange={(e) => setEditingEmbed({...editingEmbed, thumbnail_url: e.target.value})}
                        placeholder="Small top-right image"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                   <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Main Image URL</label>
                   <Input 
                      value={editingEmbed.image_url || ""} 
                      onChange={(e) => setEditingEmbed({...editingEmbed, image_url: e.target.value})}
                      placeholder="Large bottom image"
                   />
                </div>
                
                <div className="pt-4 flex gap-3">
                   <Button variant="outline" className="flex-1" onClick={() => setEditingEmbed(null)}>Cancel</Button>
                   <Button className="flex-1 gap-2" onClick={handleSaveEmbed} disabled={saving}>
                     {saving ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                     Save Appearance
                   </Button>
                </div>
              </div>
           </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Stats & Setup */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-8 shadow-xl space-y-8">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-primary/10 text-primary"><Settings2 className="h-5 w-5" /></div>
              <h3 className="text-xl font-bold text-white">Global Configuration</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Panel Channel ID</label>
                <Input 
                  value={config.panel_channel || ""} 
                  onChange={(e) => setConfig({...config, panel_channel: e.target.value})}
                  placeholder="Where the ticket panel lives"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Logging Channel ID</label>
                <Input 
                  value={config.logging_channel || ""} 
                  onChange={(e) => setConfig({...config, logging_channel: e.target.value})}
                  placeholder="Where transcripts go"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Closed Tickets Category ID</label>
                <Input 
                  value={config.closed_category || ""} 
                  onChange={(e) => setConfig({...config, closed_category: e.target.value})}
                  placeholder="Archive closed tickets here"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Panel Interaction Type</label>
                <Select 
                  value={config.panel_type || "button"}
                  onValueChange={(val) => setConfig({...config, panel_type: val})}
                >
                  <SelectTrigger className="bg-slate-900/50 border-slate-800">
                    <SelectValue placeholder="Select Type" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-800">
                    <SelectItem value="button">Buttons</SelectItem>
                    <SelectItem value="dropdown">Dropdown Menu</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2 md:col-span-2">
                <label className="text-xs font-black uppercase text-slate-500 tracking-widest">Global Staff Role IDs</label>
                <Input 
                  value={config.staff_roles.join(", ")} 
                  onChange={(e) => {
                    const roles = e.target.value.split(",").map(id => id.trim()).filter(id => id && !isNaN(Number(id))).map(Number);
                    setConfig({...config, staff_roles: roles})
                  }}
                  placeholder="ID1, ID2... These roles can see all tickets"
                />
              </div>
            </div>

            <Button onClick={handleSaveGlobal} disabled={saving} className="w-full gap-2" variant="secondary">
              {saving ? <RefreshCcw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Save Core Settings
            </Button>
          </div>

          {/* Categories Section */}
          <section className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
            <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/20">
              <div className="flex items-center gap-2">
                <Tag className="h-5 w-5 text-primary" />
                <h3 className="font-bold text-white">Ticket Categories</h3>
              </div>
              <Button size="sm" variant="outline" className="h-8 gap-1 text-xs border-primary/20 text-primary hover:bg-primary/10" onClick={handleAddCategory}>
                 <Plus className="h-3 w-3" />
                 Add New
              </Button>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {config.categories.map((cat, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-2xl border border-white/5 hover:border-primary/30 transition-all group">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center text-xl shadow-inner">
                        {cat.emoji || '📩'}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors">{cat.name}</span>
                        <span className="text-[10px] text-slate-500 flex items-center gap-1 font-mono">
                          <Shield className="h-2 w-2" />
                          {cat.staff_roles && cat.staff_roles.length > 0 ? `${cat.staff_roles.length} Staff Roles` : 'Global Staff'}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
                       <button onClick={() => {
                         setEditingCategory({index: i, data: {...cat}});
                         setIsAdding(false);
                       }} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-primary transition-colors">
                         <Settings2 className="h-4 w-4" />
                       </button>
                       <button onClick={() => handleRemoveCategory(i)} className="p-2 hover:bg-red-500/10 rounded-lg text-slate-400 hover:text-red-500 transition-colors">
                         <Trash2 className="h-4 w-4" />
                       </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </div>

        {/* Right Column: Stats & Configuration */}
        <div className="space-y-6">
          <div className="bg-[#141B2D] border border-slate-800 p-6 rounded-3xl group shadow-lg">
              <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-primary/10 rounded-2xl text-primary group-hover:scale-110 transition-transform">
                    <MessageSquare className="h-6 w-6" />
                  </div>
                  <div className="h-2 w-2 rounded-full bg-primary shadow-[0_0_10px_rgba(88,101,242,0.5)]" />
              </div>
              <p className="text-sm font-medium text-slate-500">Currently Open</p>
              <h3 className="text-3xl font-black text-white mt-1">{config.open_ticket_count} Tickets</h3>
          </div>

          <section className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <Mail className="h-32 w-32 text-white" />
            </div>
            <div className="flex items-center gap-2 mb-4">
              <Zap className="h-5 w-5 text-primary" />
              <h3 className="font-bold text-white">Panel Appearance</h3>
            </div>
            <div className="space-y-3 relative z-10">
               <div className="p-3 bg-black/20 rounded-xl border border-white/5">
                  <p className="text-[10px] uppercase font-bold text-slate-500 mb-1">Title</p>
                  <p className="text-sm text-slate-200 font-medium truncate">{config.embed.title || 'Support Department'}</p>
               </div>
               <div className="p-3 bg-black/20 rounded-xl border border-white/5">
                  <p className="text-[10px] uppercase font-bold text-slate-500 mb-1">Description</p>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {config.embed.description || 'Open a ticket below to talk to our staff.'}
                  </p>
               </div>
            </div>
            <Button 
              variant="secondary" 
              className="w-full mt-6 py-5 text-xs font-bold uppercase tracking-wider"
              onClick={() => setEditingEmbed({...config.embed})}
            >
              Edit Appearance
            </Button>
          </section>
        </div>
      </div>
    </>
  );
}
