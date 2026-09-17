export type Role = "merchant" | "influencer" | "admin" | "creative_strategist" | "content_creator";
export type Lang = "en" | "ar";

export type Tier = "PLATINUM" | "GOLD" | "SILVER" | "BRONZE" | "UNRANKED";

export interface User {
  id: string;
  email: string;
  username?: string;
  role: Role;
  full_name: string;
  full_name_en?: string;
  full_name_ar?: string;
  phone?: string;
  is_active: boolean;
  is_verified?: boolean;
  created_at: string;
}

export interface MerchantProfile {
  id: string;
  user_id: string;
  business_name: string;
  business_name_ar?: string;
  business_category: string;
  description?: string;
  description_ar?: string;
  website?: string;
  city?: string;
  total_spent_jod?: number;
  active_campaigns?: number;
  is_verified?: boolean;
}

export interface InfluencerProfile {
  id: string;
  user_id: string;
  display_name: string;
  bio?: string;
  bio_ar?: string;
  city?: string;
  social_platforms?: Record<string, { handle?: string; followers?: number; engagement_rate?: number }>;
  content_categories?: string[];
  languages?: string[];
  rate_per_post_jod?: number;
  rate_per_story_jod?: number;
  rate_per_reel_jod?: number;
  total_followers?: number;
  avg_engagement_rate?: number;
  aria_score?: number;
  aria_tier?: Tier;
  completed_deals?: number;
  is_available?: boolean;
  avg_rating?: number;
  is_verified?: boolean;
  match_score?: number;
}

export type CampaignStatus =
  | "draft"
  | "active"
  | "in_progress"
  | "completed"
  | "cancelled"
  | "paused";

export interface Campaign {
  id: string;
  merchant_id: string;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  target_categories?: string[];
  required_platforms?: string[];
  min_followers?: number;
  total_budget_jod: number;
  spent_budget_jod?: number;
  max_influencers?: number;
  start_date?: string;
  end_date?: string;
  status: CampaignStatus;
  ai_brief_summary?: string;
  cc_engagement_id?: string;
  created_at?: string;
}

export type BookingStatus =
  | "proposed"
  | "negotiating"
  | "accepted"
  | "in_progress"
  | "content_submitted"
  | "content_approved"
  | "amount_transferred"
  | "published"
  | "completed"
  | "disputed"
  | "cancelled";

export interface Booking {
  id: string;
  campaign_id?: string;
  influencer_id: string;
  agreed_amount_jod: number;
  agreed_rate_jod?: number;
  vat_amount_jod?: number;
  platform_fee_jod?: number;
  total_amount_jod?: number;
  notes?: string;
  brief?: string;
  deliverables?: Record<string, unknown>;
  deadline?: string;
  status: BookingStatus;
  content_urls?: string[];
  escrow_id?: string;
  created_at: string;
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
  sender_id: string;
  sender_name?: string;
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

export interface CreativeStrategistProfile {
  id: string;
  user_id: string;
  display_name: string;
  display_name_ar?: string;
  bio?: string;
  bio_ar?: string;
  avatar_url?: string;
  city?: string;
  portfolio_url?: string;
  specializations: string[];
  languages: string[];
  consultation_rate_jod: number;
  completed_engagements: number;
  milestone_count: number;
  total_earned_jod: number;
  avg_rating: number;
  is_verified: boolean;
  is_available: boolean;
  created_at: string;
}

export type CampaignIdeaStatus = "open" | "in_progress" | "completed" | "withdrawn";

export interface CampaignIdea {
  id: string;
  creative_strategist_id: string;
  title: string;
  title_ar?: string;
  description: string;
  description_ar?: string;
  target_audience?: string;
  suggested_platforms: string[];
  content_format: string[];
  influencer_type?: string;
  business_category?: string;
  estimated_budget_jod?: number;
  timeline_days?: number;
  status: CampaignIdeaStatus;
  view_count: number;
  adoption_count: number;
  created_at: string;
}

export type CreativeEngagementStatus = "pending" | "active" | "completed" | "cancelled";

export interface CreativeEngagement {
  id: string;
  campaign_idea_id: string;
  merchant_id: string;
  creative_strategist_id: string;
  status: CreativeEngagementStatus;
  agreed_fee_jod: number;
  merchant_notes?: string;
  strategist_notes?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

// ── Content Creator types ──────────────────────────────────────────────────────

export interface ContentCreatorProfile {
  id: string;
  user_id: string;
  display_name: string;
  display_name_ar?: string;
  bio?: string;
  bio_ar?: string;
  avatar_url?: string;
  city?: string;
  portfolio_url?: string;
  specializations: string[];
  languages: string[];
  content_categories: string[];
  consultation_rate_jod: number;
  completed_engagements: number;
  total_earned_jod: number;
  avg_rating: number;
  is_verified: boolean;
  is_available: boolean;
  created_at: string;
}

export interface ContentCreatorSummary {
  id: string;
  display_name: string;
  display_name_ar?: string;
  avatar_url?: string;
  city?: string;
  specializations: string[];
  avg_rating: number;
  completed_engagements: number;
  is_available: boolean;
}

export interface PortfolioItem {
  id: string;
  content_creator_id: string;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  campaign_type?: string;
  business_categories: string[];
  platforms: string[];
  content_formats: string[];
  example_concept?: string;
  example_concept_ar?: string;
  view_count: number;
  is_published: boolean;
  created_at: string;
}

export type BookingRequestStatus = "pending" | "accepted" | "declined" | "expired";

export interface BookingRequest {
  id: string;
  merchant_id: string;
  content_creator_id: string;
  portfolio_item_id?: string;
  business_description?: string;
  business_description_ar?: string;
  campaign_goal?: string;
  target_audience?: string;
  budget_jod?: number;
  timeline_days?: number;
  status: BookingRequestStatus;
  merchant_notes?: string;
  creator_response?: string;
  created_at: string;
  merchant_business_name?: string;
  merchant_business_name_ar?: string;
  creator_display_name?: string;
  creator_display_name_ar?: string;
}

export type CCEngagementStatus = "active" | "idea_submitted" | "idea_approved" | "completed" | "cancelled";

export interface CCEngagement {
  id: string;
  booking_request_id: string;
  merchant_id: string;
  content_creator_id: string;
  campaign_id?: string;
  status: CCEngagementStatus;
  agreed_fee_jod: number;
  platform_share_percent: number;
  idea_brief?: string;
  idea_brief_ar?: string;
  merchant_feedback?: string;
  creator_rating?: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  creator_display_name?: string;
  merchant_business_name?: string;
}
