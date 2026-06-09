import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getMyTickets, getTicketDetail } from "../../api/ticketApi";
import TicketDetailPanel from "../../components/user/TicketDetailPanel";
import TicketForm from "../../components/user/TicketForm";
import TicketList from "../../components/user/TicketList";

function getRAGTicketDraft() {
  try {
    const saved = localStorage.getItem("smartdesk_rag_ticket_draft");
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export default function TicketPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [activeTab, setActiveTab] = useState(id ? "DETAILS" : "CREATE");
  const [loading, setLoading] = useState(true);
  const [ragDraft, setRagDraft] = useState(null);

  const loadTickets = async () => {
    const response = await getMyTickets();
    setTickets(response.data);
  };

  const loadTicketDetail = async (ticketId) => {
    const response = await getTicketDetail(ticketId);
    setSelectedTicket(response.data.ticket);
  };

  const refreshCurrentTicket = async () => {
    await loadTickets();

    if (selectedTicket?.id) {
      await loadTicketDetail(selectedTicket.id);
    }
  };

  const handleSelectTicket = async (ticket) => {
    setActiveTab("DETAILS");
    navigate(`/tickets/${ticket.id}`);
    await loadTicketDetail(ticket.id);
  };

  const handleNewTicket = () => {
    localStorage.removeItem("smartdesk_rag_ticket_draft");
    setRagDraft(null);
    setSelectedTicket(null);
    setActiveTab("CREATE");
    navigate("/tickets");
  };

  const handleTicketCreated = async (ticket) => {
    localStorage.removeItem("smartdesk_rag_ticket_draft");
    setRagDraft(null);

    await loadTickets();
    setActiveTab("DETAILS");
    navigate(`/tickets/${ticket.id}`);
    await loadTicketDetail(ticket.id);
  };

  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        await loadTickets();

        const draft = getRAGTicketDraft();

        if (id) {
          setRagDraft(null);
          setActiveTab("DETAILS");
          await loadTicketDetail(id);
        } else if (draft) {
          setRagDraft(draft);
          setSelectedTicket(null);
          setActiveTab("CREATE");
        } else {
          setActiveTab("CREATE");
        }
      } finally {
        setLoading(false);
      }
    }

    init();
  }, [id]);

  if (loading) {
    return (
      <div className="sd-card pad">
        <p className="sd-body sd-muted">Loading tickets...</p>
      </div>
    );
  }

  return (
    <div className="sd-user-ticket-page">
      <TicketList
        tickets={tickets}
        selectedTicketId={selectedTicket?.id}
        onSelect={handleSelectTicket}
        onNewTicket={handleNewTicket}
      />

      <section className="sd-user-ticket-panel">
        <div className="sd-user-ticket-tabs">
          <button
            className={activeTab === "DETAILS" ? "active" : ""}
            onClick={() => {
              if (selectedTicket) setActiveTab("DETAILS");
            }}
          >
            TICKET DETAILS
          </button>

          <button
            className={activeTab === "CREATE" ? "active" : ""}
            onClick={handleNewTicket}
          >
            CREATE NEW
          </button>
        </div>

        {activeTab === "CREATE" ? (
          <TicketForm
            initialValues={ragDraft}
            onTicketCreated={handleTicketCreated}
          />
        ) : selectedTicket ? (
          <TicketDetailPanel
            ticket={selectedTicket}
            onRefresh={refreshCurrentTicket}
          />
        ) : (
          <TicketForm
            initialValues={ragDraft}
            onTicketCreated={handleTicketCreated}
          />
        )}
      </section>
    </div>
  );
}