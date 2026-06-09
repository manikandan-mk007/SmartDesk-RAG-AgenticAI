import Icon from "../common/Icon";

function normalizeLabel(label) {
  const map = {
    IT: "Infrastructure",
    HR: "Human Resources",
    FACILITIES: "Facilities",
  };

  return map[label] || label || "Infrastructure";
}

export default function AIWorkloadInsightCard({
  insight,
  requestTypeData = [],
  priorityData = [],
}) {
  const totalRequests = requestTypeData.reduce((sum, item) => sum + (item.count || 0), 0);
  const topRequest = [...requestTypeData].sort((a, b) => b.count - a.count)[0];

  const highPriority =
    priorityData.find((item) => String(item.label).toUpperCase() === "HIGH")?.count || 0;

  const requestPercent = totalRequests
    ? Math.round(((topRequest?.count || 0) / totalRequests) * 100)
    : 82;

  return (
    <div className="sd-card sd-ai-workload-card">
      <div className="sd-ai-workload-inner">
        <div className="sd-row" style={{ gap: 8 }}>
          <Icon name="auto_awesome" />
          <p className="sd-label" style={{ color: "rgba(255,255,255,0.92)" }}>
            AI WORKLOAD INSIGHT
          </p>
        </div>

        <p className="sd-ai-workload-text">
          {insight ||
            "Most tickets today are IT related. AI recommends flagging these issues for the infrastructure team."}
        </p>

        <div className="sd-ai-workload-badges">
          <span className="sd-ai-workload-badge">
            {normalizeLabel(topRequest?.label)} ({requestPercent}%)
          </span>
          <span className="sd-ai-workload-badge">
            {highPriority > 0 ? "High Urgency" : "Normal Urgency"}
          </span>
        </div>

        <div className="sd-ai-watermark">
          <Icon name="settings" />
        </div>
      </div>
    </div>
  );
}