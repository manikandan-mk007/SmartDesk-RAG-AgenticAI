import apiClient from "./axiosConfig";

export const getAgentDashboard = () => apiClient.get("/agent/dashboard/");

/*
  Phase 19:
  This queue comes from tickets app.
  Backend filters:
  - agent department tickets only
  - unassigned tickets
  - tickets assigned to same agent
*/
export const getAgentQueue = (params = {}) =>
  apiClient.get("/tickets/agent/queue/", { params });

/*
  Phase 19:
  This detail endpoint auto-claims/locks ticket for the first valid agent.
  If another agent already handles it, backend blocks access.
*/
export const getAgentTicketDetail = (id) => apiClient.get(`/tickets/${id}/`);

/*
  Phase 19:
  Agent reply uses ticket message endpoint because backend now checks
  department + assigned agent ownership here.
*/
export const sendAgentReply = (id, message) =>
  apiClient.post(`/tickets/${id}/messages/`, { message });

/*
  Keep your existing agent action endpoints.
  These are used by current AgentTicketChatPage close/escalate buttons.
*/
export const closeAgentTicket = (id, closing_note = "") =>
  apiClient.post(`/agent/tickets/${id}/close/`, { closing_note });

export const escalateAgentTicket = (id, reason = "") =>
  apiClient.post(`/agent/tickets/${id}/escalate/`, { reason });

export const generateAgentAISuggest = (id) =>
  apiClient.post(`/agent/tickets/${id}/ai-suggest/`);

/*
  Phase 19:
  Agent feedback analytics.
*/
export const getAgentFeedbackSummary = () =>
  apiClient.get("/tickets/agent/feedback/summary/");

export const getAgentFeedbackList = () =>
  apiClient.get("/tickets/agent/feedback/");