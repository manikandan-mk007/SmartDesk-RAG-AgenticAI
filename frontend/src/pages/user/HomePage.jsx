import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { searchFAQs } from "../../api/faqApi";
import { askRAG } from "../../api/ragApi";
import Button from "../../components/common/Button";
import Icon from "../../components/common/Icon";
import { useAuth } from "../../context/AuthContext";

function createRAGSessionId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }

  return `rag-session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getStoredRAGSessionId() {
  const existing = localStorage.getItem("smartdesk_rag_session_id");

  if (existing) return existing;

  const sessionId = createRAGSessionId();
  localStorage.setItem("smartdesk_rag_session_id", sessionId);

  return sessionId;
}

function getStoredRAGMessages() {
  try {
    const saved = localStorage.getItem("smartdesk_rag_messages");
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function saveRAGMessages(messages) {
  localStorage.setItem(
    "smartdesk_rag_messages",
    JSON.stringify(messages.slice(-12))
  );
}

function normalizeRAGResult(result) {
  if (!result) {
    return {
      answer: "",
      sources: [],
    };
  }

  return {
    ...result,
    answer: result.answer || "",
    sources: result.sources || [],
  };
}

function cleanTicketText(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/#+\s?/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function extractUserMessages(messages) {
  return messages
    .filter((item) => item.role === "user")
    .map((item) => cleanTicketText(item.content))
    .filter(Boolean);
}

function extractAssistantSteps(answer) {
  const text = String(answer || "");

  const lines = text
    .split("\n")
    .map((line) => cleanTicketText(line))
    .filter(Boolean);

  const stepLines = lines.filter((line) =>
    /^(step\s*\d+|[0-9]+\.)/i.test(line)
  );

  return stepLines.slice(0, 3);
}

function buildRAGTicketDraft({
  ragMessages,
  ragResult,
  latestUserQuestion,
  ragSessionId,
}) {
  const userMessages = extractUserMessages(ragMessages);

  const firstIssue = userMessages[0] || latestUserQuestion;
  const lastFollowUp = userMessages[userMessages.length - 1] || latestUserQuestion;

  const suggestedSubject =
    cleanTicketText(ragResult?.suggested_ticket_subject) ||
    cleanTicketText(firstIssue).slice(0, 120);

  const assistantSteps = extractAssistantSteps(ragResult?.answer);

  let triedText =
    "I already tried the suggested troubleshooting steps from SmartDesk AI, but the issue is still not resolved.";

  if (assistantSteps.length > 0) {
    const cleanSteps = assistantSteps.map((step) =>
      step
        .replace(/^step\s*\d+:\s*/i, "")
        .replace(/^\d+\.\s*/, "")
        .trim()
    );

    triedText = `I already tried the suggested troubleshooting steps, including ${cleanSteps.join(
      ", "
    )}, but the issue is still not resolved.`;
  }

  const issueParagraph =
    firstIssue === lastFollowUp
      ? firstIssue
      : `${firstIssue} ${lastFollowUp}`;

  const description = `${issueParagraph}

${triedText}

Please check this issue further and verify the device, logs, settings, account configuration, or hardware condition if needed. I can attach a screenshot or video for verification.`;

  return {
    source: "RAG",
    session_id: ragSessionId,
    subject: suggestedSubject,
    description,
    created_at: new Date().toISOString(),
  };
}

export default function HomePage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [faqQuery, setFaqQuery] = useState("");
  const [faqResults, setFaqResults] = useState([]);

  const [ragQuestion, setRagQuestion] = useState("");
  const [ragResult, setRagResult] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  const [ragSessionId, setRagSessionId] = useState(getStoredRAGSessionId);
  const [ragMessages, setRagMessages] = useState(getStoredRAGMessages);

  const latestUserQuestion = useMemo(() => {
    const userMessages = ragMessages.filter((item) => item.role === "user");
    return userMessages[userMessages.length - 1]?.content || ragQuestion;
  }, [ragMessages, ragQuestion]);

  useEffect(() => {
    saveRAGMessages(ragMessages);
  }, [ragMessages]);

  const handleFAQSearch = async (queryValue = faqQuery) => {
    if (!queryValue.trim()) return;

    const response = await searchFAQs(queryValue);
    setFaqResults(response.data);
  };

  const handleRAGAsk = async () => {
    if (!ragQuestion.trim() || ragLoading) return;

    const currentQuestion = ragQuestion.trim();

    const userMessage = {
      role: "user",
      content: currentQuestion,
    };

    const historyBeforeCurrent = ragMessages.slice(-8);
    const nextMessages = [...ragMessages, userMessage].slice(-12);

    setRagMessages(nextMessages);
    setRagQuestion("");

    try {
      setRagLoading(true);

      const response = await askRAG({
        question: currentQuestion,
        session_id: ragSessionId,
        chat_history: historyBeforeCurrent,
      });

      const result = normalizeRAGResult(response.data.result);
      setRagResult(result);

      const assistantMessage = {
        role: "assistant",
        content: result.answer,
      };

      setRagMessages((prev) => [...prev, assistantMessage].slice(-12));
    } catch {
      const assistantMessage = {
        role: "assistant",
        content:
          "I could not process that question right now. Please try again or create a support ticket.",
      };

      setRagMessages((prev) => [...prev, assistantMessage].slice(-12));
    } finally {
      setRagLoading(false);
    }
  };

  const handleContactAgent = () => {
    navigate(isAuthenticated ? "/tickets" : "/login");
  };

  const handleNewRAGChat = () => {
    const newSessionId = createRAGSessionId();

    localStorage.setItem("smartdesk_rag_session_id", newSessionId);
    localStorage.removeItem("smartdesk_rag_messages");
    localStorage.removeItem("smartdesk_rag_ticket_draft");

    setRagSessionId(newSessionId);
    setRagMessages([]);
    setRagResult(null);
    setRagQuestion("");
  };

  const handleCreateTicketFromRAG = () => {
    const draft = buildRAGTicketDraft({
      ragMessages,
      ragResult,
      latestUserQuestion,
      ragSessionId,
    });

    localStorage.setItem("smartdesk_rag_ticket_draft", JSON.stringify(draft));

    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    navigate("/tickets");
  };

  return (
    <>
      <section className="sd-hero">
        <h1 className="sd-display">How can we help you today?</h1>
        <p className="sd-body-lg">
          Access our comprehensive knowledge base or reach out to our team of experts for personalized assistance.
        </p>
      </section>

      <section className="sd-home-grid">
        <div className="sd-card sd-search-card">
          <div>
            <div className="sd-section-title-row">
              <div className="sd-icon-box">
                <Icon name="help_outline" />
              </div>
              <h2 className="sd-heading-sm">Search FAQs</h2>
            </div>

            <p className="sd-body sd-muted">
              Browse our collection of frequently asked questions for instant answers to common issues.
            </p>
          </div>

          <div className="sd-mt-6">
            <div className="sd-input-icon-wrap">
              <Icon name="search" />
              <input
                className="sd-input"
                value={faqQuery}
                onChange={(e) => setFaqQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleFAQSearch()}
                placeholder="Search keywords..."
              />
            </div>

            <div className="sd-chip-row">
              {[
                "password",
                "vpn",
                "payslip",
                "support",
                "ticket",
                "upload",
                "password",
                "power",
                "green lines",
                "flickering",
                "performance",
                "network",
                "teams",
                "leave",
                "employee record",
                "cooling",
                "replacement",
                "damage",
              ].map((item) => (
                <button
                  key={item}
                  className="sd-chip"
                  onClick={() => {
                    setFaqQuery(item);
                    handleFAQSearch(item);
                  }}
                >
                  {item}
                </button>
              ))}
            </div>

            <div className="sd-stack sd-mt-5">
              {faqResults.map((faq) => (
                <div key={faq.id} className="sd-panel-mini-card">
                  <h3 className="sd-ticket-title">{faq.question}</h3>
                  <p className="sd-body sd-muted sd-mt-2">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="sd-kb-card sd-card">
          <div className="sd-row-between">
            <div className="sd-section-title-row">
              <div
                className="sd-icon-box"
                style={{
                  background: "rgba(255,255,255,0.1)",
                  color: "#fff",
                }}
              >
                <Icon name="smart_toy" />
              </div>

              <h2 className="sd-heading-sm" style={{ color: "#fff" }}>
                Search Knowledge Base
              </h2>
            </div>

            {ragMessages.length > 0 && (
              <button className="sd-rag-new-chat-btn" onClick={handleNewRAGChat}>
                New Chat
              </button>
            )}
          </div>

          <p className="sd-body" style={{ color: "rgba(255,255,255,0.72)" }}>
            Ask SmartDesk AI using our internal knowledge base documents.
          </p>

          <div className="sd-row sd-mt-6">
            <input
              className="sd-input sd-kb-input"
              value={ragQuestion}
              onChange={(e) => setRagQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleRAGAsk()}
              placeholder={
                ragMessages.length > 0
                  ? "Continue your issue... e.g. I tried but not working"
                  : "Ask your question..."
              }
            />

            <Button
              variant="secondary"
              onClick={handleRAGAsk}
              disabled={ragLoading || !ragQuestion.trim()}
            >
              {ragLoading ? "..." : "Ask"}
            </Button>
          </div>

          {(ragMessages.length > 0 || ragLoading) && (
            <div className="sd-kb-result">
              <p
                className="sd-label"
                style={{ color: "rgba(255,255,255,0.65)" }}
              >
                AI Instant Insight
              </p>

              <div
                className="sd-rag-message-list"
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "12px",
                  marginTop: "12px",
                  maxHeight: "280px",
                  overflowY: "auto",
                }}
              >
                {ragMessages.map((message, index) => {
                  const isUser = message.role === "user";

                  return (
                    <div
                      key={`${message.role}-${index}`}
                      style={{
                        alignSelf: isUser ? "flex-end" : "flex-start",
                        maxWidth: "88%",
                        padding: "12px 14px",
                        borderRadius: "12px",
                        background: isUser
                          ? "#ffffff"
                          : "rgba(255,255,255,0.1)",
                        border: isUser
                          ? "none"
                          : "1px solid rgba(255,255,255,0.18)",
                        color: isUser ? "#000000" : "#ffffff",
                      }}
                    >
                      <strong
                        style={{
                          display: "block",
                          marginBottom: "6px",
                          fontSize: "11px",
                          color: isUser
                            ? "#444748"
                            : "rgba(255,255,255,0.7)",
                        }}
                      >
                        {isUser ? "You" : "SmartDesk AI"}
                      </strong>

                      <p
                        className="sd-body"
                        style={{
                          margin: 0,
                          whiteSpace: "pre-line",
                          color: isUser ? "#000000" : "#ffffff",
                        }}
                      >
                        {message.content}
                      </p>
                    </div>
                  );
                })}

                {ragLoading && (
                  <div
                    style={{
                      alignSelf: "flex-start",
                      maxWidth: "88%",
                      padding: "12px 14px",
                      borderRadius: "12px",
                      background: "rgba(255,255,255,0.1)",
                      border: "1px solid rgba(255,255,255,0.18)",
                      color: "#ffffff",
                    }}
                  >
                    <strong
                      style={{
                        display: "block",
                        marginBottom: "6px",
                        fontSize: "11px",
                        color: "rgba(255,255,255,0.7)",
                      }}
                    >
                      SmartDesk AI
                    </strong>

                    <p className="sd-body" style={{ margin: 0, color: "#fff" }}>
                      Checking best solution...
                    </p>
                  </div>
                )}
              </div>

              {ragResult?.sources?.length > 0 && (
                <p
                  className="sd-label-sm sd-mt-4"
                  style={{ color: "rgba(255,255,255,0.62)" }}
                >
                  Source: {ragResult.sources[0].document_title}
                </p>
              )}

              <button
                className="sd-kb-create-ticket-btn"
                onClick={handleCreateTicketFromRAG}
              >
                Still need help? Create ticket
              </button>
            </div>
          )}
        </div>
      </section>

      <section className="sd-card sd-home-contact-card">
        <div>
          <h3>Still cannot find the answer?</h3>
          <p>
            Our support agents are available 24/7 to help you solve your most complex
            problems.
          </p>
        </div>

        <Button onClick={handleContactAgent} className="sd-contact-agent-btn">
          <Icon name="support_agent" />
          Contact Our Agent
        </Button>
      </section>
    </>
  );
}