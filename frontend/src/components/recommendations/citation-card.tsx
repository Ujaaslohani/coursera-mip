import { Citation } from "@/types";
import {
  FileVideoCamera,
  Image as ImageIcon,
  Captions,
  FileQuestionMark,
  MessagesSquare,
} from "lucide-react";

interface CitationCardProps {
  citation: Citation;
}

export function CitationTypeBadge({ type }: { type: string }) {
  const normalizedType = type.toLowerCase();

  if (
    normalizedType.includes("transcript") ||
    normalizedType.includes("caption")
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground border border-border/60">
        <Captions className="h-3.5 w-3.5 text-muted-foreground" />
        <span>Transcript</span>
      </span>
    );
  }

  if (normalizedType.includes("image")) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground border border-border/60">
        <ImageIcon className="h-3.5 w-3.5 text-muted-foreground" />
        <span>Image</span>
      </span>
    );
  }

  if (normalizedType.includes("video")) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground border border-border/60">
        <FileVideoCamera className="h-3.5 w-3.5 text-muted-foreground" />
        <span>Video</span>
      </span>
    );
  }

  if (
    normalizedType.includes("quiz") ||
    normalizedType.includes("question")
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground border border-border/60">
        <FileQuestionMark className="h-3.5 w-3.5 text-muted-foreground" />
        <span>Quiz</span>
      </span>
    );
  }

  if (
    normalizedType.includes("discussion") ||
    normalizedType.includes("thread") ||
    normalizedType.includes("message")
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground border border-border/60">
        <MessagesSquare className="h-3.5 w-3.5 text-muted-foreground" />
        <span>Discussion Thread</span>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2.5 py-0.5 text-xs font-medium text-foreground border border-border/60">
      <Captions className="h-3.5 w-3.5 text-muted-foreground" />
      <span>{type}</span>
    </span>
  );
}

export function CitationCard({ citation }: CitationCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2.5 shadow-2xs">
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-xs text-muted-foreground">
          {citation.id}
        </span>
        <CitationTypeBadge type={citation.type} />
      </div>

      <p className="text-xs sm:text-sm font-medium text-foreground leading-relaxed">
        &ldquo;{citation.quote}&rdquo;
      </p>

      <p className="text-xs text-muted-foreground italic leading-relaxed">
        {citation.explanation}
      </p>
    </div>
  );
}
