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

import React from "react";
import Link from "next/link";
import { signIn } from "next-auth/react";
import { 
  ShieldCheck, 
  Zap, 
  BarChart4, 
  MessageSquare, 
  ChevronRight, 
  LayoutDashboard,
  LogIn,
  Layers,
  Sparkles,
  Bot,
  Activity,
  History,
  CheckCircle2,
  ShieldAlert,
  Globe,
  Terminal,
  Cpu,
  Users2,
  Lock,
  Radio,
  Gamepad2,
  Music4,
  User
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 selection:bg-red-500/30 font-sans overflow-x-hidden">
      {/* Dynamic Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] bg-red-500/[0.03] blur-[150px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-red-600/[0.03] blur-[150px] rounded-full animate-pulse [animation-delay:2s]" />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.03] bg-[#020617]/80 backdrop-blur-3xl transition-all duration-500">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4 group cursor-pointer">
            <div className="h-11 w-11 rounded-2xl bg-gradient-to-br from-red-500 to-red-800 flex items-center justify-center shadow-lg shadow-red-500/25 border border-white/20 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-lg font-bold tracking-tight text-white font-outfit leading-none">{process.env.NEXT_PUBLIC_BRAND_NAME || "ZyroX"}</h1>
              <span className="text-[9px] font-black uppercase tracking-[0.2em] text-red-500/80 mt-1">Dashboard</span>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-10 text-[11px] font-black uppercase tracking-widest text-slate-500">
            <Link href="#features" className="hover:text-red-500 transition-colors">Features</Link>
            <Link href="#architecture" className="hover:text-red-500 transition-colors">Architecture</Link>
            <Link href="#modules" className="hover:text-red-500 transition-colors">Modules</Link>
            <Link href="#network" className="hover:text-red-500 transition-colors">Network</Link>
          </div>

          <div className="flex items-center gap-4">
            <Button 
              onClick={() => signIn('discord', { callbackUrl: '/dashboard' })}
              className="rounded-xl px-7 h-11 font-black uppercase tracking-widest text-[10px] gap-2.5 shadow-2xl shadow-red-500/20 hover:scale-[1.05] active:scale-95 transition-all bg-gradient-to-r from-red-500 to-red-700 border-none"
            >
              <LogIn className="h-3.5 w-3.5" />
              Initialize Console
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative z-10 pt-56 pb-32 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-2xl bg-red-500/[0.03] border border-red-500/10 text-red-500 text-[10px] font-black uppercase tracking-[0.3em] mb-16 animate-in fade-in slide-in-from-bottom-8 duration-1000 backdrop-blur-md">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-600"></span>
            </span>
            Neural Core v2 Active • Global Shard 07
          </div>
          
          <h1 className="text-6xl sm:text-8xl md:text-[10rem] font-bold text-white tracking-tighter leading-[0.8] mb-12 font-outfit animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-100 uppercase">
            Evolution <br />
            <span className="bg-gradient-to-r from-red-500 via-red-400 to-orange-500 bg-clip-text text-transparent italic font-black">Moderated.</span>
          </h1>

          <p className="text-lg md:text-2xl text-slate-500 max-w-3xl mx-auto leading-relaxed mb-20 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 font-medium">
            The hyper-performance Discord engine. 
            Automated security, cinematic leveling, and precision tools for the world&apos;s most elite communities.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
            <Button 
              onClick={() => signIn('discord', { callbackUrl: '/dashboard' })}
              className="w-full sm:w-auto rounded-2xl px-14 py-9 text-lg font-black uppercase gap-4 group shadow-[0_0_50px_rgba(239,68,68,0.2)] bg-red-600 text-white hover:bg-red-500 border-none transition-all hover:scale-105"
            >
              <LayoutDashboard className="h-6 w-6 group-hover:rotate-12 transition-transform" />
              Open Dashboard
            </Button>
            <Button variant="outline" className="w-full sm:w-auto rounded-2xl px-14 py-9 text-lg font-bold border-white/5 bg-white/[0.02] backdrop-blur-3xl hover:bg-white/[0.05] gap-3 text-white transition-all">
              Add to Server
              <ChevronRight className="h-5 w-5 opacity-40 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>

        {/* Cinematic Dashboard Mockup */}
        <div className="max-w-6xl mx-auto mt-40 relative group animate-in fade-in zoom-in-95 duration-1000 delay-500">
           <div className="absolute -inset-4 bg-gradient-to-r from-red-500/20 to-transparent rounded-[60px] blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
           <div className="relative bg-[#020617] border border-white/[0.05] rounded-[50px] overflow-hidden shadow-[0_30px_100px_rgba(0,0,0,0.8)]">
              {/* Fake Window Controls */}
              <div className="h-16 border-b border-white/[0.03] flex items-center justify-between px-10 bg-white/[0.01]">
                <div className="flex items-center gap-3">
                  <div className="h-3 w-3 rounded-full bg-red-500/40" />
                  <div className="h-3 w-3 rounded-full bg-white/10" />
                  <div className="h-3 w-3 rounded-full bg-white/5" />
                </div>
                <div className="px-6 py-2 rounded-2xl bg-white/[0.03] border border-white/[0.05] text-[10px] font-black text-slate-500 tracking-[0.2em] uppercase">
                   sec.neural.core // active_node_01
                </div>
                <div className="w-12" />
              </div>
              {/* Content Placeholder with High Contrast */}
              <div className="aspect-[16/10] p-16 flex flex-col gap-16 relative overflow-hidden bg-gradient-to-br from-[#020617] to-[#0a0f1e]">
                <div className="flex items-center justify-between z-10 relative">
                  <div className="space-y-6">
                    <div className="h-12 w-64 bg-red-500/10 rounded-[20px] border border-red-500/20" />
                    <div className="h-6 w-[500px] bg-white/[0.02] rounded-xl" />
                  </div>
                  <div className="h-20 w-20 rounded-[30px] bg-red-500/10 border border-red-500/20 flex items-center justify-center shadow-[0_0_30px_rgba(239,68,68,0.2)]">
                    <Activity className="h-8 w-8 text-red-500 animate-pulse" />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-10 z-10">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-40 bg-white/[0.02] border border-white/[0.04] rounded-[40px] p-8 space-y-6 hover:border-red-500/20 transition-colors">
                      <div className="h-10 w-10 rounded-2xl bg-red-500/10 border border-red-500/20" />
                      <div className="h-4 w-2/3 bg-white/5 rounded-lg" />
                      <div className="h-3 w-1/2 bg-white/[0.02] rounded-lg" />
                    </div>
                  ))}
                </div>
                {/* Visual Glow Layer */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90%] h-[90%] bg-red-500/[0.02] blur-[150px] pointer-events-none" />
              </div>
           </div>
        </div>
      </header>

      {/* Grid Section */}
      <section id="features" className="py-48 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-32 gap-12 px-4">
            <div className="max-w-3xl">
              <h2 className="text-6xl md:text-8xl font-bold text-white tracking-tighter font-outfit mb-8 uppercase italic leading-none">High-Scale <br /><span className="text-red-500 not-italic">Infrastructure.</span></h2>
              <p className="text-2xl text-slate-500 font-medium leading-relaxed">Global redundancy delivers sub-millisecond dispatch times across 20+ edge regions. Zero lag, zero downtime.</p>
            </div>
            <div className="flex items-center gap-10 pb-4">
               <div className="text-right">
                 <p className="text-[10px] font-black uppercase text-slate-600 tracking-[0.3em] mb-3">Ping Latency</p>
                 <p className="text-5xl font-black text-red-500 font-outfit">12ms</p>
               </div>
               <div className="h-16 w-[1px] bg-white/5" />
               <div className="text-right">
                 <p className="text-[10px] font-black uppercase text-slate-600 tracking-[0.3em] mb-3">Global Uptime</p>
                 <p className="text-5xl font-black text-white font-outfit">99.9<span className="text-slate-700">9</span>%</p>
               </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { 
                title: "Neuro-Security", 
                desc: "Contextual AI analysis detects raids and token-logging attempts in real-time.", 
                icon: ShieldCheck,
                color: "bg-red-500/10 border-red-500/20 text-red-500"
              },
              { 
                title: "Edge Dispatch", 
                desc: "Distributed command execution ensuring your commands work everywhere, instantly.", 
                icon: Zap,
                color: "bg-orange-500/10 border-orange-500/20 text-orange-500"
              },
              { 
                title: "Leveling Engine", 
                desc: "Premium rendered rewards with 4K rank card generation and multi-role hierarchies.", 
                icon: BarChart4,
                color: "bg-red-600/10 border-red-600/20 text-red-600"
              },
              { 
                title: "Threaded Support", 
                desc: "High-volume ticket systems with enterprise encryption and lifetime transcripts.", 
                icon: MessageSquare,
                color: "bg-slate-500/10 border-slate-500/20 text-slate-400"
              },
              { 
                title: "Real-time Flux", 
                desc: "Watch server events live with zero-latency WebSocket data streaming.", 
                icon: History,
                color: "bg-red-800/10 border-red-800/20 text-red-700"
              },
              { 
                title: "Cloud Integrity", 
                desc: "Encrypted backups of all server configurations stored in off-site neural vaults.", 
                icon: Layers,
                color: "bg-white/10 border-white/20 text-white"
              }
            ].map((feature, i) => (
              <div key={i} className="group glass border-white/5 p-12 rounded-[50px] hover:border-red-500/30 transition-all duration-700 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-12 opacity-0 group-hover:opacity-5 scale-50 group-hover:scale-110 transition-all duration-1000">
                  <feature.icon className="h-64 w-64 text-white" />
                </div>
                <div className={cn("h-20 w-20 rounded-3xl flex items-center justify-center mb-10 border transition-all duration-700 group-hover:scale-110 group-hover:rotate-6 shadow-2xl shadow-black/40", feature.color)}>
                  <feature.icon className="h-10 w-10 shadow-lg" />
                </div>
                <h3 className="text-3xl font-bold text-white mb-6 tracking-tight font-outfit relative z-10">{feature.title}</h3>
                <p className="text-slate-500 leading-relaxed font-bold relative z-10 group-hover:text-slate-400 transition-colors uppercase text-[10px] tracking-[0.2em]">{feature.desc}</p>
                <div className="mt-8 h-[2px] w-0 bg-red-500 group-hover:w-full transition-all duration-700" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-48 px-6 bg-white/[0.01]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
           <div className="space-y-12">
              <div className="inline-flex px-4 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-black uppercase tracking-[0.3em]">
                 The Stack
              </div>
              <h2 className="text-6xl md:text-7xl font-bold text-white tracking-tighter font-outfit uppercase">Neural Core <br /><span className="text-slate-600 italic">Technology.</span></h2>
              <p className="text-xl text-slate-500 leading-relaxed font-medium">
                Our proprietary engine is built on a custom Rust-based microkernel that handles millions of events with a footprint smaller than a typical Discord bot.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 pt-8">
                 {[
                   { icon: Terminal, title: "Custom DSL", desc: "Write advanced logic with our intuitive ZyroX scripting language." },
                   { icon: Cpu, title: "FPGA Ready", desc: "Hardware-accelerated pattern matching for instant response." },
                   { icon: Lock, title: "Zero Trust", desc: "Every command execution is sandboxed and cryptographically verified." },
                   { icon: Radio, title: "Low Entropy", desc: "Optimized for minimal CPU jitter and maximum reliability." }
                 ].map((item, i) => (
                   <div key={i} className="space-y-4 p-6 rounded-[30px] border border-white/[0.03] hover:bg-white/[0.02] transition-colors">
                      <item.icon className="h-6 w-6 text-red-500" />
                      <h4 className="text-lg font-bold text-white font-outfit uppercase tracking-tight">{item.title}</h4>
                      <p className="text-sm text-slate-600 font-bold leading-relaxed">{item.desc}</p>
                   </div>
                 ))}
              </div>
           </div>
           <div className="relative aspect-square flex items-center justify-center group">
              <div className="absolute inset-0 bg-red-500/5 blur-[120px] rounded-full animate-pulse" />
              <div className="h-[80%] w-[80%] border-2 border-white/[0.05] rounded-full animate-[spin_60s_linear_infinite] flex items-center justify-center relative">
                 <div className="absolute top-0 left-1/2 -translate-x-1/2 h-4 w-4 rounded-full bg-red-500 shadow-[0_0_20px_rgba(239,68,68,0.5)]" />
                 <div className="h-[70%] w-[70%] border border-white/[0.05] rounded-full animate-[spin_40s_linear_infinite_reverse] flex items-center justify-center">
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-3 w-3 rounded-full bg-white/20 shadow-[0_0_20px_rgba(255,255,255,0.2)]" />
                    <div className="h-[60%] w-[60%] border border-white/[0.05] rounded-full animate-[spin_20s_linear_infinite] flex items-center justify-center">
                       <Bot className="h-20 w-20 text-red-500/40 group-hover:text-red-500 transition-all duration-700 group-hover:scale-125" />
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* Modules Grid */}
      <section id="modules" className="py-48 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-32 space-y-6">
             <h2 className="text-6xl md:text-8xl font-bold text-white tracking-tighter font-outfit uppercase">The Matrix <br /><span className="bg-gradient-to-r from-red-600 to-red-400 bg-clip-text text-transparent italic">Complete.</span></h2>
             <p className="text-2xl text-slate-500 max-w-3xl mx-auto font-medium lowercase">Every module you need. Redefined for the modern era.</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {[
              { name: "Anti-Nuke", desc: "Absolute server lockdown.", icon: ShieldAlert },
              { name: "Verification", desc: "Bot-free onboarding.", icon: CheckCircle2 },
              { name: "Welcome", desc: "Cinematic entries.", icon: Sparkles },
              { name: "Vanity Roles", desc: "Custom server identity.", icon: Gamepad2 },
              { name: "Auto Role", desc: "Instant rank assignment.", icon: User },
              { name: "Join to Create", desc: "Self-service voice channels.", icon: Music4 },
              { name: "Tracking", desc: "Predictive user metrics.", icon: Activity },
              { name: "Invites", desc: "Advanced growth tracking.", icon: Globe },
              { name: "Custom Roles", desc: "User-defined permissions.", icon: Lock },
              { name: "Reaction Roles", desc: "Interactive role menus.", icon: Layers },
              { name: "Tickets", desc: "Support at lightspeed.", icon: MessageSquare },
              { name: "Join DM", desc: "Personalized welcomes.", icon: MessageSquare }
            ].map((mod, i) => (
              <div key={i} className="group p-8 rounded-[40px] bg-white/[0.01] border border-white/[0.03] hover:bg-red-500/[0.02] hover:border-red-500/20 transition-all duration-500">
                 <div className="h-14 w-14 rounded-2xl bg-white/[0.03] flex items-center justify-center mb-6 group-hover:bg-red-500/10 transition-colors">
                    <mod.icon className="h-6 w-6 text-slate-600 group-hover:text-red-500 transition-colors" />
                 </div>
                 <h4 className="text-xl font-bold text-white font-outfit mb-2 tracking-tight">{mod.name}</h4>
                 <p className="text-xs text-slate-600 font-bold uppercase tracking-widest">{mod.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Network / Global Section */}
      <section id="network" className="py-48 px-6 bg-red-600/[0.01] relative overflow-hidden">
        <div className="max-w-7xl mx-auto relative z-10">
           <div className="flex flex-col lg:flex-row items-center gap-24">
              <div className="flex-1 space-y-12">
                 <h2 className="text-6xl md:text-8xl font-bold text-white tracking-tighter font-outfit uppercase">Global <br /><span className="text-red-500">Reach.</span></h2>
                  <p className="text-2xl text-slate-500 leading-relaxed font-medium">
                    Powering servers with over 12 million combined users. Our network spans every continent, bringing your community closer together.
                  </p>
                 <div className="space-y-8">
                    {[
                      { stat: "12M+", label: "Users Protected" },
                      { stat: "24", label: "Edge Clusters" },
                      { stat: "5.2K", label: "Verified Communities" }
                    ].map((item, i) => (
                      <div key={i} className="flex items-center gap-8">
                         <div className="text-5xl font-black text-white font-outfit">{item.stat}</div>
                         <div className="h-[1px] flex-1 bg-white/5" />
                         <div className="text-[11px] font-black uppercase text-red-500 tracking-[0.3em]">{item.label}</div>
                      </div>
                    ))}
                 </div>
              </div>
              <div className="flex-1 relative group">
                 <div className="absolute inset-0 bg-red-500/10 blur-[150px] opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
                 <div className="aspect-square bg-[#020617] border border-white/[0.05] rounded-[60px] p-12 relative overflow-hidden flex items-center justify-center">
                    <Globe className="h-64 w-64 text-red-500/10 animate-pulse" />
                    <div className="absolute inset-0 flex items-center justify-center">
                       <div className="h-32 w-32 bg-red-500/20 blur-[60px] rounded-full" />
                    </div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 space-y-12">
                       <Bot className="h-20 w-20 text-red-500 shadow-[0_0_50px_rgba(239,68,68,0.5)] bg-[#020617] rounded-3xl p-4 border border-red-500/50" />
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-48 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-24">
             <h2 className="text-5xl md:text-6xl font-black text-white font-outfit tracking-tighter uppercase mb-6">Knowledge Base</h2>
             <p className="text-slate-600 font-bold uppercase tracking-widest text-xs">Frequently Asked Questions</p>
          </div>
          <div className="space-y-6">
            {[
              { q: "Is the ZyroX Engine free to use?", a: "The core engine is 100% free for all communities. We offer premium clusters for ultra-high-scale enterprise servers." },
              { q: "How secure is my server data?", a: "Every byte of configuration data is AES-256 encrypted at rest. We never store personal user data beyond Discord's standard requirements." },
              { q: "Can I migrate from other bots?", a: "Yes, our Migration Matrix tool allows you to import leveling and configuration data from most popular bots in minutes." },
              { q: "What is the 'Neural Core'?", a: "It's our advanced event-processing architecture that uses predictive analysis to moderate raids before they escalate." }
            ].map((item, i) => (
              <div key={i} className="p-10 rounded-[40px] border border-white/[0.03] hover:border-white/10 transition-all bg-white/[0.01] group">
                 <h4 className="text-xl font-bold text-white mb-6 font-outfit uppercase tracking-tight flex items-center gap-4">
                    <div className="h-2 w-2 rounded-full bg-red-500 opacity-20 group-hover:opacity-100 transition-all" />
                    {item.q}
                 </h4>
                 <p className="text-slate-500 font-bold leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-48 px-6">
        <div className="max-w-6xl mx-auto relative rounded-[80px] p-24 md:p-32 overflow-hidden bg-gradient-to-br from-red-600 to-red-900 text-center shadow-[0_40px_100px_rgba(0,0,0,0.6)]">
           <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
           <div className="relative z-10">
              <h2 className="text-7xl md:text-[9rem] font-bold text-white tracking-tighter font-outfit mb-12 uppercase leading-[0.8] italic">Ready to <br />Evolve?</h2>
              <p className="text-2xl text-white/70 max-w-3xl mx-auto mb-20 font-medium">Join 5,000+ communities scaling their automation with the ZyroX Engine. Setup takes less than 30 seconds.</p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-8 tracking-widest uppercase text-xs font-black">
                <Button 
                  onClick={() => signIn('discord', { callbackUrl: '/dashboard' })}
                  className="w-full sm:w-auto rounded-3xl px-16 py-10 bg-white text-black hover:bg-slate-100 border-none shadow-[0_20px_50px_rgba(0,0,0,0.4)] font-black text-lg transition-transform hover:scale-105 active:scale-95"
                >
                  Get Started Free
                </Button>
                <div className="flex items-center gap-3 text-white">
                   <div className="h-3 w-3 rounded-full bg-white animate-pulse" />
                   Neural Uplink: Stable
                </div>
              </div>
           </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-32 border-t border-white/[0.03] bg-[#020617] relative z-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-20 mb-32">
            <div className="col-span-1 md:col-span-2 space-y-12">
              <div className="flex items-center gap-4 group">
                <span className="text-3xl font-bold text-white font-outfit uppercase tracking-tighter">{process.env.NEXT_PUBLIC_BRAND_NAME || "ZyroX"} Engine</span>
              </div>
              <p className="text-slate-600 max-w-sm font-bold leading-relaxed uppercase text-xs tracking-widest">
                The high-performance Discord engine for communities that demand excellence. Open-source, secure, and infinitely scalable.
              </p>
            </div>
            <div className="space-y-8">
               <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-white opacity-40">System</h4>
               <ul className="space-y-5 text-[11px] font-black uppercase tracking-widest text-slate-500">
                  <li><Link href="#" className="hover:text-red-500 transition-colors">GitHub Repository</Link></li>
                  <li><Link href="/docs" className="hover:text-red-500 transition-colors">Documentation</Link></li>
                  <li><Link href="#" className="hover:text-red-500 transition-colors">API References</Link></li>
               </ul>
            </div>
            <div className="space-y-8">
               <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-white opacity-40">Identity</h4>
               <ul className="space-y-5 text-[11px] font-black uppercase tracking-widest text-slate-500">
                  <li><Link href="/privacy" className="hover:text-red-500 transition-colors">Privacy Shield</Link></li>
                  <li><Link href="/terms" className="hover:text-red-500 transition-colors">Terms of Service</Link></li>
                  <li><Link href="#" className="hover:text-red-500 transition-colors">Discord Server</Link></li>
               </ul>
            </div>
          </div>
          <div className="pt-12 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-6 opacity-40">
            <p className="text-slate-700 text-[10px] font-black uppercase tracking-[0.4em]">
              © 2026 {process.env.NEXT_PUBLIC_BRAND_NAME || "ZyroX"} Development // Advanced Neural Infrastructure.
            </p>
            <div className="flex items-center gap-8">
               <div className="flex items-center gap-3 text-[10px] font-black text-red-500 uppercase tracking-[0.3em]">
                  <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                  All Nodes Operational
               </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
