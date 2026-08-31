"use client";

import React from "react";
import { MessageSquare } from "lucide-react";

interface ChatEmptyStateProps {
  title?: string;
  onSelectSuggestion: (suggestion: string) => void;
}

const DEFAULT_SUGGESTIONS = [
  "Why are students dropping off in lecture 2?",
  "What is the common misconception in backprop?",
  "Suggest improvements for the intro module",
];

export function ChatEmptyState({
  title,
  onSelectSuggestion,
}: ChatEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground text-sm gap-2 max-w-md mx-auto">
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
