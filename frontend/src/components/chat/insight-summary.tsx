"use client"

import React from "react"
import { type Citation } from "@/types/chat.types"
import { renderProseWithHoverSegmentBadges } from "./insight-utils"

interface InsightSummaryProps {
  summary: string
  citations?: Citation[]
}

export const InsightSummary: React.FC<InsightSummaryProps> = ({
  summary,
  citations = [],
}) => {
  if (!summary) return null

  return (
    <div className="space-y-1">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Summary
      </h4>
      <p className="font-medium text-foreground leading-snug">
        {renderProseWithHoverSegmentBadges(summary, citations)}
      </p>
    </div>
  )
}
