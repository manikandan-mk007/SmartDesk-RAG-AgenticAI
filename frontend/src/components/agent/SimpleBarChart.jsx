import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function SimpleBarChart({ data = [], title }) {
  return (
    <div className="sd-card pad">
      <h3 className="sd-heading-sm sd-mb-4">{title}</h3>

      {data.length === 0 ? (
        <p className="sd-body sd-muted">No data available.</p>
      ) : (
        <div className="sd-chart-box">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e2e2" />
              <XAxis dataKey="label" fontSize={12} stroke="#747878" />
              <YAxis allowDecimals={false} fontSize={12} stroke="#747878" />
              <Tooltip />
              <Bar dataKey="count" radius={[6, 6, 0, 0]} fill="#1c1b1b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}