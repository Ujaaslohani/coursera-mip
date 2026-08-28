import React from "react";
import { CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface StatusBannerProps {
  type: "success" | "error";
  message: string;
  className?: string;
}

export function StatusBanner({ type, message, className }: StatusBannerProps) {
  const isSuccess = type === "success";
  return (
    <div
      role="alert"
      className={cn(
        "flex items-start gap-3 p-4 rounded-lg border text-sm",
        isSuccess
          ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400"
          : "bg-destructive/10 border-destructive/30 text-destructive",
        className
      )}
    >
      {isSuccess ? (
        <CheckCircle2 className="h-5 w-5 shrink-0 mt-0.5" />
      ) : (
        <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
      )}
      <div>{message}</div>
    </div>
  );
}
