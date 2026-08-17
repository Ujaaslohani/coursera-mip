import * as React from "react";
import { Search, X } from "lucide-react";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export interface SearchInputProps extends React.ComponentProps<"input"> {
  containerClassName?: string;
  icon?: React.ReactNode;
  showClear?: boolean;
  onClear?: () => void;
}

function SearchInput({
  className,
  containerClassName,
  icon,
  value,
  onChange,
  onClear,
  showClear = false,
  placeholder = "Search...",
  ...props
}: SearchInputProps) {
  const hasValue = value !== undefined && value !== "";

  return (
    <div
      className={cn("relative flex items-center w-full", containerClassName)}
    >
      <div className="absolute left-2.5 top-1/2 -translate-y-1/2 flex items-center justify-center text-muted-foreground pointer-events-none">
        {icon ?? <Search className="h-4 w-4" />}
      </div>
      <Input
        type="search"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={cn(
          "pl-8 [&::-webkit-search-cancel-button]:appearance-none [&::-webkit-search-decoration]:appearance-none [&::-webkit-search-results-button]:appearance-none [&::-webkit-search-results-decoration]:appearance-none",
          showClear && hasValue && "pr-8",
          className
        )}
        {...props}
      />
      {showClear && hasValue && onClear && (
        <button
          type="button"
          onClick={onClear}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors p-0.5 rounded-full"
          aria-label="Clear search"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}

export { SearchInput };
