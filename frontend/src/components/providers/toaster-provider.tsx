"use client"

import { Toaster } from "sonner"

export function ToasterProvider() {
  return (
    <Toaster
      position="bottom-right"
      theme="system"
      richColors
      closeButton
      duration={4000}
    />
  )
}
