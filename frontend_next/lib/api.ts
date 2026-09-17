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
  api.post("/v1/auth/login", { email, password });

export const register = (data: {
  email: string; username?: string; password: string;
  full_name?: string; full_name_en?: string; full_name_ar?: string; phone?: string; role: string;
}) => api.post("/v1/auth/register", data);

export const getMe = () => api.get("/v1/auth/me");
export const updateMe = (data: object) => api.patch("/v1/auth/me", data);

// Campaigns
export const getCampaigns = (params?: object) =>
  api.get("/v1/campaigns/", { params });
export const getMyCampaigns = () => api.get("/v1/campaigns/my");
export const getCampaign = (id: string) => api.get(`/v1/campaigns/${id}`);
export const createCampaign = (data: object) => api.post("/v1/campaigns/", data);
export const updateCampaign = (id: string, data: object) =>
  api.patch(`/v1/campaigns/${id}`, data);
export const deleteCampaign = (id: string) => api.delete(`/v1/campaigns/${id}`);
export const activateCampaign = (id: string) =>
  api.post(`/v1/campaigns/${id}/activate`);
export const applyToCampaign = (id: string) =>
  api.post(`/v1/campaigns/${id}/apply`);

// Influencers
export const getInfluencers = (params?: object) =>
  api.get("/v1/influencers/", { params });
export const getInfluencerMe = () => api.get("/v1/influencers/profile");
export const updateInfluencerMe = (data: object) =>
  api.patch("/v1/influencers/profile", data);
export const createInfluencerProfile = (data: object) =>
  api.post("/v1/influencers/profile", data);
export const smartSearch = (data: object) =>
  api.post("/v1/influencers/smart-search", data);

// Merchants
export const getMerchantMe = () => api.get("/v1/merchants/profile");
export const createMerchantProfile = (data: object) =>
  api.post("/v1/merchants/profile", data);
export const updateMerchantMe = (data: object) =>
  api.patch("/v1/merchants/profile", data);
export const getMerchantAnalytics = () => api.get("/v1/merchants/analytics");

// Bookings
export const createBooking = (data: object) => api.post("/v1/bookings/", data);
export const getMyBookings = () => api.get("/v1/bookings/my");
export const getBooking = (id: number) => api.get(`/v1/bookings/${id}`);
export const confirmBooking = (id: number) =>
  api.post(`/v1/bookings/${id}/confirm`);
export const cancelBooking = (id: number) =>
  api.post(`/v1/bookings/${id}/cancel`);
export const submitContent = (id: number, data: object) =>
  api.post(`/v1/bookings/${id}/submit-content`, data);
export const approveContent = (id: number) =>
  api.post(`/v1/bookings/${id}/approve-content`);
export const releaseFunds = (id: number) =>
  api.post(`/v1/bookings/${id}/release-funds`);

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
export const getWalletTransactions = () => api.get("/v1/wallet/transactions");
export const redeemPoints = (points: number) =>
  api.post("/v1/wallet/redeem", { points });

// Contracts
export const generateContract = (data: object) =>
  api.post("/v1/contracts/generate", data);
export const policyQA = (question: string, language: string) =>
  api.post(`/v1/contracts/policy-qa?question=${encodeURIComponent(question)}&language=${language}`);

// Admin
export const getPlatformStats    = () => api.get("/v1/admin/platform-stats");
export const getAdminUsers       = () => api.get("/v1/admin/users");
export const getAdminDisputes    = () => api.get("/v1/admin/disputes");
export const resolveDispute      = (escrowId: number, decision: string, reason: string) =>
  api.post(`/v1/admin/disputes/${escrowId}/resolve`, { decision, reason });
export const toggleUserActive    = (id: string) => api.patch(`/v1/admin/users/${id}/toggle-active`);
export const changeUserRole      = (id: string, role: string) => api.patch(`/v1/admin/users/${id}/role`, { role });
export const deleteUser          = (id: string) => api.delete(`/v1/admin/users/${id}`);
export const triggerJob          = (job: "scoring" | "escrow_release" | "reaudit") =>
  api.post(`/v1/admin/trigger/${job}`);
export const rebuildRag          = () => api.post("/v1/admin/rag/rebuild");
export const blastNotification   = (data: { message_ar: string; message_en?: string; target_role: string }) =>
  api.post("/v1/admin/notification/blast", data);
