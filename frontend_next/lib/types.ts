export type Role = "merchant" | "influencer" | "admin";
export type Lang = "en" | "ar";

export type Tier = "PLATINUM" | "GOLD" | "SILVER" | "BRONZE" | "UNRANKED";

export interface User {
  id: number;
  email: string;
  username: string;
  role: Role;
  full_name_en?: string;
  full_name_ar?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
}

export interface MerchantProfile {
  id: number;
  user_id: number;
  business_name_en?: string;
  business_name_ar?: string;
  industry?: string;
  website?: string;
  city?: string;
}

export interface InfluencerProfile {
  id: number;
  user_id: number;
  bio_en?: string;
  bio_ar?: string;
  niche?: string;
  city?: string;
  instagram_handle?: string;
  instagram_followers?: number;
  instagram_engagement_rate?: number;
  tiktok_handle?: string;
  tiktok_followers?: number;
  rate_per_post?: number;
  rate_per_story?: number;
  rate_per_reel?: number;
  aria_score?: number;
  aria_tier?: Tier;
  campaigns_completed?: number;
  is_available?: boolean;
  audience_gender_split?: { female: number; male: number };
  audience_age_split?: Record<string, number>;
  match_score?: number;
}

export type CampaignStatus =
  | "DRAFT"
  | "ACTIVE"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "DISPUTED";

export interface Campaign {
  id: number;
  merchant_id: number;
  title_en?: string;
  title_ar?: string;
  description_en?: string;
  description_ar?: string;
  niche?: string;
  total_budget?: number;
  budget_per_influencer?: number;
  start_date?: string;
  end_date?: string;
  required_deliverables?: string[];
  hashtags?: string[];
  status: CampaignStatus;
  is_featured?: boolean;
}

export type BookingStatus =
  | "PENDING"
  | "CONFIRMED"
  | "CONTENT_SUBMITTED"
  | "CONTENT_APPROVED"
  | "RELEASED"
  | "DISPUTED";

export interface Booking {
  id: number;
  merchant_id: number;
  influencer_id: number;
  campaign_id?: number;
  agreed_rate_jod: number;
  brief?: string;
  deliverables?: string[];
  deadline?: string;
  status: BookingStatus;
  content_url?: string;
  ai_review_result?: string;
  created_at: string;
  influencer?: InfluencerProfile;
  campaign?: Campaign;
}

export type EscrowStatus =
  | "FUNDED"
  | "IN_PROGRESS"
  | "UNDER_REVIEW"
  | "RELEASED"
  | "DISPUTED";

export interface EscrowTransaction {
  id: number;
  campaign_id?: number;
  merchant_id: number;
  gross_amount: number;
  net_amount: number;
  vat_amount: number;
  platform_fee: number;
  status: EscrowStatus;
  funded_at?: string;
  auto_release_at?: string;
  campaign?: Campaign;
}

export interface Wallet {
  id: number;
  user_id: number;
  total_points: number;
  redeemed_points: number;
  available_points: number;
  tier: Tier;
}

export interface Contract {
  id: number;
  campaign_id?: number;
  contract_text: string;
  language: "ar" | "en";
  generated_at: string;
}

export interface Message {
  id: number;
  booking_id: number;
  sender_id: number;
  content: string;
  created_at: string;
  read_at?: string;
}

export interface PlatformStats {
  total_users: number;
  total_merchants: number;
  total_influencers: number;
  active_campaigns: number;
  escrow_locked: number;
  total_escrow_volume?: number;
  platform_fees?: number;
  open_disputes?: number;
  new_users_today?: number;
}

export interface MerchantAnalytics {
  total_budget_spent: number;
  active_campaigns_count: number;
  completed_campaigns_count: number;
  escrow_locked: number;
  recent_budgets: { title: string; budget: number }[];
}
