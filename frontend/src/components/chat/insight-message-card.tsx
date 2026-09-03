"use client"

import React from "react"
import { type Citation } from "@/types/chat.types"
import { TooltipProvider } from "@/components/ui/tooltip"
import { parseInsightContent, renderProseWithHoverSegmentBadges } from "./insight-utils"
import { InsightSummary } from "./insight-summary"
import { InsightFriction } from "./insight-friction"
import { InsightActions } from "./insight-actions"
import { InsightCitations } from "./insight-citations"
import { CurateButton } from "./curate-button"

export interface InsightMessageCardProps {
  content: string;
  confidence?: number;
  citations?: Citation[];
  insightId?: string;
  recommendedAction?: string | null;
  isCurated?: boolean;
  curatedSteps?: string[];
  onCurated?: (stepText?: string) => void;
}

export const InsightMessageCard: React.FC<InsightMessageCardProps> = ({
  content,
  confidence,
  citations = [],
  insightId,
  recommendedAction,
  isCurated,
  curatedSteps = [],
  onCurated,
}) => {
  const parsed = parseInsightContent(content)
  const confidencePercent =
    confidence !== undefined ? Math.round(confidence * 100) : null

  if (!parsed.isStructured) {
    return (
      <TooltipProvider>
        <div className="space-y-4 text-foreground text-sm">
          <div className="leading-relaxed whitespace-pre-wrap">
            {renderProseWithHoverSegmentBadges(content, citations)}
          </div>
          <InsightCitations citations={citations} confidencePercent={confidencePercent} />
          {!citations.length && confidencePercent !== null && (
            <div className="text-[11px] text-muted-foreground font-mono pt-1">
              {confidencePercent}% confidence
            </div>
          )}
          <CurateButton
            insightId={insightId}
            recommendedAction={recommendedAction}
            content={content}
            isCurated={isCurated}
            onCurated={onCurated}
          />
        </div>
      </TooltipProvider>
    )
  }

  return (
    <TooltipProvider>
      <div className="space-y-4 text-foreground text-sm">
        <InsightSummary summary={parsed.summary || ""} citations={citations} />
        <InsightFriction friction={parsed.friction || ""} citations={citations} />
        <InsightActions
          action={parsed.action || ""}
          citations={citations}
          insightId={insightId}
          isCurated={isCurated}
          curatedSteps={curatedSteps}
          onCurated={onCurated}
        />
        <InsightCitations citations={citations} confidencePercent={confidencePercent} />
      </div>
    </TooltipProvider>
  )
}
