# 🔒 Security hardening — comprehensive patch

Hi! I audited this bot + dashboard and put together a focused security patch. Every change below was made to close a concrete, exploitable issue found during the audit. No behavior or feature was removed — this is pure hardening.

I'm happy to **split this into smaller PRs** (one per area) if you prefer; I kept it as one comprehensive patch so the security posture is consistent. Just say the word.

---

## Critical (fixed)

| # | Issue | Fix |
|---|---|---|
| **C1** | The shared backend API key was `NEXT_PUBLIC_DASHBOARD_API_KEY`, so Next.js inlined it into the **client JS bundle** — any visitor could read it from DevTools and own the API. | `lib/api.ts` is now dual-mode: Server Components call the backend directly with a **server-only** `DASHBOARD_API_KEY`; Client Components go through a new same-origin **`/api/proxy/[...path]`** route handler that attaches the key server-side. The key is never shipped to the browser. |
| **C2** | `bot/.env.example` and `dashboard/.env.example` shipped **concrete default values** for `DASHBOARD_API_KEY` and `NEXTAUTH_SECRET`. An operator who copies them unchanged deploys with publicly-known credentials (forgeable session JWTs). | Placeholders blanked; `config.py` now `validate_critical_secrets()` at startup and **refuses to boot** on known-default / too-short secrets. |
| **C3** | **IDOR**: `app/dashboard/guild/[guildId]/layout.tsx` fetched any guild's data from the URL `guildId` with **no membership check** — any logged-in user could read/edit any guild's config. | The proxy enforces `MANAGE_GUILD`/`ADMINISTRATOR` on `guilds/{id}/*`; the guild layout also checks membership server-side. |
| **C4** | 37 `.db` files containing **real Discord user/guild IDs** were committed. | Added `*.db` / `*.db-journal` / `*.sqlite*` to `.gitignore` and untracked them. |
| **C5** | (Not changed — out of scope for this security patch.) |  |
| **C6** | In verification `both` mode (the schema default), the **Quick Verify** button granted the verified role **without a CAPTCHA**. | Changed the gate to `!= "button"` so Quick Verify only grants in pure-button mode. |

> Note: C5 (the `nitro` cog) is intentionally left untouched here — it's a product/UX decision, not a security vulnerability, so it doesn't belong in a security-only PR.

## High (fixed)

- **RCE / insecure deserialization (H1):** `eval()` on strings read from SQLite (`ai.py` trivia history, `autorole.py` role lists) → **`ast.literal_eval`**. Safe parser for the existing `str()` repr; no code execution. Becomes important because the `.db` files were committed (C4).
- **Supply chain (C8/H2):** `paginators.py` ran `os.system("pip install git+https://...")` from a **mutable branch at import time** → replaced with a clear `ImportError`. `discord-ext-menus` is already a declared dependency.
- **Admin endpoints (H3):** `/admin/*` now require a server-admin session (enforced in the proxy).
- **Admin IDs leak (H4):** `NEXT_PUBLIC_ADMIN_IDS` → server-only `ADMIN_IDS`; the sidebar resolves admin status via a new `/api/me` route.
- **SSRF (H13/H20/H21/M15):** new `utils/safehttp.py` guard wired into `rickroll`, role-icon upload, `analyze_image`, and `delete_hook` (allow-lists `discord.com`). Blocks loopback/private/link-local/cloud-metadata targets.
- **OWNER_IDS backdoor (H12):** `OWNER_IDS` is now **required** (no silent fallback to a hardcoded ID).
- **Hardcoded third-party keys (H11):** MapQuest / Pexels / Giphy / Spotify keys moved to env vars; features degrade gracefully when unset.
- **CORS (H8):** removed the shipped placeholder origin; restricted methods/headers to what's used.
- **Verification, deps, cog authz (C6/H18/H22/H24):** Quick-Verify fix; removed typo-squat/invalid deps from `requirements.txt` (`discord`, `discord.ui`, `discord.ext-context`, `collection`, stdlib dupes); reaction-role hierarchy + dangerous-permission checks; `jailhistory` permission gate.

## Files
~30 source files + 37 untracked `.db`. New: `dashboard/app/api/proxy/[...path]/route.ts`, `dashboard/app/api/me/route.ts`, `dashboard/lib/auth-utils.ts`, `bot/utils/safehttp.py`.

## Verification
- `python -m py_compile` passes on all edited Python files.
- Dashboard changes are **type-reviewed + grep-verified**; `npm install` + `next build` is recommended before merge (I couldn't run them in my environment).
- `eval(` fully removed from the touched modules; no residual `NEXT_PUBLIC_` secrets.

## Suggested follow-ups (intentionally out of scope here)
- Pin a specific `cloudflared` version + verify SHA-256 on download (`tunnel.py`).
- Add `package-lock.json` + run `npm audit` / `pip-audit`.
- `customrole` self-escalation (H23), `dmstaff` consent/audit (H25), antinuke dead listeners (H26), antinuke cooldown-queues-instead-of-drops (H27), rate-limit trusted-proxy (H7), `middleware.ts` for `/dashboard` (H5).

## Env migration for operators
- Rename `NEXT_PUBLIC_DASHBOARD_API_KEY` → `DASHBOARD_API_KEY`
- Rename `NEXT_PUBLIC_ADMIN_IDS` → `ADMIN_IDS`
- `OWNER_IDS` is now **required** (bot won't start without it)

Thanks for the project! 🙌 Happy to adjust anything.
