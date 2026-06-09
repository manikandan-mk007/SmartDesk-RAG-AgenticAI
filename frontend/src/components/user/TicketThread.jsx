import { useRef, useState } from "react";
import { sendTicketMessage, uploadTicketAttachment } from "../../api/ticketApi";
import { formatDateTime } from "../../utils/formatDate";
import Icon from "../common/Icon";

export default function TicketThread({ ticket, onRefresh }) {
  const [message, setMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [sending, setSending] = useState(false);

  const fileInputRef = useRef(null);
  const mediaInputRef = useRef(null);

  const handleSend = async (event) => {
    event.preventDefault();

    if (!message.trim() && !selectedFile) return;

    try {
      setSending(true);

      if (message.trim()) {
        await sendTicketMessage(ticket.id, message);
      }

      if (selectedFile) {
        await uploadTicketAttachment(ticket.id, selectedFile);
      }

      setMessage("");
      setSelectedFile(null);
      onRefresh();
    } finally {
      setSending(false);
    }
  };

  return (
    <section className="sd-ref-thread">
      <h2>CONVERSATION THREAD</h2>

      <div className="sd-ref-thread-body">
        {ticket.messages?.map((msg) => {
          const isUser = msg.sender_role === "USER";

          return (
            <div
              key={msg.id}
              className={`sd-ref-message-row ${isUser ? "user" : "agent"}`}
            >
              {!isUser && (
                <div className="sd-ref-avatar">
                  <Icon name="support_agent" />
                </div>
              )}

              <div className={`sd-ref-message-bubble ${isUser ? "user" : "agent"}`}>
                <div className="sd-ref-message-head">
                  <strong>{isUser ? "You" : msg.sender_name || "Support Agent"}</strong>
                  <span>{formatDateTime(msg.created_at)}</span>
                </div>

                <p>{msg.message}</p>
              </div>

              {isUser && (
                <div className="sd-ref-avatar user">
                  <Icon name="person" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {ticket.status !== "CLOSED" && (
        <form onSubmit={handleSend} className="sd-ref-composer">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Type your response or use AI Suggestion..."
          />

          {selectedFile && (
            <div className="sd-ref-selected-file">
              <Icon name="attach_file" />
              <span>{selectedFile.name}</span>
              <button type="button" onClick={() => setSelectedFile(null)}>
                ×
              </button>
            </div>
          )}

          <div className="sd-ref-composer-footer">
            <div className="sd-ref-composer-icons">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
              >
                <Icon name="attach_file" />
              </button>

              <button type="button">
                <Icon name="sentiment_satisfied" />
              </button>

              <button
                type="button"
                onClick={() => mediaInputRef.current?.click()}
              >
                <Icon name="image" />
              </button>
            </div>

            <button type="submit" disabled={sending || (!message.trim() && !selectedFile)}>
              Send
              <Icon name="send" />
            </button>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            hidden
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          />

          <input
            ref={mediaInputRef}
            type="file"
            hidden
            accept="image/*,video/*"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          />
        </form>
      )}
    </section>
  );
}