"use client";

import React from "react";
import { MessageSquare } from "lucide-react";

interface ChatEmptyStateProps {
  title?: string;
  onSelectSuggestion: (suggestion: string) => void;
}

const DEFAULT_SUGGESTIONS = [
  "What are the common student misconceptions in backpropagation and gradient descent?",
  "Where are students struggling most in transformer and attention architectures?",
  "Suggest improvements and gaps in the current course based on 2026 deep learning trends",
];

export function ChatEmptyState({
  title,
  onSelectSuggestion,
}: ChatEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground text-sm gap-2 max-w-lg mx-auto px-4">
      <MessageSquare className="h-8 w-8 text-muted-foreground/50 mb-1" />
      <p className="font-medium text-foreground text-base">
        {title || "New Conversation"}
      </p>
      <p className="text-xs text-muted-foreground">
        Ask anything about course friction, student misconceptions, or
        pedagogical improvements based on course evidence.
      </p>
      <div className="flex flex-wrap gap-2 justify-center mt-3">
        {DEFAULT_SUGGESTIONS.map((suggestion, i) => (
          <button
            key={i}
            onClick={() => onSelectSuggestion(suggestion)}
            className="text-xs bg-muted/60 hover:bg-muted text-foreground/80 hover:text-foreground px-3 py-1.5 rounded-full border border-border/50 transition-colors cursor-pointer"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
