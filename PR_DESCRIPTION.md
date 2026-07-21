# Security: Remove backdoors, enforce secure defaults, and harden API

## Summary

Security audit and hardening of the ZyroX CV2 AIO Discord bot with dashboard. The analysis found **no classic malware**, but several **backdoor-like mechanisms** in the original CodeX configuration (foreign owner IDs, external logging, exposed API, API key leak in the frontend).

This PR addresses **10 security issues** and introduces **secure defaults**: without a proper `.env` configuration, no foreign user retains owner rights, no external logging occurs, and the API is not publicly exposed.

### Fixed Risks

| # | Issue | Fix |
|---|-------|-----|
| 1 | Hardcoded foreign `OWNER_IDS` | No fallback — without `.env`, no one has owner rights |
| 2 | Jishaku (Python REPL) always enabled | Opt-in only via `JISHAKU_ENABLED=true` |
| 3 | Command logging to external webhooks | Only with a valid, complete `CMD_WEBHOOK_URL` |
| 4 | Hardcoded Discord channel IDs | Configurable via `LOG_CHANNEL_ID`, etc. |
| 5 | API bound to `0.0.0.0`, tunnel enabled by default | `API_ENABLED=false`, `API_HOST=127.0.0.1`, `TUNNEL_ENABLED=false` |
| 6 | API key exposed in browser (`NEXT_PUBLIC_*`) | Server-side proxy in Next.js, key stays server-only |
| 7 | `eval()` in calculator/autorole | New `safe_parse.py` with AST-based eval and JSON |
| 8 | Auto `pip install` / binary download | Manual installation, download opt-in only |
| 9 | Fake commands `hack`/`token`/`wizz` | Removed |
| 10 | Bot API without Discord permission checks | `discord_auth.py` + token/admin validation |

### Additional Hardening (Follow-up Audit)

- API proxy requires login + guild/admin permission checks
- Guild list filtered to manageable servers only
- Fixed crash when `command is None` in `on_command_completion`
- Server-only `ADMIN_IDS` support added

---

## Breaking Changes / Migration

**Bot (`bot/.env`):**

```env
TOKEN=...
OWNER_IDS=YOUR_DISCORD_USER_ID
DASHBOARD_API_KEY=strong_secret
```

**Dashboard (`dashboard/.env`):**

```env
DASHBOARD_API_URL=http://127.0.0.1:8000/api/v1
DASHBOARD_API_KEY=same_value_as_bot
```

Remove `NEXT_PUBLIC_DASHBOARD_API_KEY` if still set.

Optional for dashboard/API:

```env
API_ENABLED=true
LOG_CHANNEL_ID=...
```

---

## Test Plan

- [ ] Bot starts without `OWNER_IDS` and shows a warning; owner commands do not work
- [ ] With `OWNER_IDS` set, owner commands work as expected
- [ ] Jishaku loads only when `JISHAKU_ENABLED=true`
- [ ] No webhook logging without a valid `CMD_WEBHOOK_URL`
- [ ] No join/leave logging without `LOG_CHANNEL_ID`
- [ ] API disabled by default; when enabled, binds to `127.0.0.1` only
- [ ] Dashboard API calls go through `/api/proxy` — key not visible in browser
- [ ] Unauthenticated proxy access is rejected
- [ ] Guild API requires Discord token + Manage Server/Admin on target guild
- [ ] Calculator: safe expressions work, injection attempts rejected
- [ ] `hack`/`token`/`wizz` commands no longer exist
- [ ] README and `.env.example` (bot + dashboard) updated

---

## Context

Based on the full security analysis in `PROJEKT_ANALYSE.md` and the applied fixes documented in `SECURITY_FIXES.md`.
