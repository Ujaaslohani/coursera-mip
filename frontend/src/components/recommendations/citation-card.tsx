"use client";

import React, { useState } from "react";
import { RecommendationCitation } from "@/types";
import { getModalityConfig } from "@/constants/modality.constants";
import { cleanCitationText } from "@/lib/citation-sanitizer";
import { ChevronDown, ChevronUp } from "lucide-react";

interface CitationCardProps {
  citation: RecommendationCitation;
}

export function CitationTypeBadge({ type }: { type: string }) {
  const config = getModalityConfig(type);
  const IconComponent = config.icon;

  return (
    <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground border border-border/60">
      <IconComponent className={`h-3.5 w-3.5 ${config.textColorClass}`} />
      <span>{config.label}</span>
    </span>
  );
}

export function CitationCard({ citation }: CitationCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const cleanQuote = cleanCitationText(citation.quote);
  const isLong = cleanQuote.length > 200;

  const displayText = !isLong || isExpanded
    ? cleanQuote
    : cleanQuote.slice(0, 190).trim().replace(/[.,;:]+$/, "") + "...";

  return (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2.5 shadow-2xs transition-all hover:border-border/90">
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-xs text-muted-foreground font-medium">
          {citation.id}
        </span>
        <CitationTypeBadge type={citation.type} />
      </div>

      {cleanQuote ? (
        <div className="space-y-1.5">
          <blockquote className="text-xs sm:text-sm text-foreground/95 leading-relaxed border-l-2 border-primary/30 pl-3 italic">
            &ldquo;{displayText}&rdquo;
          </blockquote>

          {isLong && (
            <button
              type="button"
              onClick={() => setIsExpanded((prev) => !prev)}
              className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:text-primary/80 transition-colors cursor-pointer pl-3"
            >
              <span>{isExpanded ? "Show less" : "Show full evidence"}</span>
              {isExpanded ? (
                <ChevronUp className="h-3 w-3" />
              ) : (
                <ChevronDown className="h-3 w-3" />
              )}
            </button>
          )}
        </div>
      ) : null}

      {citation.explanation && (
        <p className="text-xs text-muted-foreground italic leading-relaxed pt-0.5">
          {citation.explanation}
        </p>
      )}
    </div>
  );
}
