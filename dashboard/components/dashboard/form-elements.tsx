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

import React from "react";
import { Switch } from "@/components/ui/switch";
import { Select, SelectOption } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

// --- ToggleSwitch ---
interface ToggleSwitchProps {
  label?: string;
  description?: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
}

export const ToggleSwitch = ({ 
  label, 
  description, 
  checked, 
  onCheckedChange, 
  disabled,
  className 
}: ToggleSwitchProps) => (
  <div className={cn("flex items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/30 border border-slate-800", className)}>
    {(label || description) && (
      <div className="flex flex-col">
        {label && <span className="text-sm font-bold text-slate-200">{label}</span>}
        {description && <span className="text-[11px] text-slate-500 font-medium italic mt-0.5">{description}</span>}
      </div>
    )}
    <Switch checked={checked} onCheckedChange={onCheckedChange} disabled={disabled} />
  </div>
);

// --- DropdownSelect ---
interface DropdownSelectProps {
  label?: string;
  value: string;
  onValueChange: (value: string) => void;
  options: SelectOption[];
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export const DropdownSelect = ({ 
  label, 
  value, 
  onValueChange, 
  options, 
  placeholder, 
  disabled,
  className 
}: DropdownSelectProps) => (
  <div className={cn("space-y-2", className)}>
    {label && <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">{label}</label>}
    <Select 
      value={value} 
      onValueChange={onValueChange} 
      options={options} 
      placeholder={placeholder} 
      disabled={disabled}
    />
  </div>
);

// --- FormInput ---
interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  icon?: React.ElementType;
}

export const FormInput = ({ label, icon: Icon, className, ...props }: FormInputProps) => (
  <div className="space-y-2 w-full">
    {label && <label className="text-xs font-black uppercase text-slate-500 tracking-widest pl-1">{label}</label>}
    <div className="relative group">
      {Icon && (
        <Icon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 group-focus-within:text-primary transition-colors" />
      )}
      <Input 
        className={cn(
          "bg-slate-900/50 border-slate-800 rounded-xl h-12 focus:ring-primary/20",
          Icon && "pl-12",
          className
        )} 
        {...props} 
      />
    </div>
  </div>
);
