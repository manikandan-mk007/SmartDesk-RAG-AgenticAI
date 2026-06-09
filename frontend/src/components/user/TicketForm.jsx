import { useEffect, useState } from "react";
import { createTicket } from "../../api/ticketApi";
import Button from "../common/Button";

function getInitialForm(initialValues) {
  return {
    subject: initialValues?.subject || "",
    description: initialValues?.description || "",
  };
}

export default function TicketForm({ initialValues, onTicketCreated }) {
  const [form, setForm] = useState(getInitialForm(initialValues));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isRAGDraft = initialValues?.source === "RAG";

  useEffect(() => {
    setForm(getInitialForm(initialValues));
  }, [initialValues]);

  const handleChange = (event) => {
    setForm((prev) => ({
      ...prev,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!form.subject.trim() || !form.description.trim()) {
      setError("Subject and description are required.");
      return;
    }

    try {
      setLoading(true);
      const response = await createTicket(form);

      localStorage.removeItem("smartdesk_rag_ticket_draft");

      setForm({ subject: "", description: "" });
      onTicketCreated(response.data.ticket);
    } catch {
      setError("Ticket creation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sd-ref-create-ticket">
      <h1>Create New Ticket</h1>
      <p>
        {isRAGDraft
          ? "SmartDesk AI prepared this ticket draft. Review or edit it before submitting."
          : "Explain your issue clearly for faster support."}
      </p>

      {error && <p className="sd-error sd-mt-3">{error}</p>}

      <form onSubmit={handleSubmit}>
        <label>Subject</label>
        <input
          name="subject"
          value={form.subject}
          onChange={handleChange}
          placeholder="Example: Laptop display flickering"
          required
        />

        <label>Description</label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          rows="7"
          placeholder="Describe the issue, when it started, and any error message..."
          required
        />

        <Button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit Ticket"}
        </Button>
      </form>
    </div>
  );
}