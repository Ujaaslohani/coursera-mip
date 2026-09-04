import { useState, useEffect, useCallback } from "react";
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
import {
  Sparkles,
  Clock,
  Save,
  ChevronDown,
  ChevronUp,
  Trash2,
} from "lucide-react";

// LOCAL STORAGE HELPERS
const NOTES_STORAGE_KEY = "recommendation-notes";

interface SavedNote {
  id: string;
  text: string;
  savedAt: string;
}

type NotesStore = Record<string, SavedNote[]>;

function loadNotesForRecommendation(recommendationId: string): SavedNote[] {
  try {
    const raw = localStorage.getItem(NOTES_STORAGE_KEY);
    if (!raw) return [];
    const store: NotesStore = JSON.parse(raw);
    return store[recommendationId] ?? [];
  } catch {
    return [];
  }
}

function persistNotes(recommendationId: string, notes: SavedNote[]) {
  try {
    const raw = localStorage.getItem(NOTES_STORAGE_KEY);
    const store: NotesStore = raw ? JSON.parse(raw) : {};
    store[recommendationId] = notes;
    localStorage.setItem(NOTES_STORAGE_KEY, JSON.stringify(store));
  } catch {
    // silently fail for now.
  }
}

// PROPS
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
  const [savedNotes, setSavedNotes] = useState<SavedNote[]>([]);
  const [notesExpanded, setNotesExpanded] = useState(true);

  // LOAD SAVED NOTES FROM LOCAL STORAGE WHEN RECOMMENDATION CHANGES
  useEffect(() => {
    if (selectedRecommendation) {
      const notes = loadNotesForRecommendation(selectedRecommendation.id);
      setSavedNotes(notes);
      setNotesExpanded(notes.length > 0);
    } else {
      setSavedNotes([]);
    }
  }, [selectedRecommendation]);

  // SAVE THE CURRENT NOTE TEXT TO LOCAL STORAGE
  const handleSaveNote = useCallback(() => {
    if (!selectedRecommendation || !noteText.trim()) return;

    const newNote: SavedNote = {
      id: crypto.randomUUID(),
      text: noteText.trim(),
      savedAt: new Date().toISOString(),
    };

    const updated = [...savedNotes, newNote];
    setSavedNotes(updated);
    persistNotes(selectedRecommendation.id, updated);
    onNoteChange("");
    setNotesExpanded(true);
  }, [selectedRecommendation, noteText, savedNotes, onNoteChange]);

  // DELETE A SAVED NOTE
  const handleDeleteNote = useCallback(
    (noteId: string) => {
      if (!selectedRecommendation) return;
      const updated = savedNotes.filter((n) => n.id !== noteId);
      setSavedNotes(updated);
      persistNotes(selectedRecommendation.id, updated);
    },
    [selectedRecommendation, savedNotes],
  );

  // FORMAT TIMESTAMP
  const formatTimestamp = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

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
                {selectedRecommendation.fullTitle ||
                  selectedRecommendation.title}
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

              {/* NOTE INPUT WITH SAVE BUTTON */}
              <div className="space-y-2">
                <label className="text-xs font-semibold text-foreground">
                  Note
                </label>
                <div className="relative">
                  <Textarea
                    placeholder="Add a note or review feedback..."
                    value={noteText}
                    onChange={(e) => onNoteChange(e.target.value)}
                    className="min-h-[100px] resize-none text-xs sm:text-sm pr-10"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={handleSaveNote}
                    disabled={!noteText.trim()}
                    title="Save note"
                    className="absolute bottom-2 right-2 h-7 w-7 text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors disabled:opacity-30"
                  >
                    <Save className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {/* SAVED NOTES COLLAPSIBLE SECTION */}
              {savedNotes.length > 0 && (
                <div className="space-y-2">
                  <button
                    type="button"
                    onClick={() => setNotesExpanded((prev) => !prev)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider hover:text-foreground transition-colors w-full"
                  >
                    {notesExpanded ? (
                      <ChevronUp className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                    Saved Notes ({savedNotes.length})
                  </button>

                  {notesExpanded && (
                    <div className="space-y-2">
                      {savedNotes.map((note) => (
                        <div
                          key={note.id}
                          className="group rounded-lg border border-border/60 bg-muted/30 p-3 space-y-1.5 transition-colors hover:border-border"
                        >
                          <p className="text-xs sm:text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
                            {note.text}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-muted-foreground">
                              {formatTimestamp(note.savedAt)}
                            </span>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeleteNote(note.id)}
                              title="Delete note"
                              className="h-5 w-5 opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all"
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
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
