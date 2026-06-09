import { useState } from "react";
import { formatDateTime } from "../../utils/formatDate";
import Icon from "../common/Icon";
import StatusBadge from "../common/StatusBadge";
import FeedbackModal from "./FeedbackModal";
import TicketThread from "./TicketThread";

function getMediaUrl(fileUrl) {
  if (!fileUrl) return "";

  if (fileUrl.startsWith("http://") || fileUrl.startsWith("https://")) {
    return fileUrl;
  }

  if (fileUrl.startsWith("/media/")) {
    return `http://127.0.0.1:8000${fileUrl}`;
  }

  return fileUrl;
}

function isImageAttachment(item) {
  const fileType = String(item.file_type || "").toUpperCase();
  const name = String(item.original_filename || item.file || "").toLowerCase();

  return (
    fileType === "IMAGE" ||
    name.endsWith(".png") ||
    name.endsWith(".jpg") ||
    name.endsWith(".jpeg") ||
    name.endsWith(".webp")
  );
}

function isVideoAttachment(item) {
  const fileType = String(item.file_type || "").toUpperCase();
  const name = String(item.original_filename || item.file || "").toLowerCase();

  return (
    fileType === "VIDEO" ||
    name.endsWith(".mp4") ||
    name.endsWith(".mov") ||
    name.endsWith(".webm")
  );
}

function isTicketClosed(ticket) {
  return String(ticket.status || "").toUpperCase() === "CLOSED";
}

function hasFeedback(ticket) {
  return Boolean(
    ticket.feedback ||
      ticket.user_feedback ||
      ticket.feedback_rating ||
      ticket.rating ||
      ticket.rating_submitted
  );
}

export default function TicketDetailPanel({ ticket, onRefresh }) {
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);

  if (!ticket) return null;

  const attachments = ticket.attachments || [];
  const closed = isTicketClosed(ticket);
  const feedbackSubmitted = hasFeedback(ticket);

  return (
    <div className="sd-ref-ticket-detail">
      <div className="sd-ref-ticket-detail-head">
        <div>
          <h1>{ticket.subject}</h1>

          <div className="sd-ref-ticket-meta">
            <span>#{ticket.ticket_number || `INC-${ticket.id}`}</span>
            <span>{formatDateTime(ticket.created_at)}</span>
            <span>
              Support Agent: {ticket.assigned_agent_name || "Not assigned"}
            </span>
          </div>
        </div>

        <div className="sd-ref-ticket-badges">
          <StatusBadge status={ticket.status} />
          <StatusBadge status={ticket.priority} />
          <StatusBadge status={ticket.request_type} />
        </div>
      </div>

      <p className="sd-ref-ticket-description">{ticket.description}</p>

      {attachments.length > 0 && (
        <div className="sd-ref-attachment-grid">
          {attachments.map((item) => {
            const fileUrl = getMediaUrl(item.file_url || item.file);
            const name = item.original_filename || "Attachment";

            return (
              <div key={item.id} className="sd-ref-attachment-card">
                {isImageAttachment(item) && fileUrl ? (
                  <img src={fileUrl} alt={name} />
                ) : isVideoAttachment(item) && fileUrl ? (
                  <video src={fileUrl} controls />
                ) : (
                  <div className="sd-ref-file-card">
                    <Icon name="movie" />
                    <strong>{name}</strong>
                    <span>{item.file_size || ""}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {closed && (
        <div className="sd-closed-feedback-row">
          {feedbackSubmitted ? (
            <button className="sd-feedback-done-btn" disabled>
              Feedback Submitted
            </button>
          ) : (
            <button
              className="sd-feedback-open-btn"
              onClick={() => setShowFeedbackModal(true)}
            >
              Give Feedback
            </button>
          )}
        </div>
      )}

      <div className="sd-ref-ticket-divider" />

      <TicketThread ticket={ticket} onRefresh={onRefresh} />

      {showFeedbackModal && (
        <FeedbackModal
          ticket={ticket}
          onClose={() => setShowFeedbackModal(false)}
          onSubmitted={async () => {
            await onRefresh?.();
          }}
        />
      )}
    </div>
  );
}