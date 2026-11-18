import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { UsageDonuts } from "@/features/dashboard/components/usage-donuts";

function item(accountId: string, value: number) {
  return { accountId, label: `${accountId}@example.com`, value, remainingPercent: value, color: "#7bb661", labelSuffix: "", isEmail: true };
}

describe("UsageDonuts", () => {
  it("shows an equal-weight average of reported account percentages", async () => {
    render(<UsageDonuts primaryItems={[item("small", 80), item("large", 20)]} secondaryItems={[item("weekly", 0)]} />);
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
  });

  it("keeps the plan-capacity safe usage forecast explicitly separate from measured averages", async () => {
    render(<UsageDonuts primaryItems={[item("primary", 60)]} secondaryItems={[item("weekly", 40)]}
      safeLinePrimary={{ safePercent: 30, riskLevel: "warning" }}
      safeLineSecondary={{ safePercent: 20, riskLevel: "danger" }} />);
    expect(await screen.findByText(/Plan-capacity estimate: safe usage 30%/)).toBeInTheDocument();
    expect(screen.getByText(/Plan-capacity estimate: safe usage 20%/)).toBeInTheDocument();
    expect(screen.queryByTestId("safe-line-tick")).not.toBeInTheDocument();
    expect(screen.getAllByTestId("donut-center-average").map((node) => node.textContent)).toEqual(["60%", "40%"]);
  });
});
