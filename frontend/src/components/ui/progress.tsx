"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface ProgressProps extends React.ComponentProps<"div"> {
  value?: number
  indicatorClassName?: string
}

function Progress({
  className,
  value = 0,
  indicatorClassName,
  ...props
}: ProgressProps) {
  const safeValue = Math.min(100, Math.max(0, value ?? 0))

  return (
    <div
      data-slot="progress"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={safeValue}
      className={cn(
        "relative h-2 w-full overflow-hidden rounded-full bg-muted border border-border/40",
        className
      )}
      {...props}
    >
      <div
        data-slot="progress-indicator"
        className={cn(
          "h-full w-full flex-1 bg-primary transition-all duration-500 ease-in-out",
          indicatorClassName
        )}
        style={{ transform: `translateX(-${100 - safeValue}%)` }}
      />
    </div>
  )
}

export { Progress }
