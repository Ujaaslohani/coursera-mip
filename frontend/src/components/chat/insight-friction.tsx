"use client"

import React from "react"
import { type Citation } from "@/types/chat.types"
import { renderProseWithHoverSegmentBadges } from "./insight-utils"

interface InsightFrictionProps {
  friction: string
  citations?: Citation[]
}

export const InsightFriction: React.FC<InsightFrictionProps> = ({
  friction,
  citations = [],
}) => {
  if (!friction) return null

  return (
    <div className="space-y-1">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Friction Diagnostic
      </h4>
      <p className="text-foreground/90 leading-relaxed">
        {renderProseWithHoverSegmentBadges(friction, citations)}
      </p>
    </div>
  )
}
