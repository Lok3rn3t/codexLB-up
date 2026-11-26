import { describe, expect, it } from "vitest";
import { formatPurchasedCredits } from "@/features/dashboard/account-credit-display";
import { createAccountSummary } from "@/test/mocks/factories";

describe("reported credit balance", () => {
  it("preserves reported balances and distinguishes unknown from measured zero", () => {
    expect(formatPurchasedCredits(createAccountSummary({ creditsBalance: 42.5 }), "Unlimited")).toBe("42.50");
    expect(formatPurchasedCredits(createAccountSummary({ creditsBalance: 0 }), "Unlimited")).toBe("0.00");
    expect(formatPurchasedCredits(createAccountSummary({ creditsBalance: null }), "Unlimited")).toBe("-");
  });
  it("shows unlimited only when the upstream flag is set", () => {
    expect(formatPurchasedCredits(createAccountSummary({ creditsUnlimited: true, creditsBalance: null }), "Unlimited")).toBe("Unlimited");
  });
});
