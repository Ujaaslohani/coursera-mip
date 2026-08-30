import React from "react";
import { cn } from "@/lib/utils";

export interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "xs" | "sm" | "md" | "lg" | "xl" | number;
  center?: boolean;
}

const sizeMap: Record<string, string> = {
  xs: "text-[12px] w-[12px] h-[12px]",
  sm: "text-[14px] w-[14px] h-[14px]",
  md: "text-[16px] w-[16px] h-[16px]",
  lg: "text-[20px] w-[20px] h-[20px]",
  xl: "text-[28px] w-[28px] h-[28px]",
};

export const Spinner = ({
  className,
  size,
  center,
  style,
  ...props
}: SpinnerProps) => {
  const sizeClass = typeof size === "string" ? sizeMap[size] : undefined;
  const customStyle =
    typeof size === "number"
      ? { fontSize: `${size}px`, width: `${size}px`, height: `${size}px`, ...style }
      : style;

  return (
    <div
      className={cn(
        "spinner",
        center && "center",
        sizeClass,
        className
      )}
      style={customStyle}
      role="status"
      aria-label="Loading"
      {...props}
    >
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
      <div className="spinner-blade"></div>
    </div>
  );
};

export default Spinner;
