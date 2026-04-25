import axios, { AxiosError } from "axios";
import Cookies from "js-cookie";

let _cachedToken: string | undefined;

export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = _cachedToken ?? Cookies.get("waslai_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    const isAuthEndpoint = err.config?.url?.includes("/auth/login");
    if (err.response?.status === 401 && !isAuthEndpoint) {
      _cachedToken = undefined;
      Cookies.remove("waslai_token");
      if (typeof window !== "undefined") window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export function syncToken(token: string) {
  _cachedToken = token;
}

// Auth
export const login = (email: string, password: string) =>
  api.post(
    "/v1/auth/login",
    new URLSearchParams({ username: email, password }),
    { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
  );

export const register = (data: {
  email: string; username: string; password: string;
  full_name_en?: string; full_name_ar?: string; phone?: string; role: string;
}) => api.post("/v1/auth/register", data);

export const getMe = () => api.get("/v1/auth/me");
export const updateMe = (data: object) => api.patch("/v1/auth/me", data);

// Campaigns
export const getCampaigns = (params?: object) =>
  api.get("/v1/campaigns/", { params });
export const getMyCampaigns = () => api.get("/v1/campaigns/my");
export const getCampaign = (id: number) => api.get(`/v1/campaigns/${id}`);
export const createCampaign = (data: object) => api.post("/v1/campaigns/", data);
export const updateCampaign = (id: number, data: object) =>
  api.patch(`/v1/campaigns/${id}`, data);
export const deleteCampaign = (id: number) => api.delete(`/v1/campaigns/${id}`);
export const activateCampaign = (id: number) =>
  api.post(`/v1/campaigns/${id}/activate`);
export const applyToCampaign = (id: number) =>
  api.post(`/v1/campaigns/${id}/apply`);

// Influencers
export const getInfluencers = (params?: object) =>
  api.get("/v1/influencers/", { params });
export const getInfluencerMe = () => api.get("/v1/influencers/me");
export const updateInfluencerMe = (data: object) =>
  api.patch("/v1/influencers/me", data);
export const createInfluencerProfile = (data: object) =>
  api.post("/v1/influencers/", data);
export const smartSearch = (data: object) =>
  api.post("/v1/influencers/smart-search", data);

// Merchants
export const getMerchantMe = () => api.get("/v1/merchants/me");
export const createMerchantProfile = (data: object) =>
  api.post("/v1/merchants/", data);
export const updateMerchantMe = (data: object) =>
  api.patch("/v1/merchants/me", data);
export const getMerchantAnalytics = () => api.get("/v1/merchants/analytics");

// Bookings
export const createBooking = (data: object) => api.post("/v1/bookings/", data);
export const getMyBookings = () => api.get("/v1/bookings/my");
export const getBooking = (id: number) => api.get(`/v1/bookings/${id}`);
export const confirmBooking = (id: number) =>
  api.post(`/v1/bookings/${id}/confirm`);
export const submitContent = (id: number, data: object) =>
  api.post(`/v1/bookings/${id}/submit-content`, data);
export const approveContent = (id: number) =>
  api.post(`/v1/bookings/${id}/approve-content`);

// Escrow
export const getMyEscrow = () => api.get("/v1/escrow/my");
export const getCampaignEscrow = (campaignId: number) =>
  api.get(`/v1/escrow/campaign/${campaignId}`);
export const releaseEscrow = (id: number) =>
  api.post(`/v1/escrow/${id}/release`);
export const disputeEscrow = (id: number, data: object) =>
  api.post(`/v1/escrow/${id}/dispute`, data);

// Wallet
export const getWallet = () => api.get("/v1/wallet/me");
export const redeemPoints = (points: number) =>
  api.post("/v1/wallet/redeem", { points });

// Contracts
export const generateContract = (data: object) =>
  api.post("/v1/contracts/generate", data);
export const policyQA = (question: string, language: string) =>
  api.post(`/v1/contracts/policy-qa?question=${encodeURIComponent(question)}&language=${language}`);

// Admin
export const getPlatformStats = () => api.get("/v1/admin/platform-stats");
export const getAdminUsers = () => api.get("/v1/admin/users");
export const getAdminDisputes = () => api.get("/v1/admin/disputes");
export const resolveDispute = (id: number, data: object) =>
  api.post(`/v1/admin/disputes/${id}/resolve`, data);

// Messages
export const getBookingMessages = (bookingId: number) =>
  api.get(`/v1/messages/booking/${bookingId}`);
export const sendMessage = (data: object) => api.post("/v1/messages/", data);
export const getUnreadCount = () => api.get("/v1/messages/unread-count/me");

// Chatbot  — actual endpoint is /chatbot/chat
export const askChatbot = (message: string, lang: string) =>
  api.post("/v1/chatbot/chat", { message, language: lang });
