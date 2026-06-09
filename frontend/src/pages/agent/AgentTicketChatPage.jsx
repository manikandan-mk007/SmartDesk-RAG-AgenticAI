import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  closeAgentTicket,
  escalateAgentTicket,
  getAgentTicketDetail,
} from "../../api/agentApi";
import AgentChatBox from "../../components/agent/AgentChatBox";
import AIAssistPanel from "../../components/agent/AIAssistPanel";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";
import StatusBadge from "../../components/common/StatusBadge";
import { formatDateTime } from "../../utils/formatDate";
import AgentAttachmentPanel from "../../components/agent/AgentAttachmentPanel";
import SmartPromptModal from "../../components/common/SmartPromptModal";

function getApiError(error) {
  const data = error?.response?.data;

  if (!data) return "Unable to open this ticket.";

  if (typeof data === "string") return data;

  if (data.message) return data.message;

  if (data.detail) return data.detail;

  return "Unable to open this ticket.";
}

export default function AgentTicketChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [promptMode, setPromptMode] = useState(null);
  const [ticket, setTicket] = useState(null);
  const [draftMessage, setDraftMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState("");

  const loadTicket = async () => {
    try {
      setLoading(true);
      setPageError("");

      const response = await getAgentTicketDetail(id);
      setTicket(response.data.ticket);
    } catch (err) {
      setTicket(null);
      setPageError(getApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTicket();
  }, [id]);

  const handleEscalate = () => {
    setPromptMode("ESCALATE");
  };

  const handleClose = () => {
    setPromptMode("CLOSE");
  };

  const handlePromptConfirm = async (value) => {
    if (promptMode === "ESCALATE") {
      if (!value.trim()) return;

      await escalateAgentTicket(ticket.id, value);
      setPromptMode(null);
      await loadTicket();
    }

    if (promptMode === "CLOSE") {
      await closeAgentTicket(ticket.id, value);
      setPromptMode(null);
      await loadTicket();
    }
  };

  if (loading) {
    return (
      <Card className="pad">
        <p className="sd-body sd-muted">Loading ticket...</p>
      </Card>
    );
  }

  if (pageError) {
    return (
      <Card className="pad">
        <p className="sd-error">{pageError}</p>

        <div className="sd-row sd-mt-4">
          <Button onClick={() => navigate("/agent/queue")}>Back to Queue</Button>

          <Link to="/agent/dashboard">
            <Button variant="secondary">Go Dashboard</Button>
          </Link>
        </div>
      </Card>
    );
  }

  if (!ticket) {
    return (
      <Card className="pad">
        <p className="sd-error">Ticket not found.</p>
      </Card>
    );
  }

  return (
    <div className="sd-stack">
      <Card className="pad">
        <div className="sd-row-between" style={{ alignItems: "flex-start" }}>
          <div>
            <p className="sd-label sd-muted">Ticket #{ticket.id}</p>

            <h1 className="sd-heading-md sd-mt-1">{ticket.subject}</h1>

            <p
              className="sd-body sd-muted sd-mt-2"
              style={{ whiteSpace: "pre-line" }}
            >
              {ticket.description}
            </p>

            <p className="sd-label-sm sd-muted sd-mt-3">
              Created by {ticket.user_name} • {formatDateTime(ticket.created_at)}
            </p>
          </div>

          <div className="sd-row" style={{ flexWrap: "wrap" }}>
            <StatusBadge status={ticket.status} />
            <StatusBadge status={ticket.priority} />
            <StatusBadge status={ticket.request_type} />
          </div>
        </div>

        <div className="sd-detail-grid">
          <div className="sd-mini-stat">
            <p className="sd-label sd-muted">Sentiment</p>
            <p className="sd-body-lg" style={{ fontWeight: 700 }}>
              {ticket.sentiment}
            </p>
          </div>

          <div className="sd-mini-stat">
            <p className="sd-label sd-muted">Assigned Agent</p>
            <p className="sd-body-lg" style={{ fontWeight: 700 }}>
              {ticket.assigned_agent_name || "Not assigned"}
            </p>
          </div>

          <div className="sd-mini-stat">
            <p className="sd-label sd-muted">Escalation</p>
            <p className="sd-body-lg" style={{ fontWeight: 700 }}>
              {ticket.escalation_required ? "Required" : "Not Required"}
            </p>
          </div>
        </div>

        {ticket.ai_summary && (
          <div className="sd-ai-summary">
            <p className="sd-label" style={{ color: "rgba(255,255,255,0.65)" }}>
              AI Summary
            </p>

            <p className="sd-body sd-mt-2">{ticket.ai_summary}</p>

            {ticket.ai_suggested_solution && (
              <p
                className="sd-body sd-mt-2"
                style={{ color: "rgba(255,255,255,0.8)" }}
              >
                {ticket.ai_suggested_solution}
              </p>
            )}
          </div>
        )}

        {ticket.status !== "CLOSED" && (
          <div className="sd-row sd-mt-6">
            <Button variant="secondary" onClick={handleEscalate}>
              Escalate
            </Button>

            <Button onClick={handleClose}>Close Ticket</Button>
          </div>
        )}
      </Card>

      <AgentAttachmentPanel attachments={ticket.attachments || []} />

      <div className="sd-agent-chat-grid">
        <AgentChatBox
          ticket={ticket}
          draftMessage={draftMessage}
          setDraftMessage={setDraftMessage}
          onRefresh={loadTicket}
        />

        <AIAssistPanel
          ticket={ticket}
          onUseSuggestion={(message) => setDraftMessage(message)}
        />
      </div>

      <SmartPromptModal
        open={promptMode === "ESCALATE"}
        title="Escalate Ticket"
        label="Enter escalation reason"
        placeholder="Example: User has an urgent client meeting and the issue is blocking work."
        confirmText="Escalate"
        onConfirm={handlePromptConfirm}
        onCancel={() => setPromptMode(null)}
      />

      <SmartPromptModal
        open={promptMode === "CLOSE"}
        title="Close Ticket"
        label="Enter closing note"
        placeholder="Example: Issue resolved after troubleshooting."
        confirmText="Close Ticket"
        onConfirm={handlePromptConfirm}
        onCancel={() => setPromptMode(null)}
      />
    </div>
  );
}