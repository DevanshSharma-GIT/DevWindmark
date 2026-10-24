import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { chartTheme, tooltipStyle } from "./chartTheme";

export default function DailyAccuracyChart({ rows }) {
  return (
    <div className="chart-frame" role="img" aria-label="Daily mean absolute error">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={rows} margin={{ top: 12, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid stroke={chartTheme.grid} vertical={false} />
          <XAxis dataKey="delivery_date" tick={{ fill: chartTheme.axis, fontSize: 10 }} minTickGap={8} />
          <YAxis tick={{ fill: chartTheme.axis, fontSize: 11 }} label={{ value: "MAE MW", angle: -90, position: "insideLeft", fill: chartTheme.axis }} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="mae_mw" name="MAE" fill={chartTheme.accent} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
