"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, setTheme, resolvedTheme } = useTheme()

  return (
    <button
      type="button"
      tabIndex={0}
      role="switch"
      aria-label="Alternar tema"
      onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
      className={cn(
        "inline-flex items-center justify-center rounded-md p-2 transition-colors hover:bg-accent hover:text-accent-foreground",
        className
      )}
    >
      <Sun className="h-4 w-4 scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
      <Moon className="absolute h-4 w-4 scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
    </button>
  )
}
