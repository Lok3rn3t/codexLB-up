import type { AccountSummary } from "@/features/dashboard/schemas";

export function estimatedSubscriptionCredits(account: AccountSummary): number | null {
  if (account.windowMinutesPrimary == null) {
    if (account.windowMinutesSecondary != null) return account.remainingCreditsSecondary ?? null;
    if (account.windowMinutesMonthly != null) return account.remainingCreditsMonthly ?? null;
  }
  return account.remainingCreditsSecondary ?? account.remainingCreditsPrimary ?? null;
}

export function formatCreditValue(value: number | null | undefined): string {
  return value == null ? "-" : value.toFixed(2);
}

export function formatPurchasedCredits(account: AccountSummary, unlimitedLabel: string): string {
  if (account.creditsUnlimited) {
    return unlimitedLabel;
  }
  return formatCreditValue(account.creditsBalance);
}
