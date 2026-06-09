import apiClient from "./axiosConfig";

export const getFAQs = () => apiClient.get("/faqs/");

export const searchFAQs = (q, category = "") =>
  apiClient.get("/faqs/search/", {
    params: { q, category },
  });

export const markFAQHelpful = (id) => apiClient.post(`/faqs/${id}/helpful/`);

export const markFAQNotHelpful = (id) => apiClient.post(`/faqs/${id}/not-helpful/`);