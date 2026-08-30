"use client";

import React, { useEffect } from "react";
import { RefreshCw, Home } from "lucide-react";
import { inter, sora } from "@/constants/fonts-config";
import "./globals.css";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Critical Application Error:", error);
  }, [error]);

  return (
    <html
      lang="en"
      className={`${sora.variable} ${inter.variable} h-full antialiased`}
    >
      <body className="min-h-full flex items-center justify-center bg-background text-foreground px-4 selection:bg-primary/20 selection:text-primary">
        <main className="flex flex-col items-center justify-center text-center">
          <div className="flex items-center gap-4 text-left">
            <h1 className="text-3xl font-bold font-heading text-destructive tracking-tight">
              500
            </h1>
            <div className="h-8 w-px bg-border" />
            <div className="space-y-0.5">
              <p className="text-sm font-semibold font-heading text-foreground">
                Something went wrong
              </p>
              <p className="text-xs text-muted-foreground">
                A critical platform error occurred.
              </p>
            </div>
          </div>

          <div className="mt-6 flex items-center gap-3">
            <button
              type="button"
              onClick={() => reset()}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary hover:bg-primary-hover text-primary-foreground px-4 py-2 text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <RefreshCw className="size-3.5" />
              Try Again
            </button>
            <button
              type="button"
              onClick={() => (window.location.href = "/")}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-card hover:bg-muted text-foreground px-4 py-2 text-xs font-medium shadow-xs transition-colors cursor-pointer"
            >
              <Home className="size-3.5" />
              Home
            </button>
          </div>
        </main>
      </body>
    </html>
  );
}
