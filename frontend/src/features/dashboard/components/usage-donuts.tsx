import { lazy, Suspense, useMemo } from "react";
import { useTranslation } from "react-i18next";

import type { DonutChartProps } from "@/components/donut-chart";
import type { RemainingItem, SafeLineView } from "@/features/dashboard/utils";
import { formatPercentNullable } from "@/utils/formatters";

const DonutChart = lazy(() =>
  import("@/components/donut-chart").then((module) => ({
    default: (props: DonutChartProps) => <module.DonutChart {...props} />,
  })),
);

export type UsageDonutsProps = {
	primaryItems: RemainingItem[];
	secondaryItems: RemainingItem[];
	safeLinePrimary?: SafeLineView | null;
	safeLineSecondary?: SafeLineView | null;
};

export function UsageDonuts({
	primaryItems,
	secondaryItems,
	safeLinePrimary,
	safeLineSecondary,
}: UsageDonutsProps) {
	const { t } = useTranslation();
	const primaryChartItems = useMemo(
		() =>
			primaryItems.map((item) => ({
				id: item.accountId,
				label: item.label,
				labelSuffix: item.labelSuffix,
				isEmail: item.isEmail,
				value: item.value,
				color: item.color,
			})),
		[primaryItems],
	);
	const secondaryChartItems = useMemo(
		() =>
			secondaryItems.map((item) => ({
				id: item.accountId,
				label: item.label,
				labelSuffix: item.labelSuffix,
				isEmail: item.isEmail,
				value: item.value,
				color: item.color,
			})),
		[secondaryItems],
	);

	return (
		<Suspense fallback={<div className="grid gap-4 lg:grid-cols-2" />}>
			<div className="grid min-w-0 gap-4 lg:grid-cols-2">
				<DonutChart
					title={t("usage.quota.fiveHour")}
					items={primaryChartItems}
					total={primaryChartItems.length * 100}
					subtitle={t("usage.quota.averageNote")}
					estimate={safeLinePrimary && t("usage.quota.safeEstimate", { percent: formatPercentNullable(safeLinePrimary.safePercent, 2) })}
					centerLayout="percent"
				/>
				<DonutChart
					title={t("usage.quota.weekly")}
					items={secondaryChartItems}
					total={secondaryChartItems.length * 100}
					subtitle={t("usage.quota.averageNote")}
					estimate={safeLineSecondary && t("usage.quota.safeEstimate", { percent: formatPercentNullable(safeLineSecondary.safePercent, 2) })}
					centerLayout="percent"
				/>
			</div>
		</Suspense>
	);
}
