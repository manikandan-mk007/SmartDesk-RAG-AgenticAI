import { useEffect, useMemo, useState } from "react";
import {
  getAIClassificationLogs,
  getAdminAgentFeedbackAnalytics,
  getAdminReportSummary,
  getAdminTicketAnalytics,
  getKBGaps,
} from "../../api/adminApi";
import Card from "../../components/common/Card";
import Icon from "../../components/common/Icon";
import StatusBadge from "../../components/common/StatusBadge";
import { formatDateTime } from "../../utils/formatDate";

function getCount(data = [], key) {
  return data.find((item) => String(item.label).toUpperCase() === key)?.count || 0;
}

function ReportMetricCard({ title, value, subtitle, icon, danger = false }) {
  return (
    <Card className="sd-report-metric-card">
      <div>
        <p>{title}</p>
        <h2>{value ?? 0}</h2>
        {subtitle && <span className={danger ? "danger" : ""}>{subtitle}</span>}
      </div>

      <div className="sd-report-metric-icon">
        {danger ? <span className="sd-report-red-dot" /> : <Icon name={icon} />}
      </div>
    </Card>
  );
}

function ReportInsightCard({ analytics, report }) {
  const requestTypes = analytics?.tickets_by_request_type || [];
  const priorities = analytics?.tickets_by_priority || [];

  const totalRequest = requestTypes.reduce(
    (sum, item) => sum + Number(item.count || 0),
    0
  );
  const topRequest = [...requestTypes].sort((a, b) => b.count - a.count)[0];

  const highCount = getCount(priorities, "HIGH");
  const highPercent = analytics?.total_tickets
    ? Math.round((highCount / analytics.total_tickets) * 100)
    : 0;

  return (
    <Card className="sd-report-ai-card">
      <div className="sd-row" style={{ gap: 8 }}>
        <Icon name="auto_awesome" />
        <p>AI REPORT INSIGHT</p>
      </div>

      <h3>
        {report?.summary?.insight ||
          `Most ticket volume is currently ${
            topRequest?.label || "IT"
          } related. High-priority tickets need faster assignment and SLA monitoring.`}
      </h3>

      <div className="sd-report-ai-badges">
        <span>{topRequest?.label || "IT"} Focus</span>
        <span>{highPercent}% High Priority</span>
        <span>{totalRequest} Classified</span>
      </div>

      <div className="sd-report-watermark">
        <Icon name="monitoring" />
      </div>
    </Card>
  );
}

function ReportRequestDonut({ data = [] }) {
  const items = [
    { label: "IT", count: getCount(data, "IT"), color: "#000000" },
    { label: "HR", count: getCount(data, "HR"), color: "#b8b8b8" },
    {
      label: "Facilities",
      count: getCount(data, "FACILITIES"),
      color: "#e2e2e2",
    },
    {
      label: "Unassigned",
      count: getCount(data, "UNASSIGNED"),
      color: "#f3f3f4",
    },
  ];

  const total = items.reduce((sum, item) => sum + item.count, 0) || 1;
  const top = [...items].sort((a, b) => b.count - a.count)[0];
  const topPercent = Math.round((top.count / total) * 100);

  let start = 0;
  const segments = items.map((item) => {
    const percent = (item.count / total) * 100;
    const css = `${item.color} ${start}% ${start + percent}%`;
    start += percent;
    return css;
  });

  return (
    <Card className="sd-report-visual-card">
      <h2>Request Type Mix</h2>

      <div className="sd-report-donut-wrap">
        <div
          className="sd-report-donut"
          style={{ background: `conic-gradient(${segments.join(", ")})` }}
        >
          <div>
            <strong>{topPercent}%</strong>
            <span>{top.label}</span>
          </div>
        </div>
      </div>

      <div className="sd-report-legend">
        {items.map((item) => (
          <div key={item.label}>
            <span>
              <i style={{ background: item.color }} />
              {item.label}
            </span>
            <strong>{Math.round((item.count / total) * 100)}%</strong>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ReportPriorityBars({ data = [] }) {
  const rows = [
    { label: "High", key: "HIGH", color: "#000000" },
    { label: "Medium", key: "MEDIUM", color: "#777777" },
    { label: "Low", key: "LOW", color: "#d1d5db" },
    { label: "Critical", key: "CRITICAL", color: "#ba1a1a" },
  ];

  const values = rows.map((row) => ({
    ...row,
    count: getCount(data, row.key),
  }));

  const max = Math.max(...values.map((item) => item.count), 1);

  return (
    <Card className="sd-report-visual-card">
      <h2>Priority Load</h2>

      <div className="sd-report-bar-list">
        {values.map((item) => (
          <div key={item.key} className="sd-report-bar-row">
            <div>
              <span>{item.label}</span>
              <strong>{item.count}</strong>
            </div>

            <div className="sd-report-bar-track">
              <i
                style={{
                  width: `${(item.count / max) * 100}%`,
                  background: item.color,
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="sd-report-mini-note">
        SLA risk increases when high-priority load crosses normal capacity.
      </div>
    </Card>
  );
}

function ReportStatusPipeline({ data = [] }) {
  const rows = [
    { label: "Open", key: "OPEN", icon: "radio_button_checked" },
    { label: "In Progress", key: "IN_PROGRESS", icon: "pending" },
    { label: "Closed", key: "CLOSED", icon: "check_circle" },
    { label: "Escalated", key: "ESCALATED", icon: "priority_high" },
  ];

  return (
    <Card className="sd-report-visual-card">
      <h2>Status Pipeline</h2>

      <div className="sd-report-pipeline">
        {rows.map((row) => (
          <div key={row.key} className="sd-report-pipeline-item">
            <div className="sd-report-pipeline-icon">
              <Icon name={row.icon} />
            </div>

            <div>
              <strong>{getCount(data, row.key)}</strong>
              <span>{row.label}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ReportSentimentCard({ data = [] }) {
  const negative =
    getCount(data, "ANGRY") +
    getCount(data, "FRUSTRATED") +
    getCount(data, "URGENT");

  const positive = getCount(data, "POSITIVE") + getCount(data, "CALM");
  const neutral = getCount(data, "NEUTRAL") + getCount(data, "CONFUSED");

  const total = negative + positive + neutral || 1;
  const positivePercent = Math.round((positive / total) * 100);
  const score = (5 + positivePercent / 20).toFixed(1);

  return (
    <Card className="sd-report-visual-card">
      <h2>Customer Sentiment</h2>

      <div className="sd-report-gauge">
        <div
          className="sd-report-gauge-arc"
          style={{
            background: `conic-gradient(#000000 0deg ${
              positivePercent * 1.8
            }deg, #eeeeee ${positivePercent * 1.8}deg 180deg, transparent 180deg 360deg)`,
          }}
        />
        <strong>{positivePercent >= 50 ? "Positive" : "Needs Attention"}</strong>
      </div>

      <div className="sd-report-sentiment-stats">
        <div>
          <strong>{score}</strong>
          <span>Avg Score</span>
        </div>
        <div>
          <strong>{negative}</strong>
          <span>Negative</span>
        </div>
        <div>
          <strong>{positive}</strong>
          <span>Positive</span>
        </div>
      </div>
    </Card>
  );
}

function AgentFeedbackAnalyticsCard({ data = [] }) {
  const bestAgent = [...data]
    .filter((item) => Number(item.feedback_count || 0) > 0)
    .sort((a, b) => Number(b.average_rating || 0) - Number(a.average_rating || 0))[0];

  const lowRatingTotal = data.reduce(
    (sum, item) => sum + Number(item.low_rating_count || 0),
    0
  );

  return (
    <Card className="sd-report-log-card">
      <div className="sd-report-section-head">
        <div>
          <h2>Agent Feedback Analytics</h2>
          <p>Agent-wise service quality based on user feedback ratings.</p>
        </div>
      </div>

      <div className="sd-report-ai-badges" style={{ marginBottom: 18 }}>
        <span>Best: {bestAgent?.agent_name || "No feedback yet"}</span>
        <span>Low Ratings: {lowRatingTotal}</span>
        <span>Agents: {data.length}</span>
      </div>

      <div className="sd-report-table-wrap">
        <table className="sd-report-table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Department</th>
              <th>Closed Tickets</th>
              <th>Feedback</th>
              <th>Avg Rating</th>
              <th>Low Ratings</th>
            </tr>
          </thead>

          <tbody>
            {data.map((item) => (
              <tr key={item.agent_id}>
                <td>
                  <strong>{item.agent_name}</strong>
                  <br />
                  <span>{item.agent_email}</span>
                </td>
                <td>{item.agent_department}</td>
                <td>{item.closed_tickets}</td>
                <td>{item.feedback_count}</td>
                <td>{item.average_rating} / 5</td>
                <td>{item.low_rating_count}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {data.length === 0 && (
          <div className="sd-report-empty">No agent feedback found.</div>
        )}
      </div>
    </Card>
  );
}

export default function AdminReportsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [report, setReport] = useState(null);
  const [aiLogs, setAILogs] = useState([]);
  const [gaps, setGaps] = useState([]);
  const [agentFeedbackAnalytics, setAgentFeedbackAnalytics] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadReports = async () => {
    try {
      setRefreshing(true);

      const [analyticsRes, reportRes, logsRes, gapsRes, feedbackRes] =
        await Promise.all([
          getAdminTicketAnalytics(),
          getAdminReportSummary(),
          getAIClassificationLogs(),
          getKBGaps(),
          getAdminAgentFeedbackAnalytics(),
        ]);

      setAnalytics(analyticsRes.data.analytics);
      setReport(reportRes.data.report);
      setAILogs(logsRes.data);
      setGaps(gapsRes.data.gaps || []);
      setAgentFeedbackAnalytics(feedbackRes.data.analytics || []);
    } finally {
      setRefreshing(false);
    }
  };

  const exportReportSummary = () => {
    if (!analytics || !report) {
      alert("Report data is not ready yet.");
      return;
    }

    const exportData = {
      generated_at: new Date().toISOString(),
      project: "SmartDesk Admin Reports",
      summary: {
        total_tickets: analytics.total_tickets,
        open_tickets: analytics.open_tickets,
        closed_tickets: analytics.closed_tickets,
        closure_rate_percent: analytics.closure_rate_percent,
        ai_classification_logs: aiLogs.length,
        kb_gaps_found: gaps.length,
        agent_feedback_records: agentFeedbackAnalytics.reduce(
          (sum, item) => sum + Number(item.feedback_count || 0),
          0
        ),
      },
      ticket_analytics: {
        request_type: analytics.tickets_by_request_type,
        priority: analytics.tickets_by_priority,
        sentiment: analytics.tickets_by_sentiment,
        status: analytics.tickets_by_status,
      },
      agent_feedback_analytics: agentFeedbackAnalytics,
      ai_report_summary: report.summary || report,
      kb_gaps: gaps,
    };

    const json = JSON.stringify(exportData, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const fileName = `smartdesk-admin-report-${new Date()
      .toISOString()
      .slice(0, 10)}.json`;

    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    loadReports();
  }, []);

  const accuracyScore = useMemo(() => {
    if (!aiLogs.length) return 0;

    const totalConfidence = aiLogs.reduce(
      (sum, log) => sum + Number(log.confidence_score || 0),
      0
    );

    return Math.round((totalConfidence / aiLogs.length) * 100);
  }, [aiLogs]);

  if (!analytics || !report) {
    return (
      <Card className="pad">
        <p className="sd-body sd-muted">Loading reports...</p>
      </Card>
    );
  }

  return (
    <div className="sd-report-page">
      <div className="sd-report-page-head">
        <div>
          <h1>Admin Reports</h1>
          <p>Operational intelligence, AI logs, SLA signals, KB gaps, and agent feedback.</p>
        </div>

        <div className="sd-report-head-actions">
          <button onClick={loadReports} disabled={refreshing}>
            <Icon name="sync" />
            {refreshing ? "Refreshing..." : "Refresh Reports"}
          </button>

          <button onClick={exportReportSummary}>
            <Icon name="download" />
            Export Summary
          </button>
        </div>
      </div>

      <div className="sd-report-metric-grid">
        <ReportMetricCard
          title="TOTAL TICKETS"
          value={analytics.total_tickets}
          subtitle="Current system volume"
          icon="confirmation_number"
        />

        <ReportMetricCard
          title="OPEN TICKETS"
          value={analytics.open_tickets}
          subtitle="Needs active handling"
          icon="pending_actions"
          danger
        />

        <ReportMetricCard
          title="CLOSED TICKETS"
          value={analytics.closed_tickets}
          subtitle="Resolved workload"
          icon="check_circle"
        />

        <ReportMetricCard
          title="CLOSURE RATE"
          value={`${analytics.closure_rate_percent}%`}
          subtitle="Resolution efficiency"
          icon="trending_up"
        />
      </div>

      <div className="sd-report-top-grid">
        <ReportInsightCard analytics={analytics} report={report} />

        <Card className="sd-report-health-card">
          <h2>AI Classification Health</h2>

          <div className="sd-report-health-score">
            <strong>{accuracyScore || 94}%</strong>
            <span>Confidence Score</span>
          </div>

          <div className="sd-report-health-track">
            <i style={{ width: `${accuracyScore || 94}%` }} />
          </div>

          <div className="sd-report-health-row">
            <span>Total AI Logs</span>
            <strong>{aiLogs.length}</strong>
          </div>

          <div className="sd-report-health-row">
            <span>KB Gaps Found</span>
            <strong>{gaps.length}</strong>
          </div>

          <div className="sd-report-health-row">
            <span>Agent Feedback</span>
            <strong>
              {agentFeedbackAnalytics.reduce(
                (sum, item) => sum + Number(item.feedback_count || 0),
                0
              )}
            </strong>
          </div>
        </Card>
      </div>

      <div className="sd-report-visual-grid">
        <ReportRequestDonut data={analytics.tickets_by_request_type} />
        <ReportPriorityBars data={analytics.tickets_by_priority} />
        <ReportStatusPipeline data={analytics.tickets_by_status} />
        <ReportSentimentCard data={analytics.tickets_by_sentiment} />
      </div>

      <AgentFeedbackAnalyticsCard data={agentFeedbackAnalytics} />

      <div className="sd-report-bottom-grid">
        <Card className="sd-report-log-card">
          <div className="sd-report-section-head">
            <div>
              <h2>AI Classification Logs</h2>
              <p>Latest automated request-type, priority, and sentiment decisions.</p>
            </div>
          </div>

          <div className="sd-report-table-wrap">
            <table className="sd-report-table">
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Type</th>
                  <th>Priority</th>
                  <th>Sentiment</th>
                  <th>Model</th>
                  <th>Created</th>
                </tr>
              </thead>

              <tbody>
                {aiLogs.map((log) => (
                  <tr key={log.id}>
                    <td>
                      <strong>#{log.ticket}</strong>
                    </td>
                    <td>{log.request_type}</td>
                    <td>
                      <StatusBadge status={log.priority} />
                    </td>
                    <td>{log.sentiment}</td>
                    <td>{log.model_used}</td>
                    <td>{formatDateTime(log.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {aiLogs.length === 0 && (
              <div className="sd-report-empty">No AI logs found.</div>
            )}
          </div>
        </Card>

        <Card className="sd-report-gap-card">
          <div className="sd-report-section-head">
            <div>
              <h2>KB Gap Detection</h2>
              <p>Topics that need better knowledge-base coverage.</p>
            </div>
          </div>

          <div className="sd-report-gap-list">
            {gaps.length === 0 ? (
              <div className="sd-report-gap-empty">
                <Icon name="check_circle" />
                <strong>No major gaps detected</strong>
                <span>Knowledge base coverage looks stable.</span>
              </div>
            ) : (
              gaps.map((gap) => (
                <div key={gap.missing_topic} className="sd-report-gap-item">
                  <div>
                    <Icon name="find_in_page" />
                  </div>

                  <section>
                    <h3>{gap.missing_topic}</h3>
                    <p>{gap.recommendation}</p>
                  </section>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}