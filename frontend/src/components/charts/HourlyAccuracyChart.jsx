import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { chartTheme, tooltipStyle } from "./chartTheme";

export default function HourlyAccuracyChart({ rows }) {
  const data = rows.map((row) => ({
    ...row,
    label: `${String(row.hour_ending_utc).padStart(2, "0")}:00`,
  }));
  return (
    <div className="chart-frame" role="img" aria-label="Time of day mean absolute error">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 12, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid stroke={chartTheme.grid} vertical={false} />
          <XAxis dataKey="label" tick={{ fill: chartTheme.axis, fontSize: 10 }} />
          <YAxis tick={{ fill: chartTheme.axis, fontSize: 11 }} label={{ value: "MAE MW", angle: -90, position: "insideLeft", fill: chartTheme.axis }} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="mae_mw" name="MAE" fill={chartTheme.forecast} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
