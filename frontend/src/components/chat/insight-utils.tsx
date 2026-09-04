"use client";

import React from "react";
import {
  type ActionData,
  type ActionStep,
  type Citation,
  type ParsedInsight,
} from "@/types/chat.types";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { getModalityIcon } from "./modality-icon";
import { cleanCitationText } from "@/lib/citation-sanitizer";

/**
 * PARSES STRUCTURED MARKDOWN HEADERS FROM LLM SYNTHESIS TEXT.
 * SUPPORTS BOTH BOLD-MARKDOWN (**Summary:**) AND PLAIN-TEXT (Summary:) HEADERS.
 */
export function parseInsightContent(content: string): ParsedInsight {
  if (!content) {
    return { isStructured: false, rawText: "" };
  }

  // Combined regex matching bold (**Header:**) or plain (Header:) headers
  const summaryMatch = content.match(
    /(?:\*\*Summary:\*\*|^Summary:)\s*([\s\S]*?)(?=(?:\*\*Friction Diagnostic:\*\*|^Friction Diagnostic:|\*\*Recommended Action:\*\*|^Recommended Action:|$))/im
  );
  const frictionMatch = content.match(
    /(?:\*\*Friction Diagnostic:\*\*|^Friction Diagnostic:)\s*([\s\S]*?)(?=(?:\*\*Recommended Action:\*\*|^Recommended Action:|$))/im
  );
  const actionMatch = content.match(
    /(?:\*\*Recommended Action:\*\*|^Recommended Action:)\s*([\s\S]*?)$/im
  );

  const summary = summaryMatch ? summaryMatch[1].trim() : undefined;
  const friction = frictionMatch ? frictionMatch[1].trim() : undefined;
  const action = actionMatch ? actionMatch[1].trim() : undefined;

  return {
    summary,
    friction,
    action,
    isStructured: Boolean(summary || friction || action),
    rawText: content,
  };
}

/**
 * EXTRACTS INTRO AND NUMBERED STEPS FROM RECOMMENDED ACTION TEXT.
 */
export function parseActionSteps(actionText: string): ActionData {
  if (!actionText) return { intro: "", steps: [] };

  // 1. Parenthesized numbers: (1) do X (2) do Y
  const parts = actionText.split(/\((\d+)\)\s*/);
  if (parts.length > 2) {
    const intro = parts[0].trim();
    const steps: ActionStep[] = [];
    for (let i = 1; i < parts.length; i += 2) {
      const num = parts[i];
      const text = parts[i + 1]?.trim() || "";
      if (text) steps.push({ number: num, text });
    }
    return { intro, steps };
  }

  // 2. Numbered lines: 1. do X \n 2. do Y
  const numParts = actionText.split(/\n(?=\d+\.\s+)/);
  if (numParts.length > 1) {
    const intro = numParts[0].startsWith("1.") ? "" : numParts[0].trim();
    const steps: ActionStep[] = numParts
      .filter((p) => /^\d+\.\s+/.test(p.trim()))
      .map((p, idx) => ({
        number: String(idx + 1),
        text: p.replace(/^\d+\.\s+/, "").trim(),
      }));
    return { intro, steps };
  }

  return { intro: actionText, steps: [] };
}

/**
 * REPLACES RAW UUID STRINGS IN TEXT WITH CLEAN INTERACTIVE HOVER BADGES.
 */
export function renderProseWithHoverSegmentBadges(
  text: string,
  citations: Citation[],
): React.ReactNode {
  const uuidPattern =
    /([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/gi;

  const parts = text.split(uuidPattern);
  if (parts.length === 1) {
    return text;
  }

  return parts.map((part, idx) => {
    const isUuid =
      /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(
        part,
      );

    if (isUuid) {
      const match = citations.find(
        (c) => c.point_id.toLowerCase() === part.toLowerCase(),
      );
      const cIndex = match ? citations.indexOf(match) + 1 : null;
      const label =
        match?.lecture_id || (cIndex ? `Evidence ${cIndex}` : "Evidence");

      return (
        <Tooltip key={idx}>
          <TooltipTrigger
            type="button"
            className="inline-flex items-center gap-1 mx-1 px-1.5 py-0.5 rounded bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 text-xs font-medium transition-colors cursor-help align-baseline"
          >
            {getModalityIcon(match?.content_type)}
            <span>{label}</span>
          </TooltipTrigger>
          <TooltipContent
            side="top"
            className="p-3 bg-popover text-popover-foreground border border-border shadow-lg"
          >
            <div className="flex flex-col gap-1.5 w-72 sm:w-80 text-left">
              <div className="flex items-center justify-between gap-2 text-xs font-semibold text-primary">
                <div className="flex items-center gap-1.5">
                  {getModalityIcon(match?.content_type)}
                  <span>{match?.lecture_id || "Course Evidence"}</span>
                </div>
                {match?.content_type && (
                  <span className="text-[10px] uppercase text-muted-foreground font-normal">
                    ({match.content_type})
                  </span>
                )}
              </div>
              <p className="text-[11px] font-mono text-muted-foreground break-all">
                Segment ID: {part}
              </p>
              {match?.text_preview && (
                <p className="text-xs text-foreground/90 leading-relaxed italic border-l-2 border-primary/40 pl-2 pt-0.5">
                  &ldquo;
                  {(() => {
                    const cleaned = cleanCitationText(match.text_preview);
                    return cleaned.length > 180
                      ? cleaned.slice(0, 180).trim().replace(/[.,;:]+$/, "") + "..."
                      : cleaned;
                  })()}
                  &rdquo;
                </p>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      );
    }

    return <span key={idx}>{part}</span>;
  });
}
