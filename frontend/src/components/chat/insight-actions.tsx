"use client"

import React, { useState } from "react"
import { type Citation } from "@/types/chat.types"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { Plus, Check } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"
import { parseActionSteps, renderProseWithHoverSegmentBadges } from "./insight-utils"
import { useCurateRecommendation } from "@/hooks/mutations/use-curate-recommendation"
import { useQueryClient } from "@tanstack/react-query"

interface InsightActionsProps {
  action: string
  citations?: Citation[]
  insightId?: string
  isCurated?: boolean
  curatedSteps?: string[]
  onCurated?: (stepText?: string) => void
}

export const InsightActions: React.FC<InsightActionsProps> = ({
  action,
  citations = [],
  insightId,
  isCurated,
  curatedSteps = [],
  onCurated,
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
                <CurateStepButton
                  insightId={insightId}
                  stepText={step.text}
                  stepNumber={step.number}
                  fullAction={action}
                  isCurated={curatedSteps.includes(step.text)}
                  onCurated={onCurated}
                />
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
          <CurateStepButton
            insightId={insightId}
            stepText={actionData.intro}
            fullAction={action}
            isCurated={curatedSteps.includes(actionData.intro)}
            onCurated={onCurated}
          />
          <p className="text-foreground/90 leading-relaxed text-sm flex-1">
            {renderProseWithHoverSegmentBadges(actionData.intro, citations)}
          </p>
        </div>
      ) : null}
    </div>
  )
}

// ── Individual step curate button ──────────────────────────────────

interface CurateStepButtonProps {
  insightId?: string
  stepText: string
  stepNumber?: string
  fullAction: string
  isCurated?: boolean
  onCurated?: (stepText?: string) => void
}

const CurateStepButton: React.FC<CurateStepButtonProps> = ({
  insightId,
  stepText,
  stepNumber,
  fullAction,
  isCurated: parentCurated,
  onCurated,
}) => {
  const curate = useCurateRecommendation()
  const queryClient = useQueryClient()
  const [added, setAdded] = useState(false)

  const isAdded = added || parentCurated

  const handleClick = () => {
    if (!insightId || isAdded || curate.isPending) return

    const title = stepText.slice(0, 80).trim()

    curate.mutate(
      {
        insight_id: insightId,
        title: stepNumber ? `${stepNumber}. ${title}` : title,
        category: "content_review",
        recommendation_text: stepText,
        priority: 1,
      },
      {
        onSuccess: () => {
          setAdded(true)
          onCurated?.(stepText)
          queryClient.invalidateQueries({ queryKey: ["recommendations"] })
        },
      }
    )
  }

  if (!insightId) {
    // No insight ID — render the button as decorative (no handler)
    return (
      <Tooltip>
        <TooltipTrigger
          type="button"
          className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 shadow-2xs transition-all cursor-pointer"
          title="Add to recommendations"
        >
          <Plus className="h-3.5 w-3.5 stroke-[2.5]" />
        </TooltipTrigger>
        <TooltipContent side="top">
          Add to recommendations
        </TooltipContent>
      </Tooltip>
    )
  }

  if (isAdded) {
    return (
      <Tooltip>
        <TooltipTrigger
          type="button"
          className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-emerald-500 text-white shadow-2xs"
        >
          <Check className="h-3.5 w-3.5 stroke-[2.5]" />
        </TooltipTrigger>
        <TooltipContent side="top">
          Added to recommendations
        </TooltipContent>
      </Tooltip>
    )
  }

  return (
    <Tooltip>
      <TooltipTrigger
        type="button"
        onClick={handleClick}
        disabled={curate.isPending}
        className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground hover:bg-primary/90 shadow-2xs transition-all cursor-pointer disabled:opacity-50"
        title="Add to recommendations"
      >
        {curate.isPending ? (
          <Spinner className="h-3 w-3" />
        ) : (
          <Plus className="h-3.5 w-3.5 stroke-[2.5]" />
        )}
      </TooltipTrigger>
      <TooltipContent side="top">
        Add to recommendations
      </TooltipContent>
    </Tooltip>
  )
}
