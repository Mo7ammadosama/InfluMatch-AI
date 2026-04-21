# WaslAI — Next.js Frontend

## Quick Start

```bash
cd C:/InfluMatch_AI/frontend_next

# 1. Install dependencies
npm install

# 2. Set environment
# Edit .env.local:  set JWT_SECRET to match the backend's JWT secret

# 3. Start dev server (runs on port 3000)
npm run dev

# Backend must be running on port 8080 (existing FastAPI)
```

## Routes

| Path | Description |
|---|---|
| `/` | Home / landing page |
| `/login` | Login |
| `/register` | Register (merchant or influencer) |
| `/merchant/dashboard` | Merchant KPIs + campaigns |
| `/influencer/dashboard` | Influencer ARIA score + campaigns |
| `/discover` | AI-powered influencer search (merchant) |
| `/bookings` | Booking lifecycle + messages |
| `/bookings/new` | Booking wizard (from discover) |
| `/campaigns` | Campaign list (role-aware) |
| `/open-campaigns` | Browse open campaigns (influencer) |
| `/escrow` | Escrow transactions |
| `/contracts` | Smart contract generator |
| `/wallet` | Loyalty wallet + redeem |
| `/settings` | Profile & preferences |
| `/admin` | God Mode (admin only) |

## JWT Auth

- Token stored in cookie `waslai_token` (httpOnly-safe, 7-day expiry)
- `middleware.ts` verifies JWT on every protected route
- Cross-role access blocked automatically

## Design System

Dark theme matching original Streamlit design:
- Background: `#0c0c13`
- Merchant accent: amber `#f59e0b`  
- Influencer accent: violet `#7c3aed`
- Admin accent: red `#ef4444`
- Fonts: Cairo (Arabic) + Inter (English)
- RTL auto-switch when language = Arabic
