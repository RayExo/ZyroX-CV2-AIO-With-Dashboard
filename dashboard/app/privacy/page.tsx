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
import { Bot, ChevronLeft, ShieldCheck, Lock, Eye, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 font-sans">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-5%] w-[40%] h-[40%] bg-red-500/[0.03] blur-[120px] rounded-full" />
      </div>

      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.03] bg-[#020617]/80 backdrop-blur-3xl px-6 h-20 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-4 group">
          <div className="h-9 w-9 rounded-xl bg-red-600 flex items-center justify-center mr-4">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white font-outfit uppercase tracking-tighter">ZyroX Engine</span>
        </Link>
        <Link href="/">
          <Button variant="ghost" className="text-slate-400 hover:text-white gap-2">
            <ChevronLeft className="h-4 w-4" />
            Back to Home
          </Button>
        </Link>
      </nav>

      <main className="relative z-10 pt-40 pb-32 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] font-black uppercase tracking-widest mb-8">
            <ShieldCheck className="h-3 w-3" />
            Privacy Shield v2.0
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white font-outfit tracking-tighter uppercase mb-12 italic">
            Privacy <span className="text-red-500 not-italic">Policy.</span>
          </h1>

          <div className="glass border-white/5 rounded-[40px] p-10 md:p-16 space-y-12">
            <section className="space-y-6">
              <div className="flex items-center gap-4 text-white">
                <div className="h-10 w-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-red-500">
                   <Eye className="h-5 w-5" />
                </div>
                <h2 className="text-2xl font-bold font-outfit uppercase tracking-tight">Data Collection</h2>
              </div>
              <p className="text-slate-400 leading-relaxed font-medium">
                The ZyroX Engine collects only the minimum necessary data to function within Discord. This includes your Discord User ID, Server (Guild) ID, and configuration settings provided during setup. We do not store message content unless explicitly configured for logging purposes by server administrators.
              </p>
            </section>

            <section className="space-y-6">
              <div className="flex items-center gap-4 text-white">
                <div className="h-10 w-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-red-500">
                   <Lock className="h-5 w-5" />
                </div>
                <h2 className="text-2xl font-bold font-outfit uppercase tracking-tight">Data Integrity</h2>
              </div>
              <p className="text-slate-400 leading-relaxed font-medium">
                All configuration data is AES-256 encrypted at rest. Our neural vaults are distributed across global edge nodes, ensuring that your server settings are both secure and instantly available. We never sell or distribute your data to third parties.
              </p>
            </section>

            <section className="space-y-6">
              <div className="flex items-center gap-4 text-white">
                <div className="h-10 w-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-red-500">
                   <FileText className="h-5 w-5" />
                </div>
                <h2 className="text-2xl font-bold font-outfit uppercase tracking-tight">User Rights</h2>
              </div>
              <p className="text-slate-400 leading-relaxed font-medium">
                You have the right to request a full dump of your data or immediate deletion of all configurations associated with your Discord account or guild. These requests can be initialized through our support matrix or directly within the dashboard settings.
              </p>
            </section>

            <div className="pt-12 border-t border-white/5">
              <p className="text-[10px] font-black uppercase text-slate-600 tracking-[0.4em]">
                Last Modified: March 2026 // Neural Jurisdiction: Global Edge Network
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
