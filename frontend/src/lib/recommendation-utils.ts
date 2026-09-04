
export function truncateWithEllipsis(text: string, limit = 80): string {
  if (!text) return "";
  const trimmed = text.trim();
  if (trimmed.length <= limit) return trimmed;

  const sliced = trimmed.slice(0, limit);
  const lastSpace = sliced.lastIndexOf(" ");

  // Cut at last space if within the last 40% of the limit to avoid cutting words in half
  const cleanCut = lastSpace > limit * 0.6 ? sliced.slice(0, lastSpace) : sliced;

  // Clean trailing punctuation before adding ellipsis
  return cleanCut.replace(/[\s,.;:!?\-‑]+$/, "") + "...";
}

export function resolveRecommendationTitles(
  rawRecommendationText?: string,
  metadataTitle?: string
): { title: string; fullTitle: string } {
  const rawText = (rawRecommendationText || "").trim();
  const metaTitle = (metadataTitle || "").trim();

  let fullTitle = metaTitle;

  if (!metaTitle) {
    fullTitle = rawText || "Untitled";
  } else if (rawText) {
    // 1. Direct match: metadata.title is literally a truncated prefix of rawText
    if (rawText.startsWith(metaTitle) && rawText.length > metaTitle.length) {
      fullTitle = rawText;
    } else {
      // 2. Prefix match: metadata.title has "4. " or "- " followed by truncated rawText
      const prefixMatch = metaTitle.match(/^(\d+\.\s*|[-*•]\s*|\(\d+\)\s*)/);
      const prefix = prefixMatch ? prefixMatch[0] : "";
      const strippedMeta = metaTitle.slice(prefix.length).trim();

      if (
        strippedMeta &&
        rawText.startsWith(strippedMeta) &&
        rawText.length > strippedMeta.length
      ) {
        fullTitle = prefix ? `${prefix}${rawText}` : rawText;
      } else if (
        metaTitle.length >= 75 &&
        metaTitle.length <= 85 &&
        rawText.length > metaTitle.length
      ) {
        // 3. Length match: metadata.title was sliced around character 80
        fullTitle = prefix ? `${prefix}${rawText}` : rawText;
      }
    }
  }

  // Generate card preview title with "..." after limit (80 characters)
  const title = truncateWithEllipsis(fullTitle, 80);

  return { title, fullTitle };
}
