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

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Server, ShieldCheck, Ticket, BarChart4, FileText, Settings,
  Menu, X, Bell, User, Search, ChevronRight, Star, Sparkles, LogOut,
  LifeBuoy, ChevronDown, Bot, Shield
} from "lucide-react";
import { useSession, signIn, signOut } from "next-auth/react";
import { cn, isAdmin } from "@/lib/utils";
import { api } from "@/lib/api";
import { AdminConfig } from "@/types/api";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const pathname = usePathname();
  const { data: session, status } = useSession();
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [globalNotification, setGlobalNotification] = useState<string | null>(null);
  
  const bellRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  // Close dropdowns on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;
      if (bellRef.current && !bellRef.current.contains(target)) {
        setIsNotificationsOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(target)) {
        setIsProfileOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Auto-close sidebar on mobile when navigating
  React.useEffect(() => {
    setIsSidebarOpen(false);
    setIsProfileOpen(false);
  }, [pathname]);

  React.useEffect(() => {
    if (status === "unauthenticated") {
      signIn("discord");
    }
    
    // Fetch global notification
    const fetchNotification = async () => {
      try {
        const config = await api.getAdminConfig();
        setGlobalNotification(config.global_notification);
      } catch (err) {
        console.error("Failed to fetch notifications:", err);
      }
    };
    fetchNotification();
  }, [status]);

  if (status === "loading" || status === "unauthenticated") {
    return (
      <div className="min-h-screen bg-[#0f172a] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
            <span className="font-black text-white italic text-xl">{process.env.NEXT_PUBLIC_BRAND_NAME_WORD || "ZX"}</span>
          </div>
          <p className="text-slate-400 font-bold tracking-widest uppercase text-xs">
            Authenticating...
          </p>
        </div>
      </div>
    );
  }

  const match = pathname.match(/\/dashboard\/guild\/([^\/]+)/);
  const currentGuildId = match ? match[1] : null;

  // Base sidebar items – will be filtered if we are inside a guild
  const allSidebarItems = currentGuildId
    ? [
        { name: "Overview", href: `/dashboard/guild/${currentGuildId}`, icon: LayoutDashboard },
        {
          name: "Security",
          items: [
            { name: "Anti-Nuke", href: `/dashboard/guild/${currentGuildId}/antinuke`, icon: ShieldCheck },
            { name: "Automod", href: `/dashboard/guild/${currentGuildId}/automod`, icon: ShieldCheck },
            { name: "Verification", href: `/dashboard/guild/${currentGuildId}/verification`, icon: User },
          ],
        },
        {
          name: "Engagement",
          items: [
            { name: "Welcome", href: `/dashboard/guild/${currentGuildId}/welcome`, icon: Bell },
            { name: "Leveling", href: `/dashboard/guild/${currentGuildId}/leveling`, icon: BarChart4 },
            { name: "Vanity Roles", href: `/dashboard/guild/${currentGuildId}/vanityroles`, icon: Star },
            { name: "Auto Role", href: `/dashboard/guild/${currentGuildId}/autorole`, icon: Search },
            { name: "Auto React", href: `/dashboard/guild/${currentGuildId}/autoreact`, icon: Settings },
            { name: "Reaction Roles", href: `/dashboard/guild/${currentGuildId}/reactionroles`, icon: Search },
            { name: "Join DM", href: `/dashboard/guild/${currentGuildId}/joindm`, icon: User },
            { name: "Invites", href: `/dashboard/guild/${currentGuildId}/invites`, icon: Search },
            { name: "Tracking", href: `/dashboard/guild/${currentGuildId}/tracking`, icon: BarChart4 },
          ],
        },
        {
          name: "Utility",
          items: [
            { name: "Tickets", href: `/dashboard/guild/${currentGuildId}/tickets`, icon: Ticket },
            { name: "Join to Create", href: `/dashboard/guild/${currentGuildId}/j2c`, icon: Menu },
            { name: "Custom Roles", href: `/dashboard/guild/${currentGuildId}/customroles`, icon: ShieldCheck },
            { name: "Voice Role", href: `/dashboard/guild/${currentGuildId}/invcrole`, icon: Settings },
          ],
        },
        { name: "Settings", href: `/dashboard/guild/${currentGuildId}/settings`, icon: Settings },
        { name: "Back to Servers", href: "/dashboard/guilds", icon: Server },
      ]
    : [
        { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
        { name: "Servers", href: "/dashboard/guilds", icon: Server },
        ...(isAdmin(session?.user?.id) 
            ? [{ name: "Admin Panel", href: "/dashboard/admin", icon: Shield }] 
            : []),
      ];

  // Separate the "Back to Servers" item when inside a guild
  let mainSidebarItems = allSidebarItems;
  let backLinkItem: any = null;

  if (currentGuildId) {
    mainSidebarItems = allSidebarItems.filter(
      (item) => !(item.name === "Back to Servers")
    );
    backLinkItem = allSidebarItems.find((item) => item.name === "Back to Servers");
  }

  const BackLinkIcon = backLinkItem?.icon || Server;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200">
      {/* Liquid Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-red-500/5 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[10%] left-[-5%] w-[30%] h-[30%] bg-indigo-500/5 blur-[100px] rounded-full animate-pulse [animation-delay:2s]" />
      </div>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar - now using flex column */}
      <aside
        className={cn(
          "fixed left-4 top-4 bottom-4 z-50 w-64 transform transition-all duration-500 ease-in-out lg:translate-x-0 glass border border-white/10 rounded-[2.5rem] shadow-2xl shadow-black/40 overflow-hidden flex flex-col",
          isSidebarOpen ? "translate-x-0" : "-translate-x-[110%]"
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center px-6 mt-4 flex-shrink-0">
          <div className="flex items-center gap-3 group">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-red-500 to-red-800 flex items-center justify-center shadow-lg shadow-red-500/20 group-hover:scale-110 transition-transform border border-white/10">
              <Bot className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-lg font-bold tracking-tight text-white font-outfit leading-none">
                {process.env.NEXT_PUBLIC_BRAND_NAME || "ZyroX"}
              </h1>
              <span className="text-[9px] font-black uppercase tracking-[0.2em] text-red-500/80 mt-1">
                Dashboard
              </span>
            </div>
          </div>
          <button
            className="ml-auto p-2 lg:hidden text-slate-400 hover:text-white"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Navigation */}
        <nav className="mt-8 px-4 space-y-6 overflow-y-auto flex-1 no-scrollbar relative z-10 pb-3">
          {mainSidebarItems.map((item: any) => {
            if (item.items) {
              return (
                <div key={item.name} className="space-y-2">
                  <p className="px-4 text-[10px] font-black uppercase tracking-[0.3em] text-slate-600 mb-3">
                    {item.name}
                  </p>
                  <div className="space-y-1">
                    {item.items.map((subItem: any) => {
                      const isActive = pathname === subItem.href;
                      return (
                        <Link
                          key={subItem.name}
                          href={subItem.href}
                          className={cn(
                            "flex items-center gap-3 px-4 py-2.5 rounded-xl transition-all duration-300 group text-[13px] font-bold",
                            isActive
                              ? "bg-red-500/10 text-red-500 border border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.1)]"
                              : "text-slate-400 hover:bg-white/[0.03] hover:text-slate-200"
                          )}
                        >
                          <subItem.icon
                            className={cn(
                              "h-4 w-4 transition-all duration-300",
                              isActive
                                ? "text-red-500 scale-110"
                                : "text-slate-600 group-hover:text-slate-400"
                            )}
                          />
                          {subItem.name}
                          {isActive && (
                            <div className="ml-auto w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
                          )}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              );
            }

            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group text-[14px] font-bold",
                  isActive
                    ? "bg-red-500/10 text-red-500 border border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.1)]"
                    : "text-slate-400 hover:bg-white/[0.03] hover:text-slate-200"
                )}
              >
                <item.icon
                  className={cn(
                    "h-5 w-5 transition-all duration-300",
                    isActive ? "text-red-500 scale-110" : "text-slate-600 group-hover:text-slate-400"
                  )}
                />
                {item.name}
                {isActive ? (
                  <ChevronRight className="ml-auto h-4 w-4 text-red-500" />
                ) : (
                  <ChevronRight className="ml-auto h-4 w-4 opacity-0 group-hover:opacity-30 transition-opacity" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Fixed "Back to Servers" link (only shown inside a guild) */}
        {backLinkItem && (
          <div className="px-4 py-2 flex-shrink-0">
            <div className="h-px bg-white/5 w-3/4 mx-auto rounded-full mb-2" />
            <Link
              href={backLinkItem.href || "/dashboard/guilds"}
              className={cn(
                "flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-300 group text-[14px] font-bold",
                pathname === backLinkItem.href
                  ? "bg-red-500/10 text-red-500 border border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.1)]"
                  : "text-slate-400 hover:bg-white/[0.03] hover:text-slate-200"
              )}
            >
              <BackLinkIcon
                className={cn(
                  "h-5 w-5 transition-all duration-300",
                  pathname === backLinkItem.href
                    ? "text-red-500 scale-110"
                    : "text-slate-600 group-hover:text-slate-400"
                )}
              />
              {backLinkItem.name}
              {pathname === backLinkItem.href ? (
                <ChevronRight className="ml-auto h-4 w-4 text-red-500" />
              ) : (
                <ChevronRight className="ml-auto h-4 w-4 opacity-0 group-hover:opacity-30 transition-opacity" />
              )}
            </Link>
          </div>
        )}

        {/* User Profile - now a normal flex child, no absolute positioning */}
        <div className="flex-shrink-0 p-4 border-t border-white/5 glass-red bg-red-500/[0.02]">
          <div className="flex items-center gap-3 p-2 bg-white/[0.02] rounded-2xl border border-white/[0.05]">
            <div className="h-10 w-10 rounded-full bg-red-500/10 flex items-center justify-center ring-1 ring-white/10 overflow-hidden border border-red-500/20">
              {session?.user?.image ? (
                <img
                  src={session.user.image}
                  alt="User Avatar"
                  className="h-full w-full object-cover opacity-80"
                />
              ) : (
                <User className="h-6 w-6 text-red-500/50" />
              )}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-bold text-white truncate font-outfit">
                {session?.user?.name || "Administrator"}
              </p>
              <p className="text-[10px] font-black uppercase text-red-500/60 truncate tracking-widest">
                User
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area (unchanged) */}
      <div className="lg:pl-72 flex flex-col min-h-screen relative z-10">
        {/* Top Navbar (unchanged) */}
        <header className="h-20 sticky top-4 z-30 mx-4 lg:mx-10 flex items-center justify-between border border-white/10 glass bg-white/[0.01] backdrop-blur-3xl px-8 rounded-[2rem] shadow-xl shadow-black/20 mb-6 mt-4">
          <button
            className="p-2 lg:hidden text-slate-400 hover:bg-white/5 rounded-xl transition-colors"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="hidden md:flex items-center w-96 max-w-full relative group">
            <Search className="absolute left-4 h-4 w-4 text-slate-500 group-focus-within:text-red-500 transition-colors" />
            <input
              type="text"
              placeholder="Query neural network..."
              className="w-full bg-white/[0.03] border border-white/5 rounded-2xl py-2.5 pl-12 pr-4 text-xs font-bold text-slate-300 focus:outline-none focus:ring-1 focus:ring-red-500/30 focus:bg-white/[0.05] transition-all placeholder:text-slate-600"
            />
          </div>

          <div className="flex items-center gap-6">
            <div className="relative" ref={bellRef}>
              <button 
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                className="relative p-2.5 text-slate-400 hover:bg-white/5 hover:text-white rounded-xl transition-all group"
              >
                <Bell className="h-5 w-5" />
                {globalNotification && (
                  <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-red-500 border-2 border-[#020617] shadow-[0_0_10px_rgba(239,68,68,0.5)]"></span>
                )}
              </button>

              {isNotificationsOpen && (
                <div className="absolute right-0 mt-3 w-80 bg-[#0a0f1e]/90 backdrop-blur-3xl border border-white/5 rounded-[24px] shadow-[0_20px_50px_rgba(0,0,0,0.5)] p-4 z-20 animate-in fade-in zoom-in-95 duration-300 origin-top-right">
                    <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
                      <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Broadcast Metrics</p>
                      <button 
                        onClick={() => setGlobalNotification(null)}
                        className="text-[10px] font-bold text-red-500/60 hover:text-red-500 transition-colors uppercase"
                      >
                        Clear
                      </button>
                    </div>
                    
                    {globalNotification ? (
                      <div className="bg-red-500/5 border border-red-500/10 rounded-2xl p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkles className="h-3 w-3 text-red-500" />
                          <span className="text-[10px] font-black uppercase text-red-500 tracking-widest">System Broadcast</span>
                        </div>
                        <p className="text-xs font-medium text-slate-300 leading-relaxed">
                          {globalNotification}
                        </p>
                      </div>
                    ) : (
                      <div className="py-8 flex flex-col items-center justify-center text-center">
                        <div className="h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center mb-3">
                          <Bell className="h-5 w-5 text-slate-600" />
                        </div>
                        <p className="text-xs font-bold text-slate-500">No active broadcasts</p>
                        <p className="text-[10px] font-medium text-slate-600 mt-1 uppercase tracking-widest">Everything is operating normally</p>
                      </div>
                    )}
                  </div>
              )}
            </div>
            <div className="h-8 w-[1px] bg-white/5 hidden sm:block"></div>

            {/* Profile Dropdown (unchanged) */}
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center gap-3.5 p-1.5 rounded-2xl hover:bg-white/5 transition-all group border border-transparent hover:border-white/10"
              >
                <div className="h-9 w-9 rounded-full bg-red-500/10 flex items-center justify-center overflow-hidden border border-red-500/20 ring-2 ring-transparent group-hover:ring-red-500/30 transition-all">
                  {session?.user?.image ? (
                    <img src={session.user.image} alt="User Avatar" className="h-full w-full object-cover opacity-80" />
                  ) : (
                    <User className="h-5 w-5 text-red-500/50" />
                  )}
                </div>
                <div className="hidden sm:flex flex-col items-start leading-none gap-1">
                  <span className="text-xs font-bold text-slate-200 group-hover:text-white transition-colors">
                    {session?.user?.name?.split(' ')[0] || "Admin"}
                  </span>
                  <span className="text-[9px] font-black uppercase text-red-500/60 tracking-widest">Active</span>
                </div>
                <ChevronDown
                  className={cn("h-4 w-4 text-slate-600 transition-transform hidden sm:block", isProfileOpen && "rotate-180")}
                />
              </button>

              {isProfileOpen && (
                <div className="absolute right-0 mt-3 w-56 bg-[#0a0f1e]/90 backdrop-blur-3xl border border-white/5 rounded-[24px] shadow-[0_20px_50px_rgba(0,0,0,0.5)] p-2 z-20 animate-in fade-in zoom-in-95 duration-300 origin-top-right">
                    <div className="px-4 py-3 border-b border-white/5 mb-2">
                      <p className="text-[9px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">Authenticated As</p>
                      <p className="text-sm font-bold text-white truncate">{session?.user?.name || "Administrator"}</p>
                    </div>

                    <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-slate-400 hover:bg-white/5 hover:text-white transition-all group/item">
                      <LifeBuoy className="h-4 w-4 text-slate-600 group-hover/item:text-red-500 transition-colors" />
                      Support Matrix
                    </button>

                    <button
                      onClick={() => signOut({ callbackUrl: '/' })}
                      className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-black uppercase tracking-widest text-red-500/80 hover:bg-red-500/10 hover:text-red-500 transition-all group/item"
                    >
                      <LogOut className="h-4 w-4" />
                      Deauthorize
                    </button>
                  </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 p-6 lg:p-10 animate-in fade-in duration-700 relative z-10">
          <div className="max-w-[1600px] mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
}