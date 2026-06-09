export default function QueueTrendCard({ data = [] }) {
  const fallback = [
    { label: "08:00", count: 2 },
    { label: "09:00", count: 3 },
    { label: "10:00", count: 5 },
    { label: "11:00", count: 4 },
    { label: "12:00", count: 6 },
    { label: "13:00", count: 3 },
    { label: "14:00", count: 7 },
    { label: "15:00", count: 5 },
    { label: "16:00", count: 4 },
    { label: "17:00", count: 6 },
    { label: "18:00", count: 2 },
  ];

  const trend = data.length ? data : fallback;
  const max = Math.max(...trend.map((item) => item.count), 1);

  return (
    <div className="sd-card pad sd-queue-trend-card">
      <div className="sd-row-between">
        <h3 className="sd-heading-sm">Queue Trend</h3>

        <div className="sd-dashboard-pill-group">
          <span className="sd-dashboard-pill active">Hourly</span>
          <span className="sd-dashboard-pill">Daily</span>
        </div>
      </div>

      <div className="sd-queue-trend-chart">
        {trend.map((item, index) => {
          const height = Math.max((item.count / max) * 165, 22);
          const isDark = item.count >= max * 0.75 || index % 4 === 2;

          return (
            <div key={`${item.label}-${index}`} className="sd-queue-trend-bar-wrap">
              <div
                className={`sd-queue-trend-bar ${isDark ? "dark" : "light"}`}
                style={{ height: `${height}px` }}
              />
              <span className="sd-queue-trend-label">{item.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}