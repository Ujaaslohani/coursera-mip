"use client"

import React from "react"
import {
  FileQuestion,
  FileText,
  Layers,
  MessageSquare,
  Subtitles,
  Video,
} from "lucide-react"

interface ModalityIconProps {
  modality?: string
  className?: string
}

export const getModalityIcon = (modality?: string, className = "h-3.5 w-3.5 shrink-0") => {
  const m = modality?.toLowerCase() || ""
  if (m.includes("video")) return <Video className={`${className} text-blue-400`} />
  if (m.includes("slide") || m.includes("frame"))
    return <Layers className={`${className} text-amber-400`} />
  if (m.includes("caption") || m.includes("transcript"))
    return <Subtitles className={`${className} text-indigo-400`} />
  if (m.includes("quiz"))
    return <FileQuestion className={`${className} text-emerald-400`} />
  if (m.includes("discussion"))
    return <MessageSquare className={`${className} text-purple-400`} />
  return <FileText className={`${className} text-sky-400`} />
}

export const ModalityIcon: React.FC<ModalityIconProps> = ({ modality, className }) => {
  return getModalityIcon(modality, className)
}
