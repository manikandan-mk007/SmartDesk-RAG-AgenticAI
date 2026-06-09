function getCount(data, key) {
  return data.find((item) => String(item.label).toUpperCase() === key)?.count || 0;
}

export default function PriorityDistributionCard({ data = [] }) {
  const items = [
    { label: "Critical", value: getCount(data, "CRITICAL"), color: "#c61f1f" },
    { label: "High", value: getCount(data, "HIGH"), color: "#444444" },
    { label: "Medium", value: getCount(data, "MEDIUM"), color: "#888888" },
    { label: "Low", value: getCount(data, "LOW"), color: "#d0d0d0" },
  ];

  const maxValue = Math.max(...items.map((item) => item.value), 1);

  return (
    <div className="sd-card pad sd-dashboard-small-card">
      <h3 className="sd-heading-sm">Priority Distribution</h3>

      <div className="sd-priority-list">
        {items.map((item) => (
          <div key={item.label} className="sd-priority-row">
            <div className="sd-row-between">
              <span className="sd-body">{item.label}</span>
              <span className="sd-body" style={{ fontWeight: 700 }}>{item.value}</span>
            </div>

            <div className="sd-priority-track">
              <div
                className="sd-priority-fill"
                style={{
                  width: `${(item.value / maxValue) * 100}%`,
                  background: item.color,
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="sd-sla-box">SLA Compliance: 94.2%</div>
    </div>
  );
}