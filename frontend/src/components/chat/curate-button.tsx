"use client"

import React from "react"
import { useCurateRecommendation } from "@/hooks/mutations/use-curate-recommendation"
import { useQueryClient } from "@tanstack/react-query"
import { Plus, Check } from "lucide-react"
import { Spinner } from "@/components/ui/spinner"

export interface CurateButtonProps {
  insightId?: string;
  recommendedAction?: string | null;
  content: string;
  isCurated?: boolean;
  onCurated?: () => void;
}

export const CurateButton: React.FC<CurateButtonProps> = ({
  insightId,
  recommendedAction,
  content,
  isCurated,
  onCurated,
}) => {
  const curate = useCurateRecommendation()
  const queryClient = useQueryClient()

  // DON'T RENDER IF THERE'S NO ACTION TO CURATE OR NO INSIGHT ID
  if (!recommendedAction && !content) return null
  if (!insightId) return null

  const handleCurate = () => {
    if (isCurated || curate.isPending) return

    // EXTRACT A TITLE FROM THE CONTENT (FIRST 80 CHARS OF THE SUMMARY LINE)
    const summaryMatch = content.match(/\*\*Summary:\*\*\s*(.+)/);
    const title = summaryMatch
      ? summaryMatch[1].slice(0, 80).trim()
      : content.slice(0, 80).trim();

    curate.mutate(
      {
        insight_id: insightId,
        title,
        category: "content_review",
        recommendation_text: recommendedAction || content.slice(0, 500),
        priority: 1,
      },
      {
        onSuccess: () => {
          onCurated?.()
          // INVALIDATE THE RECOMMENDATIONS LIST SO THE /RECOMMENDATIONS PAGE PICKS IT UP
          queryClient.invalidateQueries({ queryKey: ["recommendations"] })
          queryClient.invalidateQueries({ queryKey: ["conversation-messages"] })
        },
      }
    )
  }

  if (isCurated) {
    return (
      <div className="mt-3 pt-3 border-t border-border/50">
        <div className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full">
          <Check className="h-3.5 w-3.5" />
          <span>Added to Recommendations</span>
        </div>
      </div>
    )
  }

  return (
    <div className="mt-3 pt-3 border-t border-border/50">
      {recommendedAction && !content.includes(recommendedAction.slice(0, 60)) && (
        <p className="text-xs text-muted-foreground mb-2 line-clamp-2 leading-relaxed">
          <span className="font-medium text-foreground/80">Suggested: </span>
          {recommendedAction}
        </p>
      )}
      <button
        onClick={handleCurate}
        disabled={curate.isPending}
        className="inline-flex items-center gap-1.5 text-xs font-medium text-primary bg-primary/10 hover:bg-primary/20 px-3 py-1.5 rounded-full transition-colors disabled:opacity-50 cursor-pointer"
      >
        {curate.isPending ? (
          <>
            <Spinner className="h-3.5 w-3.5" />
            <span>Adding...</span>
          </>
        ) : (
          <>
            <Plus className="h-3.5 w-3.5" />
            <span>Add to Recommendations</span>
          </>
        )}
      </button>
      {curate.isError && (
        <p className="text-xs text-destructive mt-1.5">
          Failed to add. Please try again.
        </p>
      )}
    </div>
  )
}
