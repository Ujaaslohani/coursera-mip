import { Recommendation } from "@/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
} from "@/components/ui/sheet";
import { CitationCard } from "./citation-card";
import { Sparkles, Clock } from "lucide-react";

interface RecommendationSheetProps {
  selectedRecommendation: Recommendation | null;
  onOpenChange: (open: boolean) => void;
  noteText: string;
  onNoteChange: (note: string) => void;
  onAccept: () => void;
  onReject: () => void;
  isSubmitting?: boolean;
}

export function RecommendationSheet({
  selectedRecommendation,
  onOpenChange,
  noteText,
  onNoteChange,
  onAccept,
  onReject,
  isSubmitting = false,
}: RecommendationSheetProps) {
  return (
    <Sheet
      open={!!selectedRecommendation}
      onOpenChange={(open) => {
        onOpenChange(open);
      }}
    >
      <SheetContent
        side="right"
        className="w-full sm:max-w-xl data-[side=right]:sm:max-w-xl p-0 flex flex-col justify-between overflow-hidden"
      >
        {selectedRecommendation && (
          <div className="flex flex-col h-full overflow-hidden">
            {/* SHEET HEADER */}
            <SheetHeader className="p-6 border-b border-border space-y-3 bg-muted/20">
              <div className="flex flex-wrap items-center justify-between gap-2 pr-6">
                <span className="inline-flex items-center gap-1.5 rounded-md bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
                  <Sparkles className="h-3.5 w-3.5" />
                  {selectedRecommendation.category}
                </span>
                <span className="font-mono text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded border border-border">
                  {selectedRecommendation.id}
                </span>
              </div>

              <SheetTitle className="text-base sm:text-lg font-semibold leading-snug text-foreground text-left">
                {selectedRecommendation.fullTitle || selectedRecommendation.title}
              </SheetTitle>

              <SheetDescription className="text-xs text-muted-foreground flex items-center gap-2 text-left">
                <Clock className="h-3.5 w-3.5" />
                <span>Detected {selectedRecommendation.timestamp}</span>
                <span>•</span>
                <span>{selectedRecommendation.queryBy}</span>
              </SheetDescription>
            </SheetHeader>

            {/* SCROLLABLE BODY CONTENT */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* DESCRIPTION OBSERVATION */}
              {selectedRecommendation.description && (
                <div className="rounded-xl border border-border/80 bg-muted/40 p-4 text-xs sm:text-sm text-foreground/90 leading-relaxed">
                  {selectedRecommendation.description}
                </div>
              )}

              {/* CITATIONS SECTION */}
              {selectedRecommendation.citations &&
                selectedRecommendation.citations.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      CITATIONS ({selectedRecommendation.citations.length})
                    </h3>
                    <div className="space-y-3">
                      {selectedRecommendation.citations.map((citation, idx) => (
                        <CitationCard
                          key={citation.id || idx}
                          citation={citation}
                        />
                      ))}
                    </div>
                  </div>
                )}

              {/* NOTE TEXTAREA INPUT */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-foreground">
                  Note
                </label>
                <Textarea
                  placeholder="Add a note or review feedback..."
                  value={noteText}
                  onChange={(e) => onNoteChange(e.target.value)}
                  className="min-h-[100px] resize-none text-xs sm:text-sm"
                />
              </div>
            </div>

            {/* SHEET FOOTER WITH ACCEPT AND REJECT BUTTONS */}
            <SheetFooter className="p-4 border-t border-border bg-muted/20 flex-row items-center justify-end gap-2.5">
              <Button
                variant="outline"
                size="sm"
                onClick={onReject}
                disabled={isSubmitting}
                className="border-destructive/40 text-destructive hover:bg-destructive hover:text-white hover:border-destructive transition-colors font-medium px-4"
              >
                {isSubmitting ? "Submitting..." : "Reject"}
              </Button>
              <Button
                size="sm"
                onClick={onAccept}
                disabled={isSubmitting}
                className="bg-primary text-primary-foreground hover:bg-primary-hover font-medium px-4"
              >
                {isSubmitting ? "Submitting..." : "Accept"}
              </Button>
            </SheetFooter>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
