import React from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <main className="min-h-screen w-full flex flex-col items-center justify-center bg-background text-foreground px-4 selection:bg-primary/20 selection:text-primary">
      <div className="flex items-center gap-4 text-left">
        <h1 className="text-3xl font-bold font-heading text-primary tracking-tight">
          404
        </h1>
        <div className="h-8 w-px bg-border" />
        <div className="space-y-0.5">
          <p className="text-sm font-semibold font-heading text-foreground">
            Page not found
          </p>
          <p className="text-xs text-muted-foreground">
            This requested page could not be located.
          </p>
        </div>
      </div>

      <div className="mt-6">
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary hover:bg-primary-hover text-primary-foreground px-4 py-2 text-xs font-semibold shadow-xs transition-colors cursor-pointer"
        >
          <ArrowLeft className="size-3.5" />
          Return to Dashboard
        </Link>
      </div>
    </main>
  );
}
