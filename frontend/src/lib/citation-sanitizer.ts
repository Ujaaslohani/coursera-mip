
function getWordSet(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, "")
      .split(/\s+/)
      .filter((w) => w.length > 2)
  );
}

function isDuplicateSentence(
  candidate: string,
  existingSentences: string[]
): boolean {
  const cWords = getWordSet(candidate);
  if (cWords.size === 0) return true;

  for (const existing of existingSentences) {
    const eWords = getWordSet(existing);
    if (eWords.size === 0) continue;

    let common = 0;
    for (const word of cWords) {
      if (eWords.has(word)) common++;
    }

    const overlapCandidate = common / cWords.size;
    const overlapExisting = common / eWords.size;

    // Candidate is heavily contained in an existing sentence
    if (overlapCandidate >= 0.75) return true;
    // Short sentence with substantial overlap
    if (cWords.size <= 5 && overlapCandidate >= 0.6) return true;
    // Both sentences share substantial core content
    if (
      cWords.size >= 5 &&
      common >= 5 &&
      overlapCandidate > 0.7 &&
      overlapExisting > 0.7
    ) {
      return true;
    }
  }

  return false;
}

/**
 * Cleans citation strings of LaTeX XML tags, Base64 noise, duplicate blocks, and null artifacts.
 */
export function cleanCitationText(raw: string | null | undefined): string {
  if (!raw || typeof raw !== "string") return "";

  let text = raw;

  // 1. Strip LaTeXiT XML tags (handles both '<latexit...>' and spaced-out '< l a t e x i t...>')
  text = text.replace(
    /<\s*l\s*a\s*t\s*e\s*x\s*i\s*t[\s\S]*?<\s*\/\s*l\s*a\s*t\s*e\s*x\s*i\s*t\s*>/gi,
    " "
  );

  // 2. Strip standard XML/HTML tags
  text = text.replace(/<[^>]+>/g, " ");

  // 3. Strip standalone Base64-like noise blocks (25+ chars of base64 chars)
  text = text.replace(/\b[A-Za-z0-9+/]{25,}={0,2}\b/g, " ");

  // 4. Strip isolated/trailing None, nan, null artifacts
  text = text.replace(/\s*\b(None|nan|null)\b\.?\s*$/gi, "");
  text = text.replace(/^\s*(None|nan|null)\s*$/gim, "");

  // 5. Remove consecutively repeated phrases (15+ chars repeating)
  for (let i = 0; i < 3; i++) {
    text = text.replace(/(.{15,}?)(?:\s+|\n+)\1/gi, "$1");
  }

  // 6. Protect common academic abbreviations before splitting sentences
  const protectedText = text.replace(
    /\b(c\.f\.|et al\.|e\.g\.|i\.e\.|vs\.|fig\.|lec\.|no\.)/gi,
    (match) => match.replace(/\./g, "__DOT__")
  );

  // 7. Split into candidate sentences and paragraphs
  const rawSentences = protectedText
    .split(/(?<=[.?!])\s+|\n+/)
    .map((s) => s.replace(/__DOT__/g, ".").trim())
    .filter((s) => s.length > 0);

  // 8. Deduplicate redundant sentences
  const uniqueSentences: string[] = [];
  for (const sentence of rawSentences) {
    const norm = sentence.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (!norm || norm === "none" || norm === "nan" || norm === "null") continue;

    if (!isDuplicateSentence(sentence, uniqueSentences)) {
      uniqueSentences.push(sentence);
    }
  }

  let cleaned = uniqueSentences.join(" ");

  // 9. Clean up spacing and punctuation artifacts
  cleaned = cleaned
    .replace(/\s+/g, " ")
    .replace(/\s+([.,;:!?])/g, "$1")
    .replace(/\b(None|nan|null)\b\.?\s*$/i, "")
    .trim();

  return cleaned;
}

/**
 * Prepares citation quote text with preview and truncation metadata.
 */
export function formatCitationQuote(
  raw: string | null | undefined,
  maxLength = 180
): {
  full: string;
  preview: string;
  isLong: boolean;
} {
  const cleaned = cleanCitationText(raw);
  if (!cleaned) {
    return { full: "", preview: "", isLong: false };
  }

  const isLong = cleaned.length > maxLength;
  const preview = isLong
    ? cleaned.slice(0, maxLength).trim().replace(/[.,;:]+$/, "") + "..."
    : cleaned;

  return {
    full: cleaned,
    preview,
    isLong,
  };
}
