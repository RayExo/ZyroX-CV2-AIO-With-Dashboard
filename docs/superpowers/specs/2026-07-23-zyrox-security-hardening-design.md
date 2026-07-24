# ZyroX-CV2 — Security Hardening Design Spec

**Fecha:** 2026-07-23 · **Repo de trabajo:** `C:\MisArchivos\Proyectos Codigos\ZyroX-hardened` (fuera de OneDrive) · **Baseline commit:** `a60f268`

## Objetivo
Blindar ZyroX-CV2 para que la comunidad pueda montarlo con sus propias claves/host de forma segura. Contribuir los arreglos upstream como PRs enfocados.

## Alcance
- **IN:** solo arreglos de seguridad (auth, secretos, inyección, SSRF, cadena de suministro, authz de cogs, infra).
- **OUT (decisión del maintainer):** telemetría (H17), cog nitro (C5), webhook de comandos (H14) se conservan intactos.

## Enfoque
- Un branch por PR desde el baseline.
- Cada PR autocontenido, con justificación de seguridad y referencia al hallazgo (C#/H#/M#) de la auditoría.

## PRs

### PR #1 — Secretos & defaults  `[C2 H11 H12]`
- [x] `bot/.env.example`: blankar TOKEN, OWNER_IDS, DASHBOARD_API_KEY, LAVALINK_*
- [x] `dashboard/.env.example`: blankar NEXTAUTH_SECRET, NEXT_PUBLIC_DASHBOARD_API_KEY, NEXT_PUBLIC_ADMIN_IDS
- [x] `bot/utils/config.py`: OWNER_IDS required (raise si vacío); `_INSECURE_DEFAULTS`; `validate_critical_secrets()`
- [ ] `bot/CodeX.py`: llamar `validate_critical_secrets()` al arranque
- [ ] Mover keys hardcodeadas (MapQuest/Spotify/Pexels/Giphy) a env; deshabilitar feature si falta

### PR #2 — Dashboard auth  `[C1 C3 H3-H10]`
- [ ] Quitar `NEXT_PUBLIC_` de la API key (server-only)
- [ ] Route Handler proxy `app/api/proxy/[...path]/route.ts`
- [ ] Recablear componentes cliente a `/api/proxy/*`
- [ ] Chequeo `manage_guild` server-side en guild layout
- [ ] Admin API vía proxy server que revalide `isAdmin()`
- [ ] Callback `signIn` de NextAuth (allow-list)
- [ ] `ADMIN_IDS` server-only
- [ ] `middleware.ts` gateando `/dashboard`

### PR #3 — Inyección / RCE / SSRF  `[C4 H1 H2 H13 H20 H21 M15]`
- [ ] `eval`→`json.loads` en `ai.py` (119,149,167) + `autorole.py` (235,268,306,339)
- [ ] `.gitignore` `*.db` + `git rm --cached bot/db/*.db`
- [ ] Quitar `pip install` en import (`paginators.py`)
- [ ] Allowlists SSRF: `rickroll`, `roleicon`, `analyze_image`, `delete_hook`

### PR #4 — Verificación + supply chain  `[C6 H15 H16 H18 H19]`
- [ ] `verification.py`: no otorgar rol sin captcha en modo `both`
- [ ] Pinear `cloudflared` + verificar SHA-256 en `tunnel.py`
- [ ] Pinear deps en `requirements.txt`; lockfile del dashboard

### PR #5 (extreme) — Cog authz + antinuke + infra  `[H7 H8 H22-H27]`
- [ ] Jerarquía en `reactionroles`/`customrole`
- [ ] perm-check en `jailhistory`; consent/cooldown en `dms`
- [ ] Antinuke: renombrar listeners webhook muertos; encolar (no descartar) en cooldown
- [ ] CORS fail-closed; rate-limit con trusted-proxy

## Testing
- Por PR: grep-scan de confirmación + razonamiento manual documentado en el cuerpo del PR.
- Sin token de Discord aquí; el usuario verifica runtime tras merge.

## Estrategia upstream
- 5 PRs enfocados a `github.com/RayExo/ZyroX-CV2-With-Dashboard`.
- El fork queda como versión hardened para la comunidad sin importar si el autor mergeea.
