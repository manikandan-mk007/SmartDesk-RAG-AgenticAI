import api from "./axiosConfig";

export const askRAG = (payload) => {
  return api.post("/rag/ask/", payload);
};

export const createTicketFromRAG = (payload) => {
  return api.post("/rag/create-ticket/", payload);
};