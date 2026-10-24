import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import { chartTheme, tooltipStyle } from "./chartTheme";

export default function ScatterCompareChart({ rows }) {
  const data = rows.map((row) => ({
    actual: row.actual_generation_mw,
    forecast: row.forecast_generation_mw,
  }));
  return (
    <div className="chart-frame" role="img" aria-label="Forecast versus actual wind generation">
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart margin={{ top: 12, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid stroke={chartTheme.grid} />
          <XAxis
            type="number"
            dataKey="actual"
            name="Actual"
            unit=" MW"
            tick={{ fill: chartTheme.axis, fontSize: 11 }}
            label={{ value: "Actual MW", position: "insideBottom", offset: -4, fill: chartTheme.axis }}
          />
          <YAxis
            type="number"
            dataKey="forecast"
            name="Forecast"
            unit=" MW"
            tick={{ fill: chartTheme.axis, fontSize: 11 }}
            label={{ value: "Forecast MW", angle: -90, position: "insideLeft", fill: chartTheme.axis }}
          />
          <Tooltip contentStyle={tooltipStyle} cursor={{ stroke: "#333" }} />
          <Scatter data={data} fill="#d8d8d8" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
