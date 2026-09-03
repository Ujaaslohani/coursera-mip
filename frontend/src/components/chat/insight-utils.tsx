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

/**
 * PARSES STRUCTURED MARKDOWN HEADERS FROM LLM SYNTHESIS TEXT.
 * SUPPORTS BOTH BOLD-MARKDOWN (**Summary:**) AND PLAIN-TEXT (Summary:) HEADERS.
 */
export function parseInsightContent(content: string): ParsedInsight {
  // TRY BOLD-MARKDOWN HEADERS FIRST
  let summaryMatch = content.match(
    /\*\*Summary:\*\*\s*([\s\S]*?)(?=\*\*Friction Diagnostic:\*\*|\*\*Recommended Action:\*\*|$)/i,
  );
  let frictionMatch = content.match(
    /\*\*Friction Diagnostic:\*\*\s*([\s\S]*?)(?=\*\*Recommended Action:\*\*|$)/i,
  );
  let actionMatch = content.match(/\*\*Recommended Action:\*\*\s*([\s\S]*?)$/i);

  // IF BOLD-MARKDOWN DIDN'T FIND ANYTHING, TRY PLAIN-TEXT HEADERS (e.g. "Summary:" AT START OF LINE)
  if (!summaryMatch && !frictionMatch && !actionMatch) {
    summaryMatch = content.match(
      /^Summary:\s*([\s\S]*?)(?=Friction Diagnostic:|Recommended Action:|$)/im,
    );
    frictionMatch = content.match(
      /^Friction Diagnostic:\s*([\s\S]*?)(?=Recommended Action:|$)/im,
    );
    actionMatch = content.match(/^Recommended Action:\s*([\s\S]*?)$/im);
  }

  const summary = summaryMatch ? summaryMatch[1].trim() : undefined;
  const friction = frictionMatch ? frictionMatch[1].trim() : undefined;
  const action = actionMatch ? actionMatch[1].trim() : undefined;

  const isStructured = Boolean(summary || friction || action);

  return {
    summary,
    friction,
    action,
    isStructured,
    rawText: content,
  };
}

/**
 * EXTRACTS INTRO AND NUMBERED STEPS FROM RECOMMENDED ACTION TEXT.
 * DEDUPLICATES INTRO WHEN IT SUBSTANTIALLY OVERLAPS WITH THE FIRST STEP.
 */
export function parseActionSteps(actionText: string): ActionData {
  const parts = actionText.split(/\((\d+)\)\s*/);
  if (parts.length > 2) {
    const intro = parts[0].trim();
    const steps: ActionStep[] = [];
    for (let i = 1; i < parts.length; i += 2) {
      const num = parts[i];
      const text = parts[i + 1]?.trim() || "";
      if (text) steps.push({ number: num, text });
    }
    // DEDUPLICATE: DROP INTRO IF IT SUBSTANTIALLY OVERLAPS WITH FIRST STEP
    const cleanIntro = deduplicateIntro(intro, steps);
    return { intro: cleanIntro, steps };
  }

  const numParts = actionText.split(/\n(?=\d+\.\s+)/);
  if (numParts.length > 1) {
    const rawIntro = numParts[0].startsWith("1.") ? "" : numParts[0].trim();
    const steps: ActionStep[] = numParts
      .filter((p) => /^\d+\.\s+/.test(p.trim()))
      .map((p, idx) => ({
        number: String(idx + 1),
        text: p.replace(/^\d+\.\s+/, "").trim(),
      }));
    // DEDUPLICATE: DROP INTRO IF IT SUBSTANTIALLY OVERLAPS WITH FIRST STEP
    const cleanIntro = deduplicateIntro(rawIntro, steps);
    return { intro: cleanIntro, steps };
  }

  // TRY SEMICOLON-SEPARATED ITEMS (e.g. "do X; do Y; do Z")
  const semiParts = actionText.split(/;\s*/).filter(Boolean);
  if (semiParts.length >= 2) {
    const steps: ActionStep[] = semiParts.map((s, idx) => ({
      number: String(idx + 1),
      text: s.trim().replace(/\.$/, ""),
    }));
    return { intro: "", steps };
  }

  return { intro: actionText, steps: [] };
}

/**
 * DROPS THE INTRO IF ITS FIRST 50 CHARACTERS SUBSTANTIALLY OVERLAP WITH THE FIRST STEP.
 */
function deduplicateIntro(intro: string, steps: ActionStep[]): string {
  if (!intro || steps.length === 0) return intro;
  const introNorm = intro.toLowerCase().slice(0, 60);
  const stepNorm = steps[0].text.toLowerCase().slice(0, 60);
  // IF MORE THAN HALF THE CHARACTERS OVERLAP, THE INTRO IS REDUNDANT
  if (
    introNorm.length > 10 &&
    stepNorm.includes(introNorm.slice(0, Math.floor(introNorm.length * 0.5)))
  ) {
    return "";
  }
  return intro;
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
                  "{match.text_preview}"
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
