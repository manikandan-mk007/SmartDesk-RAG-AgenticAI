import apiClient from "./axiosConfig";

export const registerUser = (payload) => apiClient.post("/auth/register/", payload);

export const loginUser = (payload) => apiClient.post("/auth/login/", payload);

export const getProfile = () => apiClient.get("/auth/profile/");

export const getAgentProfile = () => apiClient.get("/agent/profile/");