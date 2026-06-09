import { useEffect, useMemo, useState } from "react";
import { getAgentQueue } from "../../api/agentApi";
import TicketQueueTable from "../../components/agent/TicketQueueTable";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";

export default function AgentQueuePage() {
  const [allTickets, setAllTickets] = useState([]);
  const [filters, setFilters] = useState({
    priority: "",
    status: "",
    sentiment: "",
    q: "",
  });
  const [loading, setLoading] = useState(false);

  const loadQueue = async () => {
    try {
      setLoading(true);
      const response = await getAgentQueue();
      setAllTickets(response.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const tickets = useMemo(() => {
    const q = filters.q.trim().toLowerCase();

    return allTickets.filter((ticket) => {
      const matchesPriority =
        !filters.priority || ticket.priority === filters.priority;

      const matchesStatus = !filters.status || ticket.status === filters.status;

      const matchesSentiment =
        !filters.sentiment || ticket.sentiment === filters.sentiment;

      const matchesSearch =
        !q ||
        String(ticket.subject || "").toLowerCase().includes(q) ||
        String(ticket.description || "").toLowerCase().includes(q) ||
        String(ticket.user_name || "").toLowerCase().includes(q);

      return (
        matchesPriority &&
        matchesStatus &&
        matchesSentiment &&
        matchesSearch
      );
    });
  }, [allTickets, filters]);

  const handleChange = (e) => {
    setFilters((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const resetFilters = () => {
    setFilters({
      priority: "",
      status: "",
      sentiment: "",
      q: "",
    });
  };

  return (
    <div className="sd-stack">
      <div className="sd-page-head">
        <h1 className="sd-display">Agent Queue</h1>
        <p className="sd-body">
          Your queue shows only tickets from your department and tickets assigned
          to you.
        </p>
      </div>

      <Card className="pad">
        <div className="sd-form-grid-5">
          <input
            className="sd-input"
            value="My Department Tickets"
            disabled
            title="Department access is controlled by your employee roster department."
          />

          <select
            name="priority"
            value={filters.priority}
            onChange={handleChange}
            className="sd-select"
          >
            <option value="">All Priorities</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            name="status"
            value={filters.status}
            onChange={handleChange}
            className="sd-select"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="ESCALATED">Escalated</option>
            <option value="CLOSED">Closed</option>
          </select>

          <select
            name="sentiment"
            value={filters.sentiment}
            onChange={handleChange}
            className="sd-select"
          >
            <option value="">All Sentiments</option>
            <option value="URGENT">Urgent</option>
            <option value="ANGRY">Angry</option>
            <option value="FRUSTRATED">Frustrated</option>
            <option value="CONFUSED">Confused</option>
            <option value="NEUTRAL">Neutral</option>
            <option value="CALM">Calm</option>
          </select>

          <input
            name="q"
            value={filters.q}
            onChange={handleChange}
            placeholder="Search tickets..."
            className="sd-input"
          />
        </div>

        <div className="sd-row sd-mt-4">
          <Button onClick={loadQueue} disabled={loading}>
            {loading ? "Loading..." : "Refresh Queue"}
          </Button>

          <Button variant="secondary" onClick={resetFilters}>
            Reset
          </Button>
        </div>
      </Card>

      <TicketQueueTable tickets={tickets} />
    </div>
  );
}