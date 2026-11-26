import { z } from "zod";

export const TokenUsageCoverageSchema = z.object({
  completeRequests: z.number().int().nonnegative(),
  partialRequests: z.number().int().nonnegative(),
  missingRequests: z.number().int().nonnegative(),
  unknownRequests: z.number().int().nonnegative(),
});

export type TokenUsageCoverage = z.infer<typeof TokenUsageCoverageSchema>;
