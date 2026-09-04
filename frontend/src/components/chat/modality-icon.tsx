"use client";

import React from "react";
import { getModalityConfig } from "@/constants/modality.constants";

interface ModalityIconProps {
  modality?: string;
  className?: string;
}

export const getModalityIcon = (
  modality?: string,
  className = "h-3.5 w-3.5 shrink-0"
) => {
  const config = getModalityConfig(modality);
  const IconComponent = config.icon;
  return <IconComponent className={`${className} ${config.textColorClass}`} />;
};

export const ModalityIcon: React.FC<ModalityIconProps> = ({
  modality,
  className,
}) => {
  return getModalityIcon(modality, className);
};

