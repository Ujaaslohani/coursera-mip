"use client"

import React from "react"
import { type InsightMessageCardProps } from "@/types/chat.types"
import { TooltipProvider } from "@/components/ui/tooltip"
import { parseInsightContent, renderProseWithHoverSegmentBadges } from "./insight-utils"
import { InsightSummary } from "./insight-summary"
import { InsightFriction } from "./insight-friction"
import { InsightActions } from "./insight-actions"
import { InsightCitations } from "./insight-citations"

export const InsightMessageCard: React.FC<InsightMessageCardProps> = ({
  content,
  confidence,
  citations = [],
}) => {
  const parsed = parseInsightContent(content)
  const confidencePercent =
    confidence !== undefined ? Math.round(confidence * 100) : null

  if (!parsed.isStructured) {
    return (
      <div className="space-y-2 text-sm leading-relaxed whitespace-pre-wrap text-foreground">
        {renderProseWithHoverSegmentBadges(content, citations)}
        {confidencePercent !== null && (
          <div className="text-[11px] text-muted-foreground pt-1">
            {confidencePercent}% confidence
          </div>
        )}
      </div>
    )
  }

  return (
    <TooltipProvider>
      <div className="space-y-4 text-foreground text-sm">
        <InsightSummary summary={parsed.summary || ""} citations={citations} />
        <InsightFriction friction={parsed.friction || ""} citations={citations} />
        <InsightActions action={parsed.action || ""} citations={citations} />
        <InsightCitations citations={citations} confidencePercent={confidencePercent} />
      </div>
    </TooltipProvider>
  )
}
