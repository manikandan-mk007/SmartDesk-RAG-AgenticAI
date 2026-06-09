import { useState } from "react";
import { sendAgentReply } from "../../api/agentApi";
import { formatDateTime } from "../../utils/formatDate";
import Button from "../common/Button";

export default function AgentChatBox({ ticket, draftMessage, setDraftMessage, onRefresh }) {
  const [sending, setSending] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();

    if (!draftMessage.trim()) return;

    try {
      setSending(true);
      await sendAgentReply(ticket.id, draftMessage);
      setDraftMessage("");
      onRefresh();
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="sd-card sd-thread">
      <div className="sd-card-header">
        <h2 className="sd-heading-sm">Ticket Conversation</h2>
        <p className="sd-body sd-muted sd-mt-1">
          Full user-agent thread is visible here.
        </p>
      </div>

      <div className="sd-thread-body" style={{ maxHeight: 520 }}>
        {ticket.messages?.map((msg) => {
          const isAgent = msg.sender_role === "AGENT" || msg.sender_role === "ADMIN";

          return (
            <div
              key={msg.id}
              className={`sd-message-row ${isAgent ? "agent" : "user"}`}
            >
              <div className={`sd-chat-bubble ${isAgent ? "agent" : "user"}`}>
                <p className="sd-body" style={{ whiteSpace: "pre-line", margin: 0 }}>
                  {msg.message}
                </p>
                <p className="sd-chat-meta">
                  {msg.sender_name || msg.sender_role} • {formatDateTime(msg.created_at)}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {ticket.status !== "CLOSED" && (
        <form onSubmit={handleSend} className="sd-card-body" style={{ borderTop: "1px solid var(--outline-variant)" }}>
          <textarea
            className="sd-textarea"
            rows="4"
            value={draftMessage}
            onChange={(e) => setDraftMessage(e.target.value)}
            placeholder="Type response to customer..."
          />

          <div className="sd-row sd-mt-3" style={{ justifyContent: "flex-end" }}>
            <Button type="submit" disabled={sending}>
              {sending ? "Sending..." : "Send Reply"}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}