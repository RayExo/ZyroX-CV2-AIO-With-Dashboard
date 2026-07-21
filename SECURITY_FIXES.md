# Security Remediation Advisory

| Field | Value |
|-------|-------|
| **Advisory ID** | ZYROX-SEC-2026-REM |
| **Related Report** | [PROJEKT_ANALYSE.md](PROJEKT_ANALYSE.md) (ZYROX-SEC-2026-001) |
| **Publication Date** | 2026-07-21 |
| **Status** | Patches applied — operator action required |
| **Classification** | Internal — Distribution Restricted |
| **Affected Product** | ZyroX CV2 AIO Discord Bot with Dashboard |

---

## 1. Advisory Summary

This document tracks remediation of findings identified during static security assessment **ZYROX-SEC-2026-001**. Ten primary findings (ZYROX-2026-001 through ZYROX-2026-010) were addressed through configuration hardening, access-control improvements, and code changes. A follow-up review on the same date identified six additional issues in the remediation itself; all were resolved prior to closing this advisory.

**Operator action is still required** post-update: environment files must be created or migrated per Section 6.

---

## 2. Remediation Index

| Fix | Finding ID | Title | Severity | Status |
|-----|------------|-------|----------|--------|
| #1 | ZYROX-2026-001 | Hardcoded owner fallback | Critical | ✅ Applied |
| #2 | ZYROX-2026-002 | Jishaku enabled by default | Critical | ✅ Applied |
| #3 | ZYROX-2026-003 | Command webhook telemetry | Critical | ✅ Applied |
| #4 | ZYROX-2026-004 | Hardcoded log channel IDs | High | ✅ Applied |
| #5 | ZYROX-2026-005 | Over-exposed API defaults | High | ✅ Applied |
| #6 | ZYROX-2026-006 | Client-exposed API key | High | ✅ Applied |
| #7 | ZYROX-2026-007 | Unsafe eval() usage | Medium | ✅ Applied |
| #8 | ZYROX-2026-008 | Runtime pip/binary fetch | Medium | ✅ Applied |
| #9 | ZYROX-2026-009 | Deceptive commands | Medium | ✅ Applied |
| #10 | ZYROX-2026-005 (ext.) | Missing Discord auth on API | High | ✅ Applied |

---

## 3. Patch Details

### Fix #1 — Remove Hardcoded Owner Fallback

**Finding:** ZYROX-2026-001  
**Root cause:** `_parse_ids()` supplied third-party Discord UID `870179991462236170` when `OWNER_IDS` unset.

| File | Change |
|------|--------|
| `bot/utils/config.py` | `_parse_ids()` returns empty list on missing env var |
| `bot/CodeX.py` | Startup warning when `OWNER_IDS` is empty |
| `bot/.env.example` | Placeholder `YOUR_DISCORD_USER_ID_HERE`; foreign IDs removed |
| `dashboard/.env.example` | `ADMIN_IDS` placeholder replaces foreign ID |

**Post-patch behavior:** No principal receives owner privileges without explicit configuration. Bot emits warning on empty `OWNER_IDS`.

**Migration:**
```env
OWNER_IDS=<your_discord_snowflake>
```

---

### Fix #2 — Jishaku Opt-In

**Finding:** ZYROX-2026-002  
**Root cause:** Unconditional `load_extension("jishaku")` at startup.

| File | Change |
|------|--------|
| `bot/utils/config.py` | `JISHAKU_ENABLED` flag (default: `false`) |
| `bot/CodeX.py` | Conditional extension load |
| `bot/.env.example` | Documented opt-in flag |

**Post-patch behavior:** Jishaku inactive unless `JISHAKU_ENABLED=true`. Recommended for local debugging only.

---

### Fix #3 — Webhook URL Validation

**Finding:** ZYROX-2026-003  
**Root cause:** Command logging fired on placeholder or empty webhook URLs.

| File | Change |
|------|--------|
| `bot/utils/config.py` | `_valid_webhook_url()` rejects empty/placeholder values |
| `bot/CodeX.py` | `on_command_completion` early-return when URL invalid |

**Post-patch behavior:** No outbound command telemetry without fully qualified, operator-configured webhook URL.

---

### Fix #4 — Externalize Log Channel IDs

**Finding:** ZYROX-2026-004  
**Root cause:** Hardcoded snowflakes (`1396794297386532978`, etc.) in multiple modules.

| File | Change |
|------|--------|
| `bot/utils/config.py` | `LOG_CHANNEL_ID`, `SERVER_COUNT_CHANNEL_ID`, `USER_COUNT_CHANNEL_ID` |
| `bot/CodeX.py` | Config-driven channel references; stats task gated on config |
| `bot/cogs/events/on_guild.py` | Join/leave logging conditional on `LOG_CHANNEL_ID` |
| `bot/cogs/commands/np.py` | Audit logs use `LOG_CHANNEL_ID` |
| `bot/.env.example` | Optional IDs documented (commented) |

**Post-patch behavior:** Zero external telemetry channels unless explicitly configured.

**Migration (optional):**
```env
LOG_CHANNEL_ID=<channel_snowflake>
SERVER_COUNT_CHANNEL_ID=<channel_snowflake>
USER_COUNT_CHANNEL_ID=<channel_snowflake>
```

---

### Fix #5 — Secure API Defaults

**Finding:** ZYROX-2026-005  
**Root cause:** API enabled on `0.0.0.0`; tunnel enabled by default.

| File | Change |
|------|--------|
| `bot/utils/config.py` | `API_ENABLED=false`, `API_HOST=127.0.0.1`, `TUNNEL_ENABLED=false` |
| `bot/CodeX.py` | Bind to `API_HOST`; warn on `0.0.0.0` |
| `bot/.env.example` | Secure defaults documented |

**Post-patch behavior:** API and tunnel disabled until explicitly enabled. Localhost binding by default.

**Migration (dashboard use case):**
```env
API_ENABLED=true
API_HOST=127.0.0.1
DASHBOARD_API_KEY=<cryptographically_random_secret>
```

---

### Fix #6 — Server-Side API Proxy

**Finding:** ZYROX-2026-006  
**Root cause:** `NEXT_PUBLIC_DASHBOARD_API_KEY` inlined into browser bundle.

| File | Change |
|------|--------|
| `dashboard/app/api/proxy/[...path]/route.ts` | **New** — authenticated server-side proxy |
| `dashboard/lib/api.ts` | Client → `/api/proxy`; SSR → direct with server env |
| `dashboard/.env.example` | `DASHBOARD_API_KEY` (server-only); public key removed |

**Post-patch architecture:**
```
Browser  →  GET /api/proxy/guilds/...  →  Next.js (session)  →  Bot API + Bearer token
SSR      →  Bot API direct (process.env.DASHBOARD_API_KEY)
```

**Migration:**
```env
DASHBOARD_API_URL=http://127.0.0.1:8000/api/v1
DASHBOARD_API_KEY=<same_value_as_bot_env>
```
Remove `NEXT_PUBLIC_DASHBOARD_API_KEY` from any existing `.env`.

---

### Fix #7 — Replace eval() with Safe Parsers

**Finding:** ZYROX-2026-007  
**Root cause:** Dynamic evaluation of user input and DB-stored strings.

| File | Change |
|------|--------|
| `bot/utils/safe_parse.py` | **New** — `safe_math_eval()`, `parse_role_id_list()`, `dump_role_id_list()` |
| `bot/cogs/commands/calc.py` | AST-limited arithmetic evaluator |
| `bot/cogs/commands/autorole.py` | JSON / `ast.literal_eval` for list deserialization |

**Post-patch behavior:** Calculator restricted to `[0-9+\-*/(). ]`. Autorole lists persisted as JSON with legacy read support.

**Verification:** Unit tests confirm `safe_math_eval('2+2')` succeeds; injection payloads rejected.

---

### Fix #8 — Disable Runtime Package Installation

**Finding:** ZYROX-2026-008  
**Root cause:** `os.system("pip install ...")` and unsolicited `cloudflared` download.

| File | Change |
|------|--------|
| `bot/utils/paginators.py` | ImportError with install instructions (no auto-pip) |
| `bot/utils/tunnel.py` | Binary download gated on `TUNNEL_ALLOW_BINARY_DOWNLOAD=true` |
| `bot/.env.example` | `TUNNEL_ALLOW_BINARY_DOWNLOAD=false` |

**Post-patch behavior:** Dependencies declared in `requirements.txt`; runtime installs removed.

---

### Fix #9 — Remove Deceptive Commands

**Finding:** ZYROX-2026-009  
**Root cause:** Commands simulating credential theft and server destruction.

| File | Change |
|------|--------|
| `bot/cogs/commands/general.py` | Removed `hack`, `token`, `wizz`; dead code cleanup |
| `bot/cogs/zyrox/general.py` | Help index updated |

**Post-patch behavior:** Commands no longer registered. No regression in remaining general commands.

---

### Fix #10 — Discord Permission Enforcement on Bot API

**Finding:** Extension of ZYROX-2026-005 (identified in follow-up review)  
**Root cause:** API accepted bearer token alone; no guild-scoped authorization.

