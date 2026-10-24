import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { chartTheme, tooltipStyle } from "./chartTheme";

export default function ErrorTimeChart({ rows }) {
  const data = rows.map((row) => ({
    label: row.start_time.slice(0, 16).replace("T", " "),
    error: row.forecast_error_mw,
  }));
  return (
    <div className="chart-frame" role="img" aria-label="Forecast error over time">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 12, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid stroke={chartTheme.grid} vertical={false} />
          <XAxis dataKey="label" tick={{ fill: chartTheme.axis, fontSize: 11 }} minTickGap={24} />
          <YAxis tick={{ fill: chartTheme.axis, fontSize: 11 }} label={{ value: "MW", angle: -90, position: "insideLeft", fill: chartTheme.axis }} />
          <ReferenceLine y={0} stroke="#555" />
          <Tooltip contentStyle={tooltipStyle} formatter={(value) => `${value} MW`} />
          <Line type="monotone" dataKey="error" name="Forecast error" stroke={chartTheme.actual} dot={false} strokeWidth={1.4} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
