import { describe, expect, it } from "vitest";
import { formatObservedTokens, summarizeTokenUsage } from "@/utils/token-usage";

describe("observed token usage", () => {
  it("distinguishes reported zero, partial totals, missing usage and legacy totals", () => {
    expect(formatObservedTokens(0, "complete")).toBe("0");
    expect(formatObservedTokens(130, "partial")).toBe("≥ 130");
    expect(formatObservedTokens(0, "missing")).toBe("--");
    expect(formatObservedTokens(null, "partial")).toBe("--");
    expect(formatObservedTokens(130)).toBe("≥ 130");
    expect(formatObservedTokens(1999, "partial")).toBe("≥ 1,999");
    expect(formatObservedTokens(1999)).toBe("≥ 1,999");
  });

  it.each([
    [0, [0, 0, 0, 0], "0", true],
    [0, [1, 0, 0, 0], "0", true],
    [150, [1, 0, 0, 0], "150", true],
    [130, [0, 1, 0, 0], "≥ 130", false],
    [150, [1, 0, 1, 0], "≥ 150", false],
    [0, [0, 0, 1, 0], "--", false],
    [100, [0, 0, 0, 2], "≥ 100", false],
    [0, [0, 0, 0, 2], "--", false],
  ] as const)("summarizes %s recorded tokens with coverage %j", (tokens, counts, value, complete) => {
    const [completeRequests, partialRequests, missingRequests, unknownRequests] = counts;
    expect(summarizeTokenUsage(tokens, { completeRequests, partialRequests, missingRequests, unknownRequests }))
      .toMatchObject({ value, complete });
  });

  it("does not treat legacy coverage as complete", () => {
    expect(summarizeTokenUsage(150)).toEqual({ value: "≥ 150", note: "Coverage unknown", complete: false });
  });
});
