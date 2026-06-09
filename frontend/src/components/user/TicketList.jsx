import StatusBadge from "../common/StatusBadge";
import { formatDateTime } from "../../utils/formatDate";

export default function TicketList({
  tickets,
  selectedTicketId,
  onSelect,
  onNewTicket,
}) {
  return (
    <aside className="sd-ref-ticket-list">
      <div className="sd-ref-ticket-list-head">
        <h2>Ticket List</h2>

        <button className="sd-ref-new-ticket-btn" onClick={onNewTicket}>
          <span className="material-symbols-outlined">add</span>
          New Ticket
        </button>
      </div>

      <div className="sd-ref-ticket-list-scroll">
        {tickets.length === 0 ? (
          <div className="sd-ref-ticket-card">
            <p className="sd-body sd-muted">No tickets created yet.</p>
          </div>
        ) : (
          tickets.map((ticket) => (
            <button
              key={ticket.id}
              onClick={() => onSelect(ticket)}
              className={`sd-ref-ticket-card ${
                selectedTicketId === ticket.id ? "active" : ""
              }`}
            >
              <div className="sd-ref-ticket-card-top">
                <StatusBadge status={ticket.status} />
                <span>{formatDateTime(ticket.created_at)}</span>
              </div>

              <h3>{ticket.subject}</h3>

              <p>{ticket.description}</p>

              <div className="sd-ref-ticket-chip-row">
                <span>{ticket.request_type || "IT"}</span>
                {ticket.priority && <span>{ticket.priority}</span>}
              </div>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}