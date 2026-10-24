import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { chartTheme, tooltipStyle } from "./chartTheme";

export default function ErrorDistributionChart({ bins }) {
  const data = bins.map((item) => ({
    ...item,
    label: `${item.bin_start_mw} to ${item.bin_end_mw}`,
  }));
  return (
    <div className="chart-frame" role="img" aria-label="Distribution of forecast error in megawatts">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 12, right: 16, left: 8, bottom: 32 }}>
          <CartesianGrid stroke={chartTheme.grid} vertical={false} />
          <XAxis dataKey="label" tick={{ fill: chartTheme.axis, fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={70} />
          <YAxis tick={{ fill: chartTheme.axis, fontSize: 11 }} allowDecimals={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="count" name="Intervals" fill={chartTheme.accent} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
