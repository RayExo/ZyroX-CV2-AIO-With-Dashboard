<div align="center">

# ZyroX Dashboard

Next.js web dashboard for configuring the ZyroX Discord bot.

</div>

---

## Overview

- **Discord OAuth login** — users only see servers they can manage
- **Server-side API proxy** — `DASHBOARD_API_KEY` never exposed to the browser
- **Guild permission checks** — bot API verifies Discord Manage Server / Admin rights
- **Fully branded** — name and colours via environment variables
- **Vercel-ready**

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Node.js 18+ | — |
| ZyroX bot running | with `API_ENABLED=true` on `127.0.0.1` (or via Cloudflare Tunnel) |
| Discord OAuth app | from [Discord Developer Portal](https://discord.com/developers/applications) |

---

## Setup

### 1 — Install dependencies

```bash
npm install
```

### 2 — Configure environment

Create `.env.local` in this folder (see `.env.example`):

```env
# ── Bot API (server-side only — never use NEXT_PUBLIC_ for the key) ──
DASHBOARD_API_URL             = http://127.0.0.1:8000/api/v1
DASHBOARD_API_KEY             = same_secret_as_bot_DASHBOARD_API_KEY

# ── NextAuth ──────────────────────────────────────────────────────
NEXTAUTH_URL                  = http://localhost:3000
NEXTAUTH_SECRET               = a_long_random_string

# ── Discord OAuth ─────────────────────────────────────────────────
DISCORD_CLIENT_ID             = your_discord_oauth_client_id
DISCORD_CLIENT_SECRET         = your_discord_oauth_client_secret

# ── Admin & Branding ──────────────────────────────────────────────
ADMIN_IDS                     = your_discord_user_id
NEXT_PUBLIC_ADMIN_IDS         = your_discord_user_id
NEXT_PUBLIC_BRAND_NAME        = "ZyroX"
NEXT_PUBLIC_BRAND_NAME_WORD   = "ZX"
```

### 3 — Run locally

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Environment Reference

| Variable | Description |
|---|---|
| `DASHBOARD_API_URL` | Bot API URL (server-side). Local: `http://127.0.0.1:8000/api/v1` |
| `DASHBOARD_API_KEY` | Must match bot `DASHBOARD_API_KEY` — **server-side only** |
| `NEXTAUTH_URL` | Dashboard public URL |
| `NEXTAUTH_SECRET` | Random secret for NextAuth session signing |
| `DISCORD_CLIENT_ID` | Discord OAuth2 client ID |
| `DISCORD_CLIENT_SECRET` | Discord OAuth2 client secret |
| `ADMIN_IDS` | Server-side admin user IDs (for admin API routes) |
| `NEXT_PUBLIC_ADMIN_IDS` | Same IDs for admin panel UI visibility |
| `NEXT_PUBLIC_BRAND_NAME` | Bot name in the dashboard UI |
| `NEXT_PUBLIC_BRAND_NAME_WORD` | Short abbreviation (e.g. `ZX`) |

> Do **not** set `NEXT_PUBLIC_DASHBOARD_API_KEY`. The browser uses `/api/proxy`, which adds the secret server-side.

---

## How API auth works

```
Browser  →  /api/proxy/guilds/...  →  Next.js (session check)
         →  Bot API with:
              Authorization: Bearer DASHBOARD_API_KEY
              X-Discord-Access-Token: <oauth token>
              X-Discord-User-Id: <user id>
         →  Bot verifies Discord Manage Server permission per guild
```

SSR (server components) call the bot API directly with the same headers from the active session.

---

## Deployment (Vercel)

1. Connect repo → set root directory to `dashboard/`
2. Add all environment variables from the table above
3. Set `NEXTAUTH_URL` to your Vercel domain
4. Add OAuth redirect: `https://your-app.vercel.app/api/auth/callback/discord`
5. Deploy

For production with Cloudflare Tunnel, set:

```env
DASHBOARD_API_URL=https://api.yourdomain.com/api/v1
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Dashboard can't load data | Bot running with `API_ENABLED=true`, `DASHBOARD_API_URL` correct |
| 401 from bot API | `DASHBOARD_API_KEY` must match bot `.env` exactly |
| 403 on guild routes | User must have Manage Server or Admin on that Discord server |
| Admin panel 403 | Add your Discord ID to `ADMIN_IDS` and bot `DASHBOARD_ADMIN_IDS` |
| Auth error on login | Check Discord OAuth client ID/secret and redirect URI |

See also `SECURITY_FIXES.md` in the project root.
