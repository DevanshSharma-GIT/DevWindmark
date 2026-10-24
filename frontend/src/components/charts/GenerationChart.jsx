import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { chartTheme, tooltipStyle } from "./chartTheme";

export default function GenerationChart({ rows }) {
  const data = rows.map((row) => ({
    ...row,
    label: row.start_time.slice(0, 16).replace("T", " "),
  }));
  return (
    <div className="chart-frame" role="img" aria-label="Actual and forecast wind generation in megawatts">
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={data} margin={{ top: 12, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid stroke={chartTheme.grid} vertical={false} />
          <XAxis dataKey="label" tick={{ fill: chartTheme.axis, fontSize: 11 }} minTickGap={24} />
          <YAxis
            tick={{ fill: chartTheme.axis, fontSize: 11 }}
            label={{ value: "MW", angle: -90, position: "insideLeft", fill: chartTheme.axis }}
          />
          <Tooltip contentStyle={tooltipStyle} formatter={(value) => (value == null ? "Missing" : `${value} MW`)} />
          <Legend />
          <Line type="monotone" dataKey="actual_generation_mw" name="Actual" stroke={chartTheme.actual} dot={false} strokeWidth={1.6} connectNulls={false} />
          <Line type="monotone" dataKey="forecast_generation_mw" name="Selected forecast" stroke={chartTheme.forecast} dot={false} strokeWidth={1.6} connectNulls={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
