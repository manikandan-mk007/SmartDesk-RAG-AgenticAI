import apiClient from "./axiosConfig";

export const createTicket = (payload) => apiClient.post("/tickets/", payload);

export const getMyTickets = () => apiClient.get("/tickets/my/");

export const getTicketDetail = (id) => apiClient.get(`/tickets/${id}/`);

export const getTicketStatusOptions = () =>
  apiClient.get("/tickets/status-options/");

export const sendTicketMessage = (id, message) =>
  apiClient.post(`/tickets/${id}/messages/`, { message });

export const uploadTicketAttachment = (id, file) => {
  const formData = new FormData();
  formData.append("file", file);

  return apiClient.post(`/tickets/${id}/attachments/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const submitTicketFeedback = (id, payload) =>
  apiClient.post(`/tickets/${id}/feedback/`, payload);