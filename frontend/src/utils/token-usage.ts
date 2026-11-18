import i18n from "@/i18n";
import type { TokenUsageCoverage } from "@/schemas/token-usage";
import { formatCompactNumber, formatNumber, toNumber } from "@/utils/formatters";

export type UsageCompleteness = "complete" | "partial" | "missing";

export function formatObservedTokens(value: unknown, completeness?: UsageCompleteness): string {
  const tokens = toNumber(value);
  if (tokens === null || completeness === "missing") return "--";
  return completeness === "complete" ? formatCompactNumber(tokens) : `≥ ${formatNumber(tokens)}`;
}

export function tokenUsageLabel(completeness?: UsageCompleteness): string {
  return i18n.t(`usage.tokens.${completeness ?? "unknown"}`, {});
}

export function summarizeTokenUsage(value: unknown, coverage?: TokenUsageCoverage) {
  if (!coverage) {
    return { value: formatObservedTokens(value), note: tokenUsageLabel(), complete: false };
  }
  const { completeRequests, partialRequests, missingRequests, unknownRequests } = coverage;
  const complete = partialRequests + missingRequests + unknownRequests === 0;
  const hasMeasurement = completeRequests + partialRequests > 0 || (toNumber(value) ?? 0) > 0;
  const completeness = complete ? "complete" : hasMeasurement ? "partial" : "missing";
  return {
    value: formatObservedTokens(value, completeness),
    note: i18n.t("usage.tokens.coverage", { completeRequests, partialRequests, missingRequests, unknownRequests }),
    complete,
  };
}
