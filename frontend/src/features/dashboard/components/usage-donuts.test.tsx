import { act, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TooltipProvider } from "@/components/ui/tooltip";
import { UsageDonuts } from "@/features/dashboard/components/usage-donuts";
import { usePrivacyStore } from "@/hooks/use-privacy";

function item(accountId: string, value: number) {
  return { accountId, label: `${accountId}@example.com`, value, remainingPercent: value, color: "#7bb661", labelSuffix: "", isEmail: true };
}

describe("UsageDonuts", () => {
  it("shows an equal-weight average of reported account percentages", async () => {
    render(<UsageDonuts primaryItems={[item("small", 80), item("large", 20)]} secondaryItems={[item("weekly", 0)]} />, { wrapper: TooltipProvider });
    expect(await screen.findByText("5-hour quota")).toBeInTheDocument();
    expect(screen.getByText("Weekly quota")).toBeInTheDocument();
    expect(screen.getAllByTestId("donut-center-average").map((node) => node.textContent)).toEqual(["50%", "0%"]);
    expect(screen.getByText("2 reporting accounts")).toBeInTheDocument();
    expect(screen.getByText("small@example.com")).toBeInTheDocument();
    expect(screen.getByText("80%")).toBeInTheDocument();
    expect(screen.queryByTestId("donut-center-capacity")).not.toBeInTheDocument();
  });

  it("shows unavailable instead of zero for windows without measurements", async () => {
    render(<UsageDonuts primaryItems={[]} secondaryItems={[]} />);
    expect(await screen.findByText("5-hour quota")).toBeInTheDocument();
    expect(screen.getAllByTestId("donut-center-average").map((node) => node.textContent)).toEqual(["--", "--"]);
    expect(screen.getAllByText("0 reporting accounts")).toHaveLength(2);
    expect(screen.queryByText(/Plan-capacity estimate/)).not.toBeInTheDocument();
  });

  it("keeps the plan-capacity safe usage forecast explicitly separate from measured averages", async () => {
    render(<UsageDonuts primaryItems={[item("primary", 60.22499), item("other", 60.33499)]} secondaryItems={[item("weekly", 40)]}
      safeLinePrimary={{ safePercent: 30.854312, riskLevel: "warning" }}
      safeLineSecondary={{ safePercent: 20.100001, riskLevel: "danger" }} />, { wrapper: TooltipProvider });
    expect(await screen.findByText("Plan-capacity estimate: safe usage 30.85%.")).toBeInTheDocument();
    expect(screen.getByText("Plan-capacity estimate: safe usage 20.1%.")).toBeInTheDocument();
    expect(screen.queryByTestId("safe-line-tick")).not.toBeInTheDocument();
    expect(screen.getByText("60.22%")).toBeInTheDocument();
    expect(screen.getByText("60.33%")).toBeInTheDocument();
    expect(screen.getAllByTestId("donut-center-average").map((node) => node.textContent)).toEqual(["60.28%", "40%"]);
    expect(screen.getAllByTestId("donut-used-value").map((node) => node.textContent)).toEqual(["39.72%", "60%"]);
  });

  it("conceals email identities in focused account details when privacy is enabled", async () => {
    usePrivacyStore.setState({ blurred: true });
    try {
      const { container } = render(
        <UsageDonuts primaryItems={[{ ...item("private", 93.433333), labelSuffix: " (acct-123)" }]} secondaryItems={[]} />,
        { wrapper: TooltipProvider },
      );
      const row = await screen.findByTestId("donut-legend-0");
      act(() => row.focus());
      expect(row).toHaveFocus();
      expect(await screen.findByRole("tooltip")).toHaveTextContent("•••••• (acct-123) · 93.43%");
      expect(container).not.toHaveTextContent("private@example.com");
    } finally {
      usePrivacyStore.setState({ blurred: false });
    }
  });
});
