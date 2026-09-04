import React from "react";
import {
  FileText,
  Presentation,
  Film,
  Video,
  MessagesSquare,
  HelpCircle,
  Image as ImageIcon,
  Layers,
} from "lucide-react";

export type ModalityBadgeVariant = "default" | "secondary" | "outline" | "info" | "warning";

export interface ModalityItemConfig {
  key: string;
  label: string;
  subtext: string;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  color: string;
  textColorClass: string;
  badgeVariant: ModalityBadgeVariant;
}

export const MODALITY_CONFIG: Record<string, ModalityItemConfig> = {
  caption: {
    key: "caption",
    label: "Captions",
    subtext: "Spoken lecture transcript chunks",
    icon: FileText,
    color: "#3B82F6",
    textColorClass: "text-blue-500 dark:text-blue-400",
    badgeVariant: "info",
  },
  transcript: {
    key: "transcript",
    label: "Transcript",
    subtext: "Spoken lecture transcript chunks",
    icon: FileText,
    color: "#3B82F6",
    textColorClass: "text-blue-500 dark:text-blue-400",
    badgeVariant: "info",
  },
  slide: {
    key: "slide",
    label: "Slides",
    subtext: "Instructional slide images & text",
    icon: Presentation,
    color: "#8B5CF6",
    textColorClass: "text-purple-500 dark:text-purple-400",
    badgeVariant: "secondary",
  },
  frame: {
    key: "frame",
    label: "Video Frames",
    subtext: "Caption-aligned video frames",
    icon: Film,
    color: "#06B6D4",
    textColorClass: "text-cyan-500 dark:text-cyan-400",
    badgeVariant: "default",
  },
  video: {
    key: "video",
    label: "Video",
    subtext: "Recorded lecture segments",
    icon: Video,
    color: "#06B6D4",
    textColorClass: "text-cyan-500 dark:text-cyan-400",
    badgeVariant: "default",
  },
  image: {
    key: "image",
    label: "Image",
    subtext: "Diagrams & visual assets",
    icon: ImageIcon,
    color: "#8B5CF6",
    textColorClass: "text-purple-500 dark:text-purple-400",
    badgeVariant: "secondary",
  },
  discussion: {
    key: "discussion",
    label: "Discussions",
    subtext: "Forum confusion threads & Q&A",
    icon: MessagesSquare,
    color: "#F59E0B",
    textColorClass: "text-amber-500 dark:text-amber-400",
    badgeVariant: "warning",
  },
  quiz: {
    key: "quiz",
    label: "Quizzes",
    subtext: "Formative assessments & questions",
    icon: HelpCircle,
    color: "#EC4899",
    textColorClass: "text-pink-500 dark:text-pink-400",
    badgeVariant: "outline",
  },
};

const DEFAULT_MODALITY_CONFIG: ModalityItemConfig = {
  key: "content",
  label: "Content",
  subtext: "Indexed multimodal content",
  icon: Layers,
  color: "#64748B",
  textColorClass: "text-slate-500 dark:text-slate-400",
  badgeVariant: "secondary",
};

/**
 * Normalizes any raw modality string (e.g. "transcript", "caption", "video_frame", "quiz_question")
 * to its canonical ModalityItemConfig.
 */
export function getModalityConfig(modality?: string | null): ModalityItemConfig {
  if (!modality) return DEFAULT_MODALITY_CONFIG;
  const m = modality.toLowerCase().trim();

  if (MODALITY_CONFIG[m]) return MODALITY_CONFIG[m];

  if (m.includes("transcript") || m.includes("caption")) return MODALITY_CONFIG.caption;
  if (m.includes("slide")) return MODALITY_CONFIG.slide;
  if (m.includes("frame")) return MODALITY_CONFIG.frame;
  if (m.includes("video")) return MODALITY_CONFIG.video;
  if (m.includes("image")) return MODALITY_CONFIG.image;
  if (m.includes("quiz") || m.includes("question")) return MODALITY_CONFIG.quiz;
  if (m.includes("discussion") || m.includes("forum") || m.includes("thread"))
    return MODALITY_CONFIG.discussion;

  return {
    ...DEFAULT_MODALITY_CONFIG,
    key: m,
    label: m.charAt(0).toUpperCase() + m.slice(1),
  };
}
