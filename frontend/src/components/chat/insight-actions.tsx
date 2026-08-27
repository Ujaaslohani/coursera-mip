"use client"

import React from "react"
import { type Citation } from "@/types/chat.types"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Plus } from "lucide-react"
import { parseActionSteps, renderProseWithHoverSegmentBadges } from "./insight-utils"

interface InsightActionsProps {
  action: string
  citations?: Citation[]
}

export const InsightActions: React.FC<InsightActionsProps> = ({
  action,
  citations = [],
}) => {
  if (!action) return null

  const actionData = parseActionSteps(action)

  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Recommended Action
      </h4>

      {actionData.steps && actionData.steps.length > 0 ? (
        <div className="space-y-2">
          {actionData.intro && (
            <p className="text-foreground/90 leading-relaxed">
              {renderProseWithHoverSegmentBadges(actionData.intro, citations)}
            </p>
          )}
          <ul className="space-y-2">
            {actionData.steps.map((step, idx) => (
              <li key={idx} className="flex items-start gap-2.5 group">
                <Tooltip>
                  <TooltipTrigger
                    type="button"
                    className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 shadow-2xs transition-all cursor-pointer"
                    title="Add in the recommendation"
                  >
                    <Plus className="h-3.5 w-3.5 stroke-[2.5]" />
                  </TooltipTrigger>
                  <TooltipContent side="top">
                    Add in the recommendation
                  </TooltipContent>
                </Tooltip>
                <div className="leading-relaxed text-foreground/90 text-sm flex-1">
                  <span className="font-semibold text-foreground mr-1">
                    {step.number}.
                  </span>
                  {renderProseWithHoverSegmentBadges(step.text, citations)}
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : actionData.intro ? (
        <div className="flex items-start gap-2.5 pt-0.5">
          <Tooltip>
            <TooltipTrigger
              type="button"
              className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 shadow-2xs transition-all cursor-pointer"
              title="Add in the recommendation"
            >
              <Plus className="h-3.5 w-3.5 stroke-[2.5]" />
            </TooltipTrigger>
            <TooltipContent side="top">
              Add in the recommendation
            </TooltipContent>
          </Tooltip>
          <p className="text-foreground/90 leading-relaxed text-sm flex-1">
            {renderProseWithHoverSegmentBadges(actionData.intro, citations)}
          </p>
        </div>
      ) : null}
    </div>
  )
}