| File | Change |
|------|--------|
| `bot/api/discord_auth.py` | **New** — token validation, Manage Guild / Admin checks |
| `bot/api/server.py` | Middleware on `/api/v1/guilds`, `/api/v1/admin`, `/api/v1/bot` |
| `bot/api/routes/guilds.py` | `GET /guilds` filtered to authorized guilds |
| `dashboard/lib/api.ts` | Forwards `X-Discord-Access-Token` on SSR |
| `dashboard/app/api/proxy/[...path]/route.ts` | Header passthrough + session enforcement |
| `bot/.env.example` | `DASHBOARD_ADMIN_IDS` documented |
| `README.md`, `bot/README.md`, `dashboard/README.md` | Secure configuration guidance |

**Post-patch behavior:** Guild-scoped endpoints require valid Discord OAuth token with Manage Guild or Administrator permission on target guild.

---

## 4. Follow-Up Review (2026-07-21)

Secondary pass on remediation code identified gaps in the initial proxy implementation. All items below were patched same-day.

| Issue | Severity | Resolution |
|-------|----------|------------|
| API proxy accessible without session | Critical | Session gate + guild/admin validation in proxy route |
| Guild dashboard pages lacking authZ check | High | `guild/[guildId]/layout.tsx` enforces Discord permissions |
| `GET /guilds` returned all bot guilds | High | Proxy filters to user-manageable intersection |
| `on_command_completion` NullPointer on `command is None` | Medium | Guard clause in `CodeX.py` |
| Orphaned `jishaku` import in `bot/core/zyrox.py` | Low | Import removed |
| Admin check relied solely on `NEXT_PUBLIC_ADMIN_IDS` | Medium | Server-side `ADMIN_IDS` supported |

---

## 5. Verification & Test Results

| Test | Method | Result |
|------|--------|--------|
| Python syntax | `py_compile` on modified modules | Pass |
| Safe parser unit tests | `safe_parse` test suite | Pass — arithmetic OK, injection blocked |
| Hardcoded channel ID grep | Static scan of `bot/` | Pass — no hardcoded snowflakes in code paths |
| Public API key exposure | Grep `NEXT_PUBLIC_DASHBOARD_API_KEY` | Pass — removed from code and examples |
| Proxy auth bypass (manual) | Unauthenticated request to `/api/proxy/*` | Pass — 401/403 |

**Regression scope:** General commands, guild config API, dashboard OAuth flow. No automated E2E suite present at time of review.

---

## 6. Operator Deployment Checklist

Execute after pulling patched codebase:

| Step | Action | Required |
|------|--------|----------|
| 1 | Create/update `bot/.env` with `TOKEN`, `OWNER_IDS` | Yes |
| 2 | Create/update `dashboard/.env` with server-only `DASHBOARD_API_KEY` | Yes |
| 3 | Delete `NEXT_PUBLIC_DASHBOARD_API_KEY` from legacy configs | Yes |
| 4 | Set `LOG_CHANNEL_ID` etc. if logging desired | Optional |
| 5 | Enable `API_ENABLED=true` only when dashboard is deployed | Optional |
| 6 | Set `JISHAKU_ENABLED=true` only for controlled debugging | Optional |

---

## 7. Intentionally Unchanged (Accepted Risk)

| Item | Rationale | Risk Level |
|------|-----------|------------|
| Developer credits in `mention.py`, `stats.py` | Cosmetic attribution | Informational |
| CodeX file headers | Branding | Informational |
| `discord.gg/codexdev` in welcome templates | Operator-configurable content | Informational |

These items do not constitute exploitable vulnerabilities under the assessed threat model.

---

## 8. Residual Recommendations

| Area | Recommendation | Priority |
|------|----------------|----------|
| SQLite at rest | Restrict filesystem permissions on `bot/db/` | P2 |
| Secret rotation | Rotate `DASHBOARD_API_KEY` and `TOKEN` on suspected compromise | P1 |
| Dependency pinning | Lock `requirements.txt` / `package-lock.json` hashes | P2 |
| AutoBlacklist cog | Review before enabling — aggressive auto-ban behavior | P3 |
| Lavalink | Self-host node; avoid third-party defaults (`lavalink.jirayu.net`) | P3 |

---

## 9. Document History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-07-21 | Initial remediation (Fixes #1–#9) |
| 1.1 | 2026-07-21 | Follow-up review + Fix #10 (Discord API authZ) |

---

**End of Advisory**

*Cross-reference: vulnerability details and threat context in [PROJEKT_ANALYSE.md](PROJEKT_ANALYSE.md).*
