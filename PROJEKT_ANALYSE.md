# Security Assessment Report

| Field | Value |
|-------|-------|
| **Report ID** | ZYROX-SEC-2026-001 |
| **Target** | ZyroX CV2 AIO Discord Bot with Dashboard |
| **Repository** | `ZyroX-CV2-AIO-With-Dashboard-main` |
| **Assessment Date** | 2026-07-21 |
| **Report Version** | 1.0 |
| **Classification** | Internal — Distribution Restricted |
| **Assessment Type** | Static source-code review, configuration analysis, threat modeling |
| **Assessor** | Independent security review (automated + manual verification) |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-21 | Security Review | Initial assessment |

**Scope:** Full repository including `bot/` (Python/discord.py), `bot/api/` (FastAPI), and `dashboard/` (Next.js). Out of scope: runtime penetration testing, infrastructure review, third-party Lavalink/OpenAI endpoints.

**Methodology:**
1. Recursive static analysis of source tree (~200+ Python/TypeScript files)
2. Configuration default and `.env.example` review
3. Identification of trust boundaries (Discord ↔ Bot ↔ API ↔ Dashboard ↔ Internet)
4. Mapping findings to [CWE](https://cwe.mitre.org/) where applicable
5. Severity assignment per internal scale (Critical → Informational)

**Limitations:** This assessment reflects the codebase state at review time. No dynamic exploitation was performed against a live deployment. Residual risk may exist in unreviewed dependencies.

---

## 1. Executive Summary

A security review of the ZyroX CV2 AIO Discord bot (originally published by CodeX Devs) was conducted to determine whether the repository contains malicious code and to identify exploitable misconfigurations.

### 1.1 Malware Classification

| Indicator | Result |
|-----------|--------|
| Known malware signatures (trojan, RAT, cryptominer, token stealer) | Not observed |
| Obfuscated or packed payloads | Not observed |
| Committed binary artifacts (`.exe`, `.dll`, `.sh`) | None |
| Covert C2 / unknown outbound endpoints | Not observed |
| Intentional third-party control primitives | **Confirmed** (see Findings) |

**Verdict:** The codebase does **not** exhibit characteristics of traditional malware. However, **default configuration and hardcoded identifiers create effective pre-positioned access** for third parties if an operator deploys without modification. This pattern is classified as **latent supply-chain / configuration backdoor risk**, not as a self-propagating trojan.

### 1.2 Risk Overview

| Severity | Count | Representative Issues |
|----------|-------|---------------------|
| Critical | 3 | Hardcoded owner fallback, Jishaku RCE, command telemetry webhook |
| High | 3 | Hardcoded log channels, exposed API surface, client-side API key |
| Medium | 3 | `eval()` usage, runtime package/binary fetch, deceptive commands |
| Low | 1 | Developer branding / optional telemetry hooks |
| **Total** | **10** | |

**Operational impact if deployed with defaults:** A third-party Discord account retains bot owner privileges; command metadata and guild join events may be exfiltrated to external Discord channels/webhooks; owner-level Jishaku access enables host-level code execution.

---

## 2. System Overview & Attack Surface

### 2.1 Architecture

```
                    ┌─────────────────────────────────────┐
                    │           Trust Boundary            │
  Discord Users ───►│  discord.py Gateway (bot/CodeX.py)  │
                    │         │              │            │
                    │         ▼              ▼            │
                    │    SQLite (bot/db/)  FastAPI :8000  │
                    │                           │         │
  Web Users ───────►│  Next.js Dashboard :3000 ◄┘         │
                    │         │                           │
                    │         ▼ (optional)                  │
                    │  Cloudflare Tunnel → Internet       │
                    └─────────────────────────────────────┘
```

### 2.2 Trust Boundaries

| Boundary | Authentication | Authorization Gap (pre-remediation) |
|----------|----------------|-------------------------------------|
| Discord → Bot | Discord token, owner ID list | Owner list defaulted to third party |
| Bot → External webhooks/channels | None (hardcoded destinations) | Unauthenticated telemetry sink |
| Dashboard → Bot API | Bearer `DASHBOARD_API_KEY` | No Discord permission binding |
| Browser → Dashboard API | OAuth session (partial) | API key embedded in client bundle |
| Internet → FastAPI | API key only when tunnel enabled | Binds `0.0.0.0` by default |

### 2.3 Expanded Attack Surface

Beyond a typical Discord bot, this project includes:

| Component | Path | Notes |
|-----------|------|-------|
| Web dashboard | `dashboard/` | OAuth, guild configuration UI |
| REST API | `bot/api/` | Full guild config CRUD |
| Cloudflare tunnel | `bot/utils/tunnel.py` | Optional public exposure |
| Lavalink integration | `bot/cogs/commands/music.py` | External dependency |
| AI modules | `bot/cogs/commands/ai.py` | External API calls |
| Embedded games/utilities | `bot/games/`, various cogs | Expanded code surface |

These components are **in scope for the product design** but increase exposure relative to a minimal bot.

---

## 3. Detailed Findings

Findings are indexed as `ZYROX-2026-NNN`. Severity uses: **Critical**, **High**, **Medium**, **Low**, **Informational**.

---

### ZYROX-2026-001 — Hardcoded Owner ID Fallback

| Attribute | Value |
|-----------|-------|
| **Severity** | Critical |
| **CWE** | [CWE-1188](https://cwe.mitre.org/data/definitions/1188.html) — Insecure Default Initialization of Resource |
| **CVSS 3.1 (est.)** | 9.1 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H) |
| **Status at review** | Open → Remediated in `SECURITY_FIXES.md` (#1) |

**Affected component:** `bot/utils/config.py`

**Description:** When `OWNER_IDS` is absent from environment configuration, the bot falls back to a hardcoded Discord snowflake belonging to the original maintainer.

```python
OWNER_IDS: list[int] = _parse_ids("OWNER_IDS", [870179991462236170])
```

**Impact:** Unconfigured deployments grant **full bot owner privileges** to UID `870179991462236170`, including process restart (`reload`), cross-guild moderation, global blacklist, invite generation, and access to Jishaku (Finding 002).

**Evidence:** `bot/utils/config.py`; additional third-party IDs present in `bot/.env.example`.

**Owner-capable commands (non-exhaustive):** `reload`, `leaveguild`, `makeinvite`, `GB`, `global kick`, `global timeout`, `blacklist user/guild`.

**Remediation:**
- Remove hardcoded fallback; fail closed or warn when `OWNER_IDS` is empty
- Replace example IDs with placeholders
- Operator must set `OWNER_IDS=<own_discord_id>`

---

### ZYROX-2026-002 — Jishaku Extension Enabled by Default

| Attribute | Value |
|-----------|-------|
| **Severity** | Critical |
| **CWE** | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) / [CWE-94](https://cwe.mitre.org/data/definitions/94.html) |
| **CVSS 3.1 (est.)** | 9.8 (AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H) |
| **Status at review** | Open → Remediated (#2) |

**Affected component:** `bot/CodeX.py` (~L345)

```python
await client.load_extension("jishaku")
```

**Description:** [Jishaku](https://github.com/Gorialis/jishaku) provides an in-Discord Python REPL restricted to bot owners. Any principal in `OWNER_IDS` can execute arbitrary Python on the host process.

**Impact:** Full host compromise under owner account compromise or misconfigured `OWNER_IDS` (chained with Finding 001).

**Remediation:** Load Jishaku only when `JISHAKU_ENABLED=true`; default `false`. Never enable in production.

---

### ZYROX-2026-003 — Command Telemetry via Discord Webhook

| Attribute | Value |
|-----------|-------|
| **Severity** | Critical |
| **CWE** | [CWE-359](https://cwe.mitre.org/data/definitions/359.html) — Exposure of Private Personal Information |
| **CVSS 3.1 (est.)** | 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N) |
| **Status at review** | Open → Remediated (#3) |

**Affected component:** `bot/CodeX.py` → `on_command_completion`

**Description:** Non-owner command invocations are POSTed to `CMD_WEBHOOK_URL` with command text, user ID, guild name/ID, and channel ID. Owner commands are explicitly excluded from logging.

**Impact:** Webhook controller receives **cross-guild activity intelligence**. Privacy violation; potential GDPR relevance depending on jurisdiction.

**Remediation:** Disable by default; validate URL before enabling; use operator-controlled webhook only.

---

### ZYROX-2026-004 — Hardcoded Discord Channel IDs for Telemetry

| Attribute | Value |
|-----------|-------|
| **Severity** | High |
| **CWE** | [CWE-798](https://cwe.mitre.org/data/definitions/798.html) — Use of Hard-coded Credentials (analogous) |
| **Status at review** | Open → Remediated (#4) |

**Affected components:**

| File | Channel ID | Function |
|------|------------|----------|
| `bot/CodeX.py` | `1396794297386532978` | Guild join notifications |
| `bot/CodeX.py` | `1419729255977189467` | Server count display |
| `bot/CodeX.py` | `1419729283861184632` | Member count display |
| `bot/cogs/events/on_guild.py` | `1396794297386532978` | Join/leave detail logs |
| `bot/cogs/commands/np.py` | `1396794297386532978` | No-prefix command audit |

**Impact:** Guild metadata (name, owner, member count, invite links) transmitted to channels controlled by the original developer.

**Remediation:** Externalize to `LOG_CHANNEL_ID`, `SERVER_COUNT_CHANNEL_ID`, `USER_COUNT_CHANNEL_ID`; no logging when unset.

---

### ZYROX-2026-005 — Over-Exposed FastAPI with Optional Public Tunnel

| Attribute | Value |
|-----------|-------|
| **Severity** | High |
| **CWE** | [CWE-284](https://cwe.mitre.org/data/definitions/284.html) — Improper Access Control |
| **Status at review** | Open → Partially remediated (#5, #10) |

**Affected components:** `bot/api/server.py`, `bot/utils/tunnel.py`, `bot/CodeX.py`

**Description:** API listens on `0.0.0.0:8000` by default. Cloudflare tunnel can expose localhost to the public internet. Authentication is a single shared bearer token without per-guild Discord authorization (pre-fix).

**Sensitive endpoints (sample):**
- `PATCH /api/v1/guilds/{id}/automod`
- `PATCH /api/v1/guilds/{id}/antinuke`
- `PATCH /api/v1/guilds/{id}/verification`
- `PATCH /api/v1/admin/config`

**Impact:** API key compromise → full configuration manipulation across all guilds.

**Remediation:** Default `API_ENABLED=false`, `API_HOST=127.0.0.1`, `TUNNEL_ENABLED=false`; bind Discord OAuth token + guild admin checks (Fix #10).

---

### ZYROX-2026-006 — API Key Embedded in Client Bundle

| Attribute | Value |
|-----------|-------|
| **Severity** | High |
| **CWE** | [CWE-522](https://cwe.mitre.org/data/definitions/522.html) — Insufficiently Protected Credentials |
| **Status at review** | Open → Remediated (#6) |

**Affected component:** `dashboard/lib/api.ts`

```typescript
const API_KEY = process.env.NEXT_PUBLIC_DASHBOARD_API_KEY;
```

**Description:** Next.js inlines `NEXT_PUBLIC_*` variables into client JavaScript. Any dashboard visitor can extract the bearer token.

**Impact:** Unauthenticated API access if combined with reachable bot API (Finding 005).

**Remediation:** Server-side proxy route; `DASHBOARD_API_KEY` server-only; remove `NEXT_PUBLIC_DASHBOARD_API_KEY`.

---

### ZYROX-2026-007 — Unsafe Dynamic Code Evaluation (`eval`)

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium |
| **CWE** | [CWE-95](https://cwe.mitre.org/data/definitions/95.html) — Improper Neutralization of Directives in Eval |
| **Status at review** | Open → Remediated (#7) |

**Affected components:**

| File | Line(s) | Context |
|------|---------|---------|
| `bot/cogs/commands/calc.py` | 92 | User-supplied expression |
| `bot/cogs/commands/autorole.py` | 235, 268, 306, 339 | DB-persisted list parsing |

**Impact:** Local RCE if an attacker can write SQLite records or abuse calculator input validation gaps.

**Remediation:** AST-limited math evaluator; JSON/`ast.literal_eval` for structured data.

---

### ZYROX-2026-008 — Runtime Dependency Installation & Binary Fetch

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium |
| **CWE** | [CWE-829](https://cwe.mitre.org/data/definitions/829.html) — Inclusion of Functionality from Untrusted Control Sphere |
| **Status at review** | Open → Remediated (#8) |

**Affected components:** `bot/utils/tunnel.py`, `bot/utils/paginators.py`

**Description:** Application invokes `pip install` via `os.system` and downloads `cloudflared` from GitHub at runtime.

**Impact:** Supply-chain compromise if upstream artifact is tampered; violates principle of immutable deployments.

**Remediation:** Declare dependencies in `requirements.txt`; opt-in binary download via `TUNNEL_ALLOW_BINARY_DOWNLOAD=true`.

---

### ZYROX-2026-009 — Deceptive User-Facing Commands

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium (Social Engineering) |
| **CWE** | [CWE-451](https://cwe.mitre.org/data/definitions/451.html) — User Interface (UI) Misrepresentation of Critical Information |
| **Status at review** | Open → Remediated (#9) |

**Affected component:** `bot/cogs/commands/general.py`

| Command | Behavior | Actual harm |
|---------|----------|-------------|
| `hack @user` | Fabricated credentials | None |
| `token @user` | Random 59-char string | None |
| `wizz` | Simulated destruction UI | None |

**Impact:** No technical exploitation; reputational and social-engineering risk.

**Remediation:** Remove or clearly label as parody commands.

---

### ZYROX-2026-010 — Developer Branding & Dormant Telemetry Hooks

| Attribute | Value |
|-----------|-------|
| **Severity** | Low / Informational |
| **Status at review** | Acknowledged — no code change required |

**Description:** >100 files contain CodeX branding headers (`discord.gg/codexdev`). Commented `autoblacklist` cog references external support channel. Help footers link to developer Discord.

**Impact:** No direct exploitation path; increases fingerprinting and social-trust surface.

---

## 4. Finding Summary Matrix

| ID | Title | Severity | Exploitability | Data Impact | Remediation Priority |
|----|-------|----------|----------------|-------------|---------------------|
| ZYROX-2026-001 | Hardcoded owner fallback | Critical | Trivial (default deploy) | Full bot control | P0 |
| ZYROX-2026-002 | Jishaku RCE | Critical | Requires owner access | Host compromise | P0 |
| ZYROX-2026-003 | Command webhook telemetry | Critical | Passive (default URL) | User/guild metadata | P0 |
| ZYROX-2026-004 | Hardcoded log channels | High | Passive | Guild intelligence | P1 |
| ZYROX-2026-005 | Exposed FastAPI + tunnel | High | Requires key/network | Config takeover | P1 |
| ZYROX-2026-006 | Client-exposed API key | High | Trivial (view source) | Config takeover | P1 |
| ZYROX-2026-007 | eval() injection | Medium | Conditional | Local RCE | P2 |
| ZYROX-2026-008 | Runtime pip/binary fetch | Medium | Supply-chain | Integrity | P2 |
| ZYROX-2026-009 | Deceptive commands | Medium | Social | None (technical) | P2 |
| ZYROX-2026-010 | Branding / telemetry hooks | Low | N/A | N/A | P3 |

---

## 5. Pre-Deployment Checklist (Operator)

### P0 — Before first production start

- [ ] Set `OWNER_IDS` to operator-controlled Discord account(s)
- [ ] Verify no third-party IDs in `.env` or `.env.example`
- [ ] Confirm `JISHAKU_ENABLED` is unset or `false`
- [ ] Leave `CMD_WEBHOOK_URL` empty unless operator-owned
- [ ] Replace or unset all hardcoded log channel IDs

### P1 — Before exposing dashboard/API

- [ ] Generate cryptographically strong `DASHBOARD_API_KEY` (≥32 bytes entropy)
- [ ] Set `API_HOST=127.0.0.1`; enable tunnel only if required
- [ ] Confirm API key is **not** prefixed with `NEXT_PUBLIC_`
- [ ] Validate Discord OAuth permission checks on guild routes

### P2 — Hardening

- [ ] Audit SQLite file permissions on `bot/db/`
- [ ] Review `eval()` replacements in calculator/autorole modules
- [ ] Pin dependencies; disable runtime installs
- [ ] Remove or relabel parody moderation commands

---

## Appendix A — Repository Structure

### A.1 Root

| Path | Description |
|------|-------------|
| `bot/` | Python Discord bot, FastAPI, SQLite persistence |
| `dashboard/` | Next.js 14+ dashboard with NextAuth |
| `PROJEKT_ANALYSE.md` | This report |
| `SECURITY_FIXES.md` | Remediation advisory |

### A.2 Bot Core (`bot/`)

| Component | Role |
|-----------|------|
| `CodeX.py` | Process entry: bot, API thread, optional tunnel |
| `core/zyrox.py` | `AutoShardedBot` subclass, prefix resolution |
| `utils/config.py` | Centralized environment configuration |
| `api/` | FastAPI REST layer for dashboard |
| `cogs/` | Feature modules (~80+ extensions) |
| `db/` | Per-module SQLite databases |

### A.3 Bot API Routes (`bot/api/`)

| Route group | Capability |
|-------------|------------|
| `/api/v1/guilds/*` | Guild-scoped configuration CRUD |
| `/api/v1/admin/*` | Global stats, maintenance mode |
| `/api/v1/bot/*` | Bot status |

**Authentication (post-remediation):** Bearer `DASHBOARD_API_KEY` + `X-Discord-Access-Token` with guild permission validation.

### A.4 Dashboard (`dashboard/`)

OAuth via NextAuth → guild list intersection (bot present ∧ user has Manage Guild) → proxied API calls to bot backend.

Key paths: `app/dashboard/guild/[guildId]/*`, `app/api/proxy/[...path]/route.ts`, `lib/api.ts`.

---

## Appendix B — Persistence Layer

| Database | Contents |
|----------|----------|
| `prefix.db` | Per-guild command prefixes |
| `automod.db` | Automod rule configuration |
| `block.db` | Global user/guild denylist |
| `leveling.db` | XP and rank data |
| `tickets.db`, `welcome.db`, `antinuke.db`, `verification.db` | Module configs |
| `admin_config.db` | Maintenance mode flag |

All databases are local SQLite files under `bot/db/`. No encryption at rest observed.

---

## Appendix C — Environment Variables

### Bot (`.env`)

| Variable | Required | Security note |
|----------|----------|---------------|
| `TOKEN` | Yes | Discord bot secret — never commit |
| `OWNER_IDS` | Yes | Must be operator-controlled |
| `DASHBOARD_API_KEY` | If API enabled | Shared secret; rotate on compromise |
| `CMD_WEBHOOK_URL` | No | Disable unless operator-owned |
| `API_ENABLED` / `API_HOST` / `TUNNEL_ENABLED` | No | Secure defaults: off / 127.0.0.1 / off |
| `JISHAKU_ENABLED` | No | Default: false |

### Dashboard (`.env`)

| Variable | Required | Security note |
|----------|----------|---------------|
| `DISCORD_CLIENT_SECRET` | Yes | Server-side only |
| `DASHBOARD_API_KEY` | Yes | Server-side only — **not** `NEXT_PUBLIC_*` |
| `NEXTAUTH_SECRET` | Yes | Session integrity |

---

## Appendix D — Startup Sequence

```
python bot/CodeX.py
  ├─ load_dotenv()
  ├─ FastAPI thread (if API_ENABLED)
  ├─ Cloudflare tunnel (if TUNNEL_ENABLED)
  ├─ discord.py client.start(TOKEN)
  │    ├─ load cogs (~80+)
  │    ├─ load jishaku (if JISHAKU_ENABLED)
  │    └─ sync slash commands
  └─ on_ready → background tasks

npm run dev (dashboard/)
  ├─ Next.js :3000
  └─ /api/proxy/* → Bot FastAPI (server-side key)
```

---

## 6. Conclusion

ZyroX CV2 AIO is a feature-rich Discord bot platform, not a self-propagating malware sample. The primary security concern is **deployment-time trust delegation**: unchanged defaults effectively assign operational control and observability to the original publisher.

Operators treating this as production software must treat initial configuration as a **security-critical step**, equivalent to key ceremony for any SaaS deployment.

Remediation details and verification results are documented in **`SECURITY_FIXES.md`** (Advisory ZYROX-SEC-2026-REM).

---

**End of Report**

*For remediation status and patch verification, see `SECURITY_FIXES.md`.*