export const forceUpdateCampaign = (id: number, status: string) =>
  api.patch(`/v1/admin/campaigns/${id}/status`, { status });

// Messages
export const getBookingMessages = (bookingId: number) =>
  api.get(`/v1/messages/booking/${bookingId}`);
export const sendMessage = (data: object) => api.post("/v1/messages/", data);
export const getUnreadCount = () => api.get("/v1/messages/unread-count/me");

// Chatbot
export const askChatbot = (message: string, lang: string) =>
  api.post("/v1/chat/onboarding", { message, language: lang });

// Creative Strategists
export const getMyStrategistProfile = () => api.get("/v1/creative-strategists/profile/me");
export const createStrategistProfile = (data: object) => api.post("/v1/creative-strategists/profile", data);
export const updateStrategistProfile = (data: object) => api.put("/v1/creative-strategists/profile/me", data);
export const listStrategists = (params?: object) => api.get("/v1/creative-strategists/", { params });

// Campaign Ideas
export const submitIdea = (data: object) => api.post("/v1/ideas/", data);
export const getMyIdeas = () => api.get("/v1/ideas/my");
export const listIdeas = (params?: object) => api.get("/v1/ideas/", { params });
export const getIdea = (id: string) => api.get(`/v1/ideas/${id}`);
export const updateIdea = (id: string, data: object) => api.put(`/v1/ideas/${id}`, data);
export const withdrawIdea = (id: string) => api.delete(`/v1/ideas/${id}`);
export const engageStrategist = (ideaId: string, data: object) => api.post(`/v1/ideas/${ideaId}/engage`, data);
export const completeEngagement = (engagementId: string) => api.post(`/v1/ideas/engagements/${engagementId}/complete`);
export const getMyEngagements = () => api.get("/v1/ideas/engagements/my");

// Content Creators
export const getMyCreatorProfile = () => api.get("/v1/content-creators/profile/me");
export const createCreatorProfile = (data: object) => api.post("/v1/content-creators/profile", data);
export const updateCreatorProfile = (data: object) => api.put("/v1/content-creators/profile/me", data);
export const listCreators = (params?: object) => api.get("/v1/content-creators/", { params });
export const getCreator = (id: string) => api.get(`/v1/content-creators/${id}`);

// Booking Requests
export const sendBookingRequest = (data: object) => api.post("/v1/content-creators/booking-requests", data);
export const getReceivedBookings = () => api.get("/v1/content-creators/booking-requests/received");
export const getSentBookings = () => api.get("/v1/content-creators/booking-requests/sent");
export const acceptBooking = (id: string) => api.put(`/v1/content-creators/booking-requests/${id}/accept`);
export const declineBooking = (id: string) => api.put(`/v1/content-creators/booking-requests/${id}/decline`);

// CC Engagements
export const getMyCCEngagements = () => api.get("/v1/content-creators/engagements/");
export const getCCEngagement = (id: string) => api.get(`/v1/content-creators/engagements/${id}`);
export const submitIdeaBrief = (id: string, data: object) => api.put(`/v1/content-creators/engagements/${id}/submit-idea`, data);
export const approveIdeaBrief = (id: string) => api.put(`/v1/content-creators/engagements/${id}/approve-idea`);
export const completeCCEngagement = (id: string) => api.put(`/v1/content-creators/engagements/${id}/complete`);
export const rateCCCreator = (id: string, data: object) => api.put(`/v1/content-creators/engagements/${id}/rate`, data);

// Portfolio Items
export const createPortfolioItem = (data: object) => api.post("/v1/portfolio/", data);
export const listPortfolioItems = (params?: object) => api.get("/v1/portfolio/", { params });
export const getMyPortfolio = () => api.get("/v1/portfolio/mine");
export const getPortfolioItem = (id: string) => api.get(`/v1/portfolio/${id}`);
export const updatePortfolioItem = (id: string, data: object) => api.put(`/v1/portfolio/${id}`, data);
export const deletePortfolioItem = (id: string) => api.delete(`/v1/portfolio/${id}`);

// Onboarding Chat
export const onboardingChat = (message: string, role?: string) =>
  api.post("/v1/chat/onboarding", { message, role });
