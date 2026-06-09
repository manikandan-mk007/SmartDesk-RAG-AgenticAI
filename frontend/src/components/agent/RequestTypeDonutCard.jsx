function buildRequestTypeData(data = []) {
  const findCount = (key) =>
    data.find((item) => String(item.label).toUpperCase() === key)?.count || 0;

  const items = [
    { label: "IT Support", short: "IT", count: findCount("IT"), color: "#000000" },
    { label: "Human Resources", short: "HR", count: findCount("HR"), color: "#cfcfcf" },
    { label: "Facilities", short: "FACILITIES", count: findCount("FACILITIES"), color: "#e9e9e9" },
  ];

  return items;
}

export default function RequestTypeDonutCard({ data = [] }) {
  const items = buildRequestTypeData(data);
  const total = items.reduce((sum, item) => sum + item.count, 0) || 1;

  const dominant = [...items].sort((a, b) => b.count - a.count)[0];
  const dominantPercent = Math.round((dominant.count / total) * 100);

  let start = 0;
  const segments = items.map((item) => {
    const percent = (item.count / total) * 100;
    const segment = `${item.color} ${start}% ${start + percent}%`;
    start += percent;
    return segment;
  });

  const donutStyle = {
    background: `conic-gradient(${segments.join(", ")})`,
  };

  return (
    <div className="sd-card pad sd-dashboard-small-card">
      <h3 className="sd-heading-sm">Request Type</h3>

      <div className="sd-request-type-center">
        <div className="sd-request-donut" style={donutStyle}>
          <div className="sd-request-donut-inner">
            <div className="sd-request-donut-value">{dominantPercent}%</div>
            <div className="sd-request-donut-label">{dominant.label}</div>
          </div>
        </div>
      </div>

      <div className="sd-request-type-legend">
        {items.map((item) => {
          const percent = Math.round((item.count / total) * 100);

          return (
            <div key={item.short} className="sd-request-legend-row">
              <div className="sd-row" style={{ gap: 8 }}>
                <span
                  className="sd-request-legend-dot"
                  style={{ background: item.color }}
                />
                <span className="sd-body">{item.label}</span>
              </div>
              <span className="sd-body" style={{ fontWeight: 700 }}>{percent}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}