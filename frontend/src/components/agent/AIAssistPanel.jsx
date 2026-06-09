import { useState } from "react";
import { generateAgentAISuggest } from "../../api/agentApi";
import Button from "../common/Button";
import Icon from "../common/Icon";

export default function AIAssistPanel({ ticket, onUseSuggestion }) {
  const [suggestion, setSuggestion] = useState(ticket?.agent_suggestions?.[0] || null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      const response = await generateAgentAISuggest(ticket.id);
      setSuggestion(response.data.suggestion);
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="sd-card sd-ai-panel">
      <div className="sd-ai-panel-head">
        <div className="sd-section-title-row" style={{ marginBottom: 0 }}>
          <Icon name="smart_toy" />
          <div>
            <h2 className="sd-heading-sm" style={{ color: "#fff" }}>AI Assist Panel</h2>
            <p className="sd-body" style={{ color: "rgba(255,255,255,0.7)", margin: 0 }}>
              Suggested reply, KB articles, and similar tickets.
            </p>
          </div>
        </div>
      </div>

      <div className="sd-ai-panel-body">
        <Button onClick={handleGenerate} disabled={loading} className="full">
          {loading ? "Generating..." : "Generate Suggestion"}
        </Button>

        {!suggestion && (
          <p className="sd-body sd-muted sd-mt-4">
            Click generate to create an AI support suggestion.
          </p>
        )}

        {suggestion && (
          <>
            <section className="sd-panel-section">
              <p className="sd-label sd-muted">Ticket Summary</p>
              <p className="sd-body sd-mt-1">{suggestion.ticket_summary}</p>
            </section>

            <section className="sd-panel-section">
              <p className="sd-label sd-muted">Priority Reason</p>
              <p className="sd-body sd-mt-1">{suggestion.priority_reason}</p>
            </section>

            <section className="sd-panel-section">
              <p className="sd-label sd-muted">Sentiment Explanation</p>
              <p className="sd-body sd-mt-1">{suggestion.sentiment_explanation}</p>
            </section>

            <section className="sd-panel-section sd-panel-mini-card">
              <p className="sd-label sd-muted">Suggested Reply</p>
              <p className="sd-body sd-mt-2" style={{ whiteSpace: "pre-line" }}>
                {suggestion.suggested_reply}
              </p>

              <div className="sd-mt-4">
                <Button onClick={() => onUseSuggestion(suggestion.suggested_reply)}>
                  Use Suggestion
                </Button>
              </div>
            </section>

            <section className="sd-panel-section">
              <p className="sd-label sd-muted">Suggested Steps</p>
              <p className="sd-body sd-mt-1" style={{ whiteSpace: "pre-line" }}>
                {suggestion.suggested_steps}
              </p>
            </section>

            <section className="sd-panel-section">
              <p className="sd-label sd-muted">Escalation Suggestion</p>
              <p className="sd-body sd-mt-1">{suggestion.escalation_suggestion}</p>
            </section>

            <section className="sd-panel-section">
              <p className="sd-label sd-muted">Related KB Articles</p>

              {suggestion.related_kb_articles?.length === 0 ? (
                <p className="sd-body sd-muted sd-mt-2">No related KB articles found.</p>
              ) : (
                suggestion.related_kb_articles?.map((item, index) => (
                  <div key={`${item.document_id}-${index}`} className="sd-panel-mini-card">
                    <p className="sd-ticket-title">{item.document_title}</p>
                    <p className="sd-label-sm sd-muted">Score: {item.similarity_score}</p>
                    <p className="sd-body sd-muted sd-line-3 sd-mt-2">{item.preview}</p>
                  </div>
                ))
              )}
            </section>

            <section className="sd-panel-section">
              <p className="sd-label sd-muted">Similar Tickets</p>

              {suggestion.similar_tickets?.length === 0 ? (
                <p className="sd-body sd-muted sd-mt-2">No similar tickets found.</p>
              ) : (
                suggestion.similar_tickets?.map((item) => (
                  <div key={item.id} className="sd-panel-mini-card">
                    <p className="sd-ticket-title">#{item.id} - {item.subject}</p>
                    <p className="sd-label-sm sd-muted">
                      {item.request_type} • {item.priority} • {item.status}
                    </p>
                  </div>
                ))
              )}
            </section>
          </>
        )}
      </div>
    </aside>
  );
}