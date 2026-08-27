"use client"

import React from "react"
import { useCurateRecommendation } from "@/hooks/mutations/use-curate-recommendation"
import { useQueryClient } from "@tanstack/react-query"
import { Plus, Check, Loader } from "lucide-react"

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

  // Don't render if there's no action to curate or no insight ID
  if (!recommendedAction && !content) return null
  if (!insightId) return null

  const handleCurate = () => {
    if (isCurated || curate.isPending) return

    // Extract a title from the content (first 80 chars of the summary line)
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
          // Invalidate the recommendations list so the /recommendations page picks it up
          queryClient.invalidateQueries({ queryKey: ["recommendations"] })
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
      {recommendedAction && (
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
            <Loader className="h-3.5 w-3.5 animate-spin" />
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
