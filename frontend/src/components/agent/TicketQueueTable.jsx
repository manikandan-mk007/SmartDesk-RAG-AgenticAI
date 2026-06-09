import { Link } from "react-router-dom";
import { formatDateTime } from "../../utils/formatDate";
import StatusBadge from "../common/StatusBadge";

export default function TicketQueueTable({ tickets = [] }) {
  return (
    <CardlessQueueTable tickets={tickets} />
  );
}

function CardlessQueueTable({ tickets }) {
  return (
    <div className="sd-card">
      <div className="sd-table-wrap">
        <table className="sd-table">
          <thead>
            <tr>
              <th>Req Type</th>
              <th>Priority</th>
              <th>Subject</th>
              <th>Status</th>
              <th>Sentiment</th>
              <th>Created</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {tickets.map((ticket) => (
              <tr key={ticket.id}>
                <td style={{ color: "var(--primary)", fontWeight: 700 }}>{ticket.request_type}</td>
                <td><StatusBadge status={ticket.priority} /></td>
                <td>
                  <p className="sd-ticket-title">{ticket.subject}</p>
                  <p className="sd-body sd-muted sd-line-1">{ticket.description}</p>
                </td>
                <td><StatusBadge status={ticket.status} /></td>
                <td>{ticket.sentiment}</td>
                <td>{formatDateTime(ticket.created_at)}</td>
                <td>
                  <Link className="sd-btn sd-btn-primary" to={`/agent/tickets/${ticket.id}`}>
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {tickets.length === 0 && (
          <div style={{ padding: 32, textAlign: "center" }}>
            <p className="sd-body sd-muted">No tickets found for selected filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}