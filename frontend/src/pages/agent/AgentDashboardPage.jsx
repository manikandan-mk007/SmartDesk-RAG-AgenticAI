import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getAgentDashboard,
  getAgentFeedbackSummary,
} from "../../api/agentApi";
import DashboardStatCard from "../../components/agent/DashboardStatCard";
import QueueTrendCard from "../../components/agent/QueueTrendCard";
import AIWorkloadInsightCard from "../../components/agent/AIWorkloadInsightCard";
import RequestTypeDonutCard from "../../components/agent/RequestTypeDonutCard";
import PriorityDistributionCard from "../../components/agent/PriorityDistributionCard";
import CustomerSentimentCard from "../../components/agent/CustomerSentimentCard";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import StatusBadge from "../../components/common/StatusBadge";
import { formatDateTime } from "../../utils/formatDate";

export default function AgentDashboardPage() {
  const [dashboard, setDashboard] = useState(null);
  const [feedbackSummary, setFeedbackSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadDashboard = async () => {
    try {
      setLoading(true);

      const [dashboardRes, feedbackRes] = await Promise.all([
        getAgentDashboard(),
        getAgentFeedbackSummary(),
      ]);

      setDashboard(dashboardRes.data.dashboard);
      setFeedbackSummary(feedbackRes.data.summary);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <Card className="pad">
        <p className="sd-body sd-muted">Loading agent dashboard...</p>
      </Card>
    );
  }

  const cards = dashboard?.cards || {};
  const charts = dashboard?.charts || {};
  const recentTickets = dashboard?.recent_tickets || [];
  const requestTypeData = charts.tickets_by_request_type || [];
  const priorityData = charts.tickets_by_priority || [];
  const sentimentData = charts.tickets_by_sentiment || [];
  const queueTrendData = charts.queue_trend || [];
  const latestFeedback = feedbackSummary?.latest_feedback || [];

  return (
    <div className="sd-stack">
      <div className="sd-row-between sd-page-head">
        <div>
          <h1 className="sd-display">Overview</h1>
          <p className="sd-body">
            System performance, ticket allocation, and customer feedback for today.
          </p>
        </div>

        <Link to="/agent/queue">
          <Button>View Queue</Button>
        </Link>
      </div>

      <div className="sd-stat-grid">
        <DashboardStatCard
          title="Total Tickets"
          value={cards.total_tickets}
          icon="confirmation_number"
        />
        <DashboardStatCard
          title="Open Tickets"
          value={cards.open_tickets}
          icon="pending_actions"
        />
        <DashboardStatCard
          title="Closed Tickets"
          value={cards.closed_tickets}
          icon="check_circle"
        />
        <DashboardStatCard
          title="Today"
          value={cards.today_queue_count}
          icon="today"
        />
      </div>


      <div className="sd-dashboard-visual-top">
        <QueueTrendCard data={queueTrendData} />
        <AIWorkloadInsightCard
          insight={dashboard?.ai_workload_insight}
          requestTypeData={requestTypeData}
          priorityData={priorityData}
        />
      </div>


      <div className="sd-dashboard-visual-bottom">
        <RequestTypeDonutCard data={requestTypeData} />
        <PriorityDistributionCard data={priorityData} />
        <CustomerSentimentCard data={sentimentData} />
      </div>
      <Card className="pad">
        <div className="sd-row-between" style={{ alignItems: "flex-start" }}>
          <div>
            <h2 className="sd-heading-sm">My Feedback Performance</h2>
            <p className="sd-body sd-muted sd-mt-2">
              Ratings from users for tickets handled by you.
            </p>
          </div>

          <div className="sd-row" style={{ gap: 10, flexWrap: "wrap" }}>
            <div className="sd-mini-stat">
              <p className="sd-label sd-muted">Average Rating</p>
              <p className="sd-body-lg" style={{ fontWeight: 900 }}>
                {feedbackSummary?.average_rating || 0} / 5
              </p>
            </div>

            <div className="sd-mini-stat">
              <p className="sd-label sd-muted">Total Feedback</p>
              <p className="sd-body-lg" style={{ fontWeight: 900 }}>
                {feedbackSummary?.total_feedback || 0}
              </p>
            </div>

            <div className="sd-mini-stat">
              <p className="sd-label sd-muted">5 Star</p>
              <p className="sd-body-lg" style={{ fontWeight: 900 }}>
                {feedbackSummary?.five_star_count || 0}
              </p>
            </div>

            <div className="sd-mini-stat">
              <p className="sd-label sd-muted">Low Rating</p>
              <p className="sd-body-lg" style={{ fontWeight: 900 }}>
                {feedbackSummary?.low_rating_count || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="sd-table-wrap sd-mt-5">
          <table className="sd-table">
            <thead>
              <tr>
                <th>Ticket</th>
                <th>Rating</th>
                <th>Comment</th>
                <th>Created</th>
              </tr>
            </thead>

            <tbody>
              {latestFeedback.map((item) => (
                <tr key={item.id}>
                  <td style={{ color: "var(--primary)", fontWeight: 700 }}>
                    #{item.ticket} - {item.ticket_subject}
                  </td>
                  <td>{item.rating} / 5</td>
                  <td>{item.comments || "-"}</td>
                  <td>{formatDateTime(item.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {latestFeedback.length === 0 && (
            <p className="sd-body sd-muted" style={{ padding: 20 }}>
              No feedback received yet.
            </p>
          )}
        </div>
      </Card>

      <Card>
        <div className="sd-card-header">
          <h2 className="sd-heading-sm">Recent Tickets</h2>
        </div>

        <div className="sd-table-wrap">
          <table className="sd-table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Type</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>

            <tbody>
              {recentTickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td>
                    <Link
                      to={`/agent/tickets/${ticket.id}`}
                      style={{ color: "var(--primary)", fontWeight: 700 }}
                    >
                      {ticket.subject}
                    </Link>
                  </td>
                  <td>{ticket.request_type}</td>
                  <td>
                    <StatusBadge status={ticket.priority} />
                  </td>
                  <td>
                    <StatusBadge status={ticket.status} />
                  </td>
                  <td>{formatDateTime(ticket.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {recentTickets.length === 0 && (
            <p className="sd-body sd-muted" style={{ padding: 20 }}>
              No recent tickets found.
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}