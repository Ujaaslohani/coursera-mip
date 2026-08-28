import { Recommendation } from "@/types";
import { Sparkles, Mail, Clock } from "lucide-react";

interface RecommendationCardProps {
  item: Recommendation;
  onSelect: (item: Recommendation) => void;
}

export function RecommendationCard({
  item,
  onSelect,
}: RecommendationCardProps) {
  return (
    <div
      onClick={() => onSelect(item)}
      className="flex flex-col justify-between rounded-xl border border-border bg-card p-5 shadow-xs transition-all duration-200 hover:shadow-md hover:border-primary/40 hover:-translate-y-0.5 group cursor-pointer"
    >
      <div className="space-y-3">
        {/* HEADER TAGS */}
        <div className="flex items-center justify-between gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
            {item.category}
          </span>
          <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground">
            <Clock className="h-3 w-3" />
            {item.timestamp}
          </span>
        </div>

        {/* TITLE */}
        <h2 className="text-sm font-semibold leading-snug text-card-foreground group-hover:text-primary transition-colors">
          {item.title}
        </h2>

        {/* DESCRIPTION */}
        {item.description && (
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {item.description}
          </p>
        )}
      </div>

      {/* FOOTER */}
      <div className="mt-4 pt-3 border-t border-border flex items-center justify-between gap-2 text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5 min-w-0">
          <Mail className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
          <span className="truncate font-mono text-[11px]">{item.queryBy}</span>
        </div>
      </div>
    </div>
  );
}
