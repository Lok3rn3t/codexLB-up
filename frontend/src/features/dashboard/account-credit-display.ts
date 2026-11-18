import type { AccountSummary } from "@/features/dashboard/schemas";

export function formatCreditValue(value: number | null | undefined): string {
  return value == null ? "-" : value.toFixed(2);
}

export function formatPurchasedCredits(account: AccountSummary, unlimitedLabel: string): string {
  if (account.creditsUnlimited) {
    return unlimitedLabel;
  }
  return formatCreditValue(account.creditsBalance);
}
