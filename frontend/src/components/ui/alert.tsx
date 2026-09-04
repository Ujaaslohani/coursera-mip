import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const alertVariants = cva(
  "relative w-full rounded-xl border px-4 py-3 text-sm grid has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] grid-cols-[0_1fr] has-[>svg]:gap-x-3 gap-y-0.5 items-start [&>svg]:size-4 [&>svg]:translate-y-0.5 [&>svg]:text-current transition-all",
  {
    variants: {
      variant: {
        default: "bg-card text-card-foreground border-border",
        info: "bg-primary/10 text-foreground border-primary/20 [&>svg]:text-primary",
        destructive:
          "text-destructive bg-destructive/10 border-destructive/20 [&>svg]:text-destructive *:[[data-slot=alert-description]]:text-destructive/90",
        success:
          "text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20 [&>svg]:text-emerald-600 dark:[&>svg]:text-emerald-400",
        warning:
          "text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/20 [&>svg]:text-amber-600 dark:[&>svg]:text-amber-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Alert({
  className,
  variant,
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof alertVariants>) {
  return (
    <div
      data-slot="alert"
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    />
  );
}

function AlertTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-title"
      className={cn("font-medium tracking-tight text-xs", className)}
      {...props}
    />
  );
}

function AlertDescription({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-description"
      className={cn("text-xs text-muted-foreground", className)}
      {...props}
    />
  );
}

export { Alert, AlertTitle, AlertDescription };
