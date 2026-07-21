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

"use client"

import * as React from "react"
import { ChevronDown, Check } from "lucide-react"
import { cn } from "@/lib/utils"

// Context for sub-components
const SelectContext = React.createContext<{
  value: string
  onValueChange: (value: string) => void
  isOpen: boolean
  setIsOpen: (open: boolean) => void
} | null>(null)

export interface SelectOption {
  value: string
  label: string
}

interface SelectProps {
  children?: React.ReactNode
  value: string
  onValueChange: (value: string) => void
  // Legacy props compatibility
  options?: SelectOption[]
  placeholder?: string
  className?: string
  disabled?: boolean
}

const Select = ({ children, value, onValueChange, options, placeholder, className, disabled }: SelectProps) => {
  const [isOpen, setIsOpen] = React.useState(false)
  const containerRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  // If options are provided, use the legacy rendering
  if (options) {
    const selectedOption = options.find((opt) => opt.value === value)
    return (
      <div className={cn("relative w-full", className)} ref={containerRef}>
        <button
          type="button"
          disabled={disabled}
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            "flex h-10 w-full items-center justify-between rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-2 text-sm transition-all focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:cursor-not-allowed disabled:opacity-50",
            isOpen && "ring-2 ring-primary/50 border-slate-700"
          )}
        >
          <span className={cn("truncate", !selectedOption && "text-slate-500")}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <ChevronDown className={cn("h-4 w-4 text-slate-500 transition-transform duration-200", isOpen && "rotate-180")} />
        </button>

        {isOpen && (
          <div className="absolute top-full z-50 mt-2 w-full overflow-hidden rounded-xl border border-slate-800 bg-[#141B2D] p-1 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <div className="max-h-60 overflow-y-auto overflow-x-hidden no-scrollbar">
              {options.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => {
                    onValueChange(option.value)
                    setIsOpen(false)
                  }}
                  className={cn(
                    "flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors hover:bg-slate-800",
                    value === option.value ? "bg-primary text-white" : "text-slate-300"
                  )}
                >
                  <span className="truncate">{option.label}</span>
                  {value === option.value && <Check className="h-4 w-4" />}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // Otherwise, use the sub-component pattern
  return (
    <SelectContext.Provider value={{ value, onValueChange, isOpen, setIsOpen }}>
      <div className={cn("relative w-full", className)} ref={containerRef}>
        {children}
      </div>
    </SelectContext.Provider>
  )
}

const SelectTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, children, ...props }, ref) => {
  const context = React.useContext(SelectContext)
  if (!context) return null

  return (
    <button
      ref={ref}
      type="button"
      onClick={() => context.setIsOpen(!context.isOpen)}
      className={cn(
        "flex h-10 w-full items-center justify-between rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-2 text-sm transition-all focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:cursor-not-allowed disabled:opacity-50",
        context.isOpen && "ring-2 ring-primary/50 border-slate-700",
        className
      )}
      {...props}
    >
      {children}
      <ChevronDown className={cn("h-4 w-4 text-slate-500 transition-transform duration-200", context.isOpen && "rotate-180")} />
    </button>
  )
})
SelectTrigger.displayName = "SelectTrigger"

const SelectValue = ({ placeholder, className }: { placeholder?: string, className?: string }) => {
  const context = React.useContext(SelectContext)
  if (!context) return null
  return <span className={cn("truncate", !context.value && "text-slate-500", className)}>{context.value || placeholder}</span>
}

const SelectContent = ({ children, className }: { children: React.ReactNode, className?: string }) => {
  const context = React.useContext(SelectContext)
  if (!context || !context.isOpen) return null

  return (
    <div className={cn("absolute top-full z-50 mt-2 w-full overflow-hidden rounded-xl border border-slate-800 bg-[#141B2D] p-1 shadow-2xl animate-in fade-in zoom-in-95 duration-200", className)}>
      <div className="max-h-60 overflow-y-auto overflow-x-hidden no-scrollbar">
        {children}
      </div>
    </div>
  )
}

const SelectItem = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { value: string }
>(({ className, children, value, ...props }, ref) => {
  const context = React.useContext(SelectContext)
  if (!context) return null

  const isSelected = context.value === value

  return (
    <button
      ref={ref}
      type="button"
      onClick={() => {
        context.onValueChange(value)
        context.setIsOpen(false)
      }}
      className={cn(
        "flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors hover:bg-slate-800",
        isSelected ? "bg-primary text-white" : "text-slate-300",
        className
      )}
      {...props}
    >
      <span className="truncate">{children}</span>
      {isSelected && <Check className="h-4 w-4" />}
    </button>
  )
})
SelectItem.displayName = "SelectItem"

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem }
