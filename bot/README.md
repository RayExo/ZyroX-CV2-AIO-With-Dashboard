<div align="center">

```
███████╗██╗   ██╗██████╗  ██████╗ ██╗  ██╗
╚══███╔╝╚██╗ ██╔╝██╔══██╗██╔═══██╗╚██╗██╔╝
  ███╔╝  ╚████╔╝ ██████╔╝██║   ██║ ╚███╔╝ 
 ███╔╝    ╚██╔╝  ██╔══██╗██║   ██║ ██╔██╗ 
███████╗   ██║   ██║  ██║╚██████╔╝██╔╝ ██╗
╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
```

<h3>ZyroX Bot — Python Discord Bot + FastAPI Backend</h3>

<a href="https://nexiohost.in"><img src="https://img.shields.io/badge/⭐%20PREMIUM%20HOSTING-NexioHost-FFD700?style=for-the-badge&labelColor=1a1a2e&color=FFD700&logoColor=FFD700"/></a>

<p>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/></a>
  <a href="https://discordpy.readthedocs.io"><img src="https://img.shields.io/badge/Discord.py-v2-5865F2?style=for-the-badge&logo=discord&logoColor=white"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge"/></a>
</p>
<p>
  <a href="https://discord.gg/codexdev"><img src="https://img.shields.io/badge/Discord-Join_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white"/></a>
  <a href="https://youtube.com/@CodeXDevs"><img src="https://img.shields.io/badge/YouTube-CodeXDevs-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/></a>
  <a href="https://github.com/RayExo"><img src="https://img.shields.io/badge/GitHub-RayExo-181717?style=for-the-badge&logo=github&logoColor=white"/></a>
</p>

</div>

---

## ✦ Overview

This folder contains the ZyroX Discord bot built on `discord.py v2` alongside a `FastAPI` backend that powers the web dashboard. Everything runs from a single `python CodeX.py` command.

```
bot/
├── api/                   FastAPI backend (routes, schemas, db manager)
│   └── routes/            /bot  /guilds  /admin
├── cogs/
│   ├── antinuke/          Antinuke protection event listeners
│   ├── automod/           Automod enforcement event listeners
│   ├── commands/          All slash & prefix command modules
│   ├── events/            General Discord event listeners
│   ├── moderation/        Moderation action modules
│   └── zyrox/             Core ZyroX feature cogs
├── core/                  Bot client, context, cog base classes
├── games/                 Standalone game logic + button views
├── utils/                 Emoji, tools, sync, Cloudflare tunnel
├── assets/                Fonts, backgrounds, GIFs
└── CodeX.py               Entry point
```

---

## ✦ Features

<table>
<tr>
<td width="50%">

**🛡️ Antinuke**
- Mass ban, kick, channel & role flood detection
- Webhook abuse, bot add, prune protection
- Anti-member update
- Whitelist / unwhitelist system
- Emergency lockdown mode

</td>
<td width="50%">

**🤖 Automod**
- Anti-spam, anti-caps, anti-links
- Anti-invites, mass mention, emoji spam
- Fully configurable per server
- Works alongside Discord's native automod

</td>
</tr>
<tr>
<td>

**🎵 Music**
- Lavalink v4 powered playback
- YouTube, SoundCloud, JioSaavn support
- Queue, loop, shuffle, autoplay
- Seek, rewind, forward controls

</td>
<td>

**⚙️ Moderation**
- Ban, kick, mute, warn, lock, jail
- Snipe, message management
- Full logging system
- Reaction roles, vanity roles, invite tracker

</td>
</tr>
<tr>
<td>

**🎉 Engagement**
- Leveling & XP with leaderboard
- Birthday tracker
- Counting, AFK, autorole, autoresponder
- Sticky messages, booster perks, giveaways

</td>
<td>

**🎮 Games**
- Chess, Battleship, Connect Four
- Wordle, Typeracer, 2048, Memory
- Reaction test, RPS, Tic-tac-toe
- Country guess, Number slider, Lights out

</td>
</tr>
<tr>
<td>

**🌐 API Backend**
- FastAPI with API key auth
- SlowAPI rate limiting
- Structured JSON request logging
- CORS configured for your dashboard domain
- `CORS_ORIGINS` env var for extra domains

</td>
<td>

**🔧 Developer**
- Jishaku eval support
- Application emoji auto-sync
- Slash + prefix commands
- Cloudflare Tunnel via pycloudflared — zero system installs, unlimited traffic
- Single `OWNER_IDS` env var controls all permission checks
- CodeX Devs watermark on every source file

</td>
</tr>
</table>

---

## ✦ Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | — |
| Lavalink v4 node | for music features |
| Discord bot token | from Developer Portal |
| Cloudflare account (free) | for HTTPS tunnel — browser setup only |

---

## ✦ Setup

### 1 — Install dependencies

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 2 — Configure environment

Create a `.env` file (copy from `.env.example`):

```env
# ── Core ──────────────────────────────────────────────────────────
TOKEN              = your_discord_bot_token
brand_name         = 'ZyroX'

# ── Owner IDs (REQUIRED — your Discord user ID) ───────────────────
OWNER_IDS          = YOUR_DISCORD_USER_ID_HERE

# ── Lavalink ──────────────────────────────────────────────────────
LAVALINK_HOST      = "your-lavalink-host"
LAVALINK_PASSWORD  = "your_password"
LAVALINK_SECURE    = "true"
LAVALINK_PORT      = ""

# ── Emoji Sync ────────────────────────────────────────────────────
EMOJI_SYNC         = "false"

# ── API / Dashboard Backend ───────────────────────────────────────
API_ENABLED        = "false"
API_HOST           = "127.0.0.1"
API_PORT           = "8000"
DASHBOARD_API_KEY  = "change_this_to_a_strong_secret"
DASHBOARD_ADMIN_IDS = YOUR_DISCORD_USER_ID_HERE
CORS_ORIGINS       = ""

# ── Cloudflare Tunnel (optional) ──────────────────────────────────
TUNNEL_ENABLED     = "false"
CF_TUNNEL_TOKEN    = "your_tunnel_token"
CF_TUNNEL_URL      = "https://api.yourdomain.com"

# ── Webhooks (optional) ─────────────────────────────────────────────
# CMD_WEBHOOK_URL    = "https://discord.com/api/webhooks/ID/TOKEN"
```

### 3 — Run

```bash
python CodeX.py
```

---

## ✦ Environment Reference

| Variable | Default | Description |
|---|---|---|
| `TOKEN` | — | Discord bot token |
| `OWNER_IDS` | _(required)_ | Comma-separated owner Discord user IDs — **your own ID only** |
| `LAVALINK_HOST` | — | Lavalink server hostname (no protocol) |
| `LAVALINK_PASSWORD` | — | Lavalink password |
| `LAVALINK_SECURE` | `true` | `true` = HTTPS, `false` = HTTP |
| `LAVALINK_PORT` | _(empty)_ | Port — only when `LAVALINK_SECURE=false` |
| `EMOJI_SYNC` | `false` | Auto-sync application emojis on startup |
| `JISHAKU_ENABLED` | `false` | Enable owner debug REPL (disable in production) |
| `API_ENABLED` | `false` | Start the FastAPI dashboard backend |
| `API_HOST` | `127.0.0.1` | Bind address for the API server |
| `API_PORT` | `8000` | Port the backend listens on |
| `DASHBOARD_API_KEY` | — | Shared secret with dashboard (server-side only) |
| `DASHBOARD_ADMIN_IDS` | — | Discord user IDs for admin API routes |
| `CORS_ORIGINS` | _(empty)_ | Extra CORS-allowed origins, comma-separated |
| `CMD_WEBHOOK_URL` | _(empty)_ | Optional webhook for command logging |
| `TUNNEL_ENABLED` | `false` | Expose API over HTTPS via Cloudflare Tunnel |
| `CF_TUNNEL_TOKEN` | — | Token from Cloudflare Zero Trust dashboard |
| `CF_TUNNEL_URL` | — | Your permanent public URL |
| `LOG_CHANNEL_ID` | _(empty)_ | Optional channel for join/leave logs |

> **API security:** All `/api/v1/guilds/*` routes verify Discord Manage Server permission via `X-Discord-Access-Token` header.

---

## ✦ HTTPS Tunnel (Cloudflare)

Uses **pycloudflared** — downloads the `cloudflared` binary automatically on first run. No system installs, no CLI, works on Pterodactyl and any Python host.

**Why Cloudflare over ngrok:**

| | Cloudflare Tunnel | ngrok free |
|---|---|---|
| Bandwidth | Unlimited | 1 GB/month |
| Requests | Unlimited | 10k/month |
| URL stability | Permanent | Permanent (1 domain) |
| System install | ❌ Not needed | ❌ Not needed |
| Cost | Free | Free |

**Setup (browser only — no CLI needed):**

1. Go to [one.dash.cloudflare.com](https://one.dash.cloudflare.com) → **Networks → Tunnels → Create a tunnel**
2. Choose **Cloudflared**, name it (e.g. `zyrox-api`), save
3. On **Install connector**, copy the token from the command shown:
   ```
   cloudflared tunnel run --token <COPY_THIS_TOKEN>
   ```
4. On **Public Hostname** tab → add a hostname:
   - Subdomain: `api` · Domain: `yourdomain.com` · Service: `http://localhost:8000`
5. Add to `.env`:
   ```env
   CF_TUNNEL_TOKEN = "eyJhIjoiXXXX..."
   CF_TUNNEL_URL   = "https://api.yourdomain.com"
   ```

On every startup the console prints:
```
◈ Tunnel: cloudflared binary ready — starting tunnel on port 8000…
◈ Tunnel: API is live at  https://api.yourdomain.com
  ↳ DASHBOARD_API_URL = https://api.yourdomain.com/api/v1
```

Set `TUNNEL_ENABLED=false` to disable.

---

## ✦ Emoji Sync

When `EMOJI_SYNC=true`, the bot syncs application emojis on every startup:

| Event | Action |
|---|---|
| New emoji found | Uploaded to application, ID written to `emoji.py` |
| Stale ID detected | `emoji.py` patched automatically |
| No changes | Sync completes instantly, no restart |
| After any patch | Bot restarts so fresh IDs are live |

---

## ✦ Deployment

Upload the entire `bot/` folder to your host and set the start command to:

```bash
python CodeX.py
```

`pycloudflared` downloads the binary on first run — no extra steps on any host.

> Recommended free hosts: Render · Railway · Fly.io · Pterodactyl
>
> ⭐ **[NexioHost](https://nexiohost.in)** — Premium bot hosting, built for Discord bots. Fast, reliable, and affordable.

---

## ✦ Troubleshooting

| Problem | Fix |
|---|---|
| Bot fails to start | Check `TOKEN` and gateway intents in Developer Portal |
| Music not working | Verify `LAVALINK_HOST`, `LAVALINK_SECURE`, `LAVALINK_PORT` |
| Dashboard can't reach API | Check `API_ENABLED=true`, `DASHBOARD_API_URL` in dashboard, and Discord login |
| CORS errors | Add your Vercel URL to `CORS_ORIGINS` in `.env` |
| Emojis showing as plain text | Run once with `EMOJI_SYNC=true` to upload and patch IDs |
| Tunnel not starting | Check `CF_TUNNEL_TOKEN` is valid and `pycloudflared` is installed |
| Want to add an owner | Add their ID to `OWNER_IDS` in `.env` — no code changes needed |

---

<div align="center">

## ✦ CodeX Devs

*Built for protection. Designed for style.*

<a href="https://discord.gg/codexdev"><img src="https://discord.com/api/guilds/1301573144817045524/widget.png?style=banner2" alt="CodeX Development Discord Server" width="480"/></a>

<p>
  <a href="https://discord.gg/codexdev"><img src="https://img.shields.io/badge/Discord-Join_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white"/></a>
  <a href="https://youtube.com/@CodeXDevs"><img src="https://img.shields.io/badge/YouTube-CodeXDevs-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/></a>
  <a href="https://github.com/RayExo"><img src="https://img.shields.io/badge/GitHub-RayExo-181717?style=for-the-badge&logo=github&logoColor=white"/></a>
  <a href="https://nexiohost.in"><img src="https://img.shields.io/badge/⭐%20PREMIUM%20HOSTING-NexioHost-FFD700?style=for-the-badge&labelColor=1a1a2e&color=FFD700&logoColor=FFD700"/></a>
</p>

© 2026 CodeX Devs — MIT License

</div>
