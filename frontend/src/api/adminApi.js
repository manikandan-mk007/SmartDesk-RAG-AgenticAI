import apiClient from "./axiosConfig";

export const getAdminDashboard = () => apiClient.get("/admin/dashboard/");

export const getAdminUsers = () => apiClient.get("/admin/users/");

export const getAdminAgents = () => apiClient.get("/admin/agents/");

export const createAdminAgent = (payload) =>
  apiClient.post("/admin/agents/create/", payload);

export const updateAdminUser = (id, payload) =>
  apiClient.patch(`/admin/users/${id}/`, payload);

export const updateAdminAgent = (id, payload) =>
  apiClient.patch(`/admin/agents/${id}/`, payload);

export const updateAdminUserStatus = (id, payload) =>
  apiClient.patch(`/admin/users/${id}/status/`, payload);

export const getAdminTickets = (params = {}) =>
  apiClient.get("/admin/tickets/", { params });

export const getAdminTicketAnalytics = () =>
  apiClient.get("/admin/ticket-analytics/");

export const getAIClassificationLogs = () =>
  apiClient.get("/admin/ai-classification-logs/");

export const getKBGaps = () => apiClient.get("/admin/kb-gaps/");

export const getAdminReportSummary = () =>
  apiClient.get("/admin/reports/summary/");

// Phase 19: Admin agent-wise feedback analytics
export const getAdminAgentFeedbackAnalytics = () =>
  apiClient.get("/tickets/admin/feedback/agent-analytics/");

// Employee roster security APIs
export const uploadEmployeeRoster = (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return apiClient.post("/admin/employees/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getAdminEmployees = (params = {}) =>
  apiClient.get("/admin/employees/", { params });

export const getEmployeeRosterUploads = () =>
  apiClient.get("/admin/employees/uploads/");

// FAQ Admin APIs
export const getAdminFAQs = () => apiClient.get("/faqs/admin/");

export const createAdminFAQ = (payload) =>
  apiClient.post("/faqs/admin/", payload);

export const updateAdminFAQ = (id, payload) =>
  apiClient.patch(`/faqs/admin/${id}/`, payload);

export const deleteAdminFAQ = (id) =>
  apiClient.delete(`/faqs/admin/${id}/`);

// KB Admin APIs
export const getKBDocuments = () => apiClient.get("/kb/documents/");

export const uploadKBDocument = (title, file) => {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);

  return apiClient.post("/kb/documents/upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const deleteKBDocument = (id) =>
  apiClient.delete(`/kb/documents/${id}/`);