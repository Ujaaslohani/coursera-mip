"use client"

import React, { useState } from "react"
import { type Citation } from "@/types/chat.types"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { ChevronDown, ChevronUp } from "lucide-react"
import { getModalityIcon } from "./modality-icon"
import { cleanCitationText } from "@/lib/citation-sanitizer"

interface InsightCitationsProps {
  citations?: Citation[]
  confidencePercent?: number | null
}

export const InsightCitations: React.FC<InsightCitationsProps> = ({
  citations = [],
  confidencePercent = null,
}) => {
  const [expandedCitation, setExpandedCitation] = useState<number | null>(null)

  if (citations.length === 0 && confidencePercent === null) {
    return null
  }

  if (citations.length === 0 && confidencePercent !== null) {
    return (
      <div className="pt-2 border-t border-border/40 text-[11px] text-muted-foreground font-mono">
        {confidencePercent}% confidence
      </div>
    )
  }

  return (
    <div className="pt-2 border-t border-border/40 space-y-2">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="font-medium">
          Cited Evidence ({citations.length})
        </span>
        {confidencePercent !== null && (
          <span className="text-[11px] font-mono opacity-80">
            {confidencePercent}% confidence
          </span>
        )}
      </div>

      <div className="space-y-1.5">
        {citations.map((c, idx) => {
          const isExpanded = expandedCitation === idx
          return (
            <div
              key={idx}
              onClick={() => setExpandedCitation(isExpanded ? null : idx)}
              className="rounded-md bg-muted/40 hover:bg-muted/70 px-2.5 py-1.5 text-xs cursor-pointer transition-colors border border-border/30"
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  {getModalityIcon(c.content_type)}
                  <Tooltip>
                    <TooltipTrigger
                      type="button"
                      onClick={(e) => e.stopPropagation()}
                      className="font-medium text-foreground truncate hover:underline underline-offset-2 cursor-help"
                    >
                      {c.lecture_id || c.point_id}
                    </TooltipTrigger>
                    <TooltipContent
                      side="top"
                      className="text-[11px] font-mono max-w-xs break-all"
                    >
                      Segment ID: {c.point_id}
                    </TooltipContent>
                  </Tooltip>
                  {c.content_type && (
                    <span className="text-[10px] text-muted-foreground uppercase">
                      ({c.content_type})
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1.5 shrink-0 text-muted-foreground">
                  {c.score !== undefined && (
                    <span className="text-[10px] font-mono">
                      {(c.score * 100).toFixed(0)}%
                    </span>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="h-3 w-3" />
                  ) : (
                    <ChevronDown className="h-3 w-3" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <p className="mt-1.5 pt-1.5 border-t border-border/40 text-muted-foreground whitespace-pre-wrap leading-relaxed">
                  {cleanCitationText(c.text_preview)}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
