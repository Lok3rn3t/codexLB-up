import { screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { createApiKey } from "@/test/mocks/factories";
import { renderWithProviders } from "@/test/utils";

import { ApiKeysOverview } from "./api-keys-overview";

describe("ApiKeysOverview", () => {
  it("preserves complete measured totals when another key has never been used", () => {
    renderWithProviders(<ApiKeysOverview apiKeys={[
      createApiKey({ id: "used", usageSummary: { requestCount: 1, totalTokens: 130, cachedInputTokens: 0, totalCostUsd: 0,
        tokenUsage: { completeRequests: 1, partialRequests: 0, missingRequests: 0, unknownRequests: 0 } } }),
      createApiKey({ id: "unused", usageSummary: null }),
    ]} />);
    const requests = screen.getByTestId("api-keys-overview-stat-lifetime-requests");
    expect(requests).toHaveTextContent("130 tokens");
    expect(requests).not.toHaveTextContent("≥");
    expect(requests).toHaveTextContent("1 complete · 0 partial · 0 missing · 0 unknown");
  });

  it.each([
    ["complete", { completeRequests: 1, partialRequests: 0, missingRequests: 0, unknownRequests: 0 }, "0 tokens"],
    ["partial", { completeRequests: 0, partialRequests: 1, missingRequests: 0, unknownRequests: 0 }, "≥ 0 tokens"],
    ["missing", { completeRequests: 0, partialRequests: 0, missingRequests: 1, unknownRequests: 0 }, "Usage unavailable"],
  ])("distinguishes %s zero-token summaries", (_label, tokenUsage, expected) => {
    renderWithProviders(<ApiKeysOverview apiKeys={[
      createApiKey({ usageSummary: { requestCount: 1, totalTokens: 0, cachedInputTokens: 0, totalCostUsd: 0, tokenUsage } }),
    ]} />);
    const panel = screen.getByTestId("api-keys-overview-tokens-panel");
    expect(panel).toHaveTextContent(expected);
    if (expected !== "Usage unavailable") expect(panel).not.toHaveTextContent("Usage unavailable");
  });

  it("marks known token totals as partial when another key has missing usage", () => {
    renderWithProviders(<ApiKeysOverview apiKeys={[
      createApiKey({ id: "partial", usageSummary: { requestCount: 1, totalTokens: 130, cachedInputTokens: 40, totalCostUsd: 0,
        tokenUsage: { completeRequests: 0, partialRequests: 1, missingRequests: 0, unknownRequests: 0 } } }),
      createApiKey({ id: "missing", usageSummary: { requestCount: 1, totalTokens: 0, cachedInputTokens: 0, totalCostUsd: 0,
        tokenUsage: { completeRequests: 0, partialRequests: 0, missingRequests: 1, unknownRequests: 0 } } }),
    ]} />);
    const requests = screen.getByTestId("api-keys-overview-stat-lifetime-requests");
    expect(requests).toHaveTextContent("≥ 130 tokens");
    expect(requests).toHaveTextContent("0 complete · 1 partial · 1 missing · 0 unknown");
    expect(screen.getByTestId("api-keys-overview-tokens-panel")).toHaveTextContent("≥ 130");
  });

  it("summarizes the full key set and breaks usage down by metric", () => {
    renderWithProviders(
      <ApiKeysOverview
        apiKeys={[
          createApiKey({
            id: "key_1",
            name: "Primary key",
            keyPrefix: "sk-primary",
            usageSummary: {
              requestCount: 300,
              totalTokens: 80_000,
              cachedInputTokens: 12_000,
              totalCostUsd: 2.5,
            },
          }),
          createApiKey({
            id: "key_2",
            name: "Secondary key",
            keyPrefix: "sk-secondary",
            isActive: false,
            usageSummary: {
              requestCount: 120,
              totalTokens: 20_000,
              cachedInputTokens: 2_000,
              totalCostUsd: 1.0,
            },
          }),
        ]}
      />,
    );

    expect(screen.getByText("Overview")).toBeInTheDocument();
    expect(screen.getByTestId("api-keys-overview-stat-api-keys")).toHaveTextContent("2");
    expect(screen.getByTestId("api-keys-overview-stat-active-keys")).toHaveTextContent("1");
    expect(screen.getByTestId("api-keys-overview-stat-used-keys")).toHaveTextContent("2");
    expect(screen.getByTestId("api-keys-overview-stat-lifetime-requests")).toHaveTextContent("420");
    expect(screen.getByTestId("api-keys-overview-stat-lifetime-cost")).toHaveTextContent("$3.50");

    expect(screen.getByText("Lifetime Cost by API Key")).toBeInTheDocument();
    expect(screen.getByText("Lifetime Tokens by API Key")).toBeInTheDocument();

    const costPanel = screen.getByTestId("api-keys-overview-cost-panel");
    expect(within(costPanel).getByText("Primary key")).toBeInTheDocument();
    expect(within(costPanel).getByText("Secondary key")).toBeInTheDocument();
  });
});
