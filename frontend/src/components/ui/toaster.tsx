"use client"

import { Toaster as HotToaster } from "react-hot-toast"

export const Toaster = () => {
  return (
    <HotToaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: "var(--card)",
          color: "var(--foreground)",
          border: "1px solid var(--border)",
          borderRadius: "0.75rem",
          boxShadow:
            "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
          fontSize: "0.875rem",
          padding: "10px 14px",
        },
        success: {
          iconTheme: {
            primary: "var(--primary)",
            secondary: "var(--primary-foreground)",
          },
        },
        error: {
          iconTheme: {
            primary: "var(--destructive)",
            secondary: "#ffffff",
          },
        },
      }}
    />
  )
}
