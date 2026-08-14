import React, { useId } from "react";
import { cn } from "@/lib/utils";

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: React.ReactNode;
}

export function Checkbox({
  id,
  label,
  className,
  checked,
  onChange,
  disabled,
  ...props
}: CheckboxProps) {
  const generatedId = useId();
  const inputId = id || generatedId;

  return (
    <div className={cn("checkbox-wrapper-46 inline-flex items-center", className)}>
      <input
        type="checkbox"
        id={inputId}
        className="inp-cbx"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        {...props}
      />
      <label htmlFor={inputId} className="cbx flex items-center text-xs font-medium text-muted-foreground select-none">
        <span>
          <svg viewBox="0 0 12 10" height="10px" width="12px">
            <polyline points="1.5 6 4.5 9 10.5 1" />
          </svg>
        </span>
        {label && <span>{label}</span>}
      </label>
    </div>
  );
}

export default Checkbox;