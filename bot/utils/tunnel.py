# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

"""
HTTPS Tunnel for the ZyroX API — Cloudflare Tunnel via pycloudflared.

Zero manual installs. Just:
  1. pip install pycloudflared  (already in requirements.txt)
  2. Get your tunnel token from the Cloudflare dashboard (browser only, no CLI)
  3. Set CF_TUNNEL_TOKEN in .env

That's it. The cloudflared binary is downloaded automatically on first run.

──────────────────────────────────────────────────────────────────────────────
How to get your CF_TUNNEL_TOKEN (browser only, no CLI needed)
──────────────────────────────────────────────────────────────────────────────
1. Go to https://one.dash.cloudflare.com
2. Networks → Tunnels → Create a tunnel
3. Choose "Cloudflared" as connector type
4. Give it a name (e.g. zyrox-api) and click Save
5. On the "Install connector" step, find the token in the command shown:
      cloudflared tunnel run --token <YOUR_TOKEN_HERE>
   Copy just the token string.
6. Go to "Published Application Routes" tab → Add a Published Application Routes:
      Subdomain: zyrox-api   Domain: yourdomain.com   Service: http://localhost:8000
   (Or use any domain you have on Cloudflare)
7. Paste the token into your .env:
      CF_TUNNEL_TOKEN = "eyJhIjoiX..."
      CF_TUNNEL_URL   = "https://zyrox-api.yourdomain.com"

That's the permanent URL — never changes between restarts.
Unlimited bandwidth, unlimited requests, free.
──────────────────────────────────────────────────────────────────────────────
"""

import os
import time
import threading
import subprocess

# ── env vars ──────────────────────────────────────────────────────────────────
from utils.config import TUNNEL_ENABLED, TUNNEL_ALLOW_BINARY_DOWNLOAD, API_PORT

CF_TUNNEL_TOKEN = os.getenv("CF_TUNNEL_TOKEN", "").strip()   # token from Cloudflare dashboard
CF_TUNNEL_URL   = os.getenv("CF_TUNNEL_URL", "").strip()     # e.g. https://api.yourdomain.com

# ── colours ───────────────────────────────────────────────────────────────────
_CYAN   = "\033[36m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_RED    = "\033[31m"
_RESET  = "\033[0m"


def _ensure_pycloudflared() -> bool:
    """Return True if pycloudflared is installed (no automatic pip install)."""
    try:
        import pycloudflared  # noqa: F401
        return True
    except ImportError:
        print(
            f"{_RED}◈ Tunnel: pycloudflared is not installed.\n"
            f"  Install manually: pip install pycloudflared{_RESET}"
        )
        return False


def _download_cloudflared_direct() -> str | None:
    """
    Last-resort: download the cloudflared binary directly from GitHub
    into a local ./bin/ directory. Works even if pycloudflared fails.
    """
    import platform
    import urllib.request
    import stat

    system  = platform.system().lower()   # linux / darwin / windows
    machine = platform.machine().lower()  # x86_64 / aarch64 / arm64

    # Map to Cloudflare's release naming
    if system == "linux":
        if machine in ("aarch64", "arm64"):
            asset = "cloudflared-linux-arm64"
        elif machine == "arm":
            asset = "cloudflared-linux-arm"
        else:
            asset = "cloudflared-linux-amd64"
    elif system == "darwin":
        asset = "cloudflared-darwin-amd64"
    elif system == "windows":
        asset = "cloudflared-windows-amd64.exe"
    else:
        print(f"{_RED}◈ Tunnel: unsupported OS '{system}' for direct download.{_RESET}")
        return None

    url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/{asset}"
    bin_dir = os.path.join(os.path.dirname(__file__), "..", "bin")
    os.makedirs(bin_dir, exist_ok=True)
    dest = os.path.join(bin_dir, asset)

    if os.path.isfile(dest):
        # Already downloaded — just ensure it's executable
        pass
    else:
        print(f"{_YELLOW}◈ Tunnel: downloading cloudflared binary from GitHub…{_RESET}")
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"{_GREEN}◈ Tunnel: downloaded to {dest}{_RESET}")
        except Exception as exc:
            print(f"{_RED}◈ Tunnel: direct download failed — {exc}{_RESET}")
            return None

    # Fix execute bit
    try:
        current = os.stat(dest).st_mode
        os.chmod(dest, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except OSError:
        pass

    return dest


def _get_binary() -> str | None:
    """
    Return a working path to the cloudflared binary.
    Strategy (in order):
      1. pycloudflared package  (auto-installs package if missing, triggers binary download)
      2. System PATH
      3. Direct GitHub download into ./bin/
    """
    import shutil
    import stat

    # ── Step 0: check pycloudflared is installed ─────────────────────────────
    if not _ensure_pycloudflared():
        return None

    candidates: list[str] = []

    # ── Step 1: ask pycloudflared for the binary ───────────────────────────────
    try:
        import pycloudflared as _pcf

        # cloudflared_path attribute (set after first download)
        path = getattr(_pcf, "cloudflared_path", None)
        if path:
            candidates.append(str(path))

        # Walk the package directory for any cloudflared file
        pkg_dir = os.path.dirname(_pcf.__file__)
        for fname in os.listdir(pkg_dir):
            full = os.path.join(pkg_dir, fname)
            if "cloudflared" in fname.lower() and os.path.isfile(full):
                candidates.append(full)

        # pycloudflared ≥ 0.2 exposes a download() helper
        if not candidates or not any(os.path.isfile(c) for c in candidates):
            download_fn = getattr(_pcf, "download", None)
            if callable(download_fn):
                print(f"{_YELLOW}◈ Tunnel: triggering pycloudflared binary download…{_RESET}")
                try:
                    downloaded = download_fn()
                    if downloaded:
                        candidates.append(str(downloaded))
                except Exception:
                    pass

    except ImportError:
        pass

    # ── Step 2: system PATH ────────────────────────────────────────────────────
    sys_path = shutil.which("cloudflared")
    if sys_path:
        candidates.append(sys_path)

    # ── Step 3: validate each candidate ───────────────────────────────────────
    for candidate in candidates:
        if not os.path.isfile(candidate):
            continue
        # Fix execute bit (common issue in Pterodactyl containers)
        try:
            current = os.stat(candidate).st_mode
            if not (current & stat.S_IXUSR):
                os.chmod(candidate, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            pass
        # Smoke-test
        try:
            result = subprocess.run(
                [candidate, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=5,
            )
            if result.returncode == 0:
                return candidate
        except (OSError, subprocess.TimeoutExpired):
            continue

    # ── Step 4: direct GitHub download (opt-in only) ─────────────────────────
    if not TUNNEL_ALLOW_BINARY_DOWNLOAD:
        print(
            f"{_YELLOW}◈ Tunnel: no working binary found.\n"
            f"  Install pycloudflared manually, or set TUNNEL_ALLOW_BINARY_DOWNLOAD=true "
            f"to allow downloading cloudflared from GitHub.{_RESET}"
        )
        return None

    print(f"{_YELLOW}◈ Tunnel: no working binary found — attempting direct download…{_RESET}")
    direct = _download_cloudflared_direct()
    if direct and os.path.isfile(direct):
        try:
            result = subprocess.run(
                [direct, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=5,
            )
            if result.returncode == 0:
                return direct
        except (OSError, subprocess.TimeoutExpired):
            pass

    return None


def _run_tunnel(binary: str, token: str, port: int, public_url: str) -> None:
    """
    Blocking loop — runs:
      cloudflared tunnel --no-autoupdate run --token <token>
    Restarts automatically if the process exits.
    """
    cmd = [
        binary,
        "tunnel",
        "--no-autoupdate",
        "--url", f"http://localhost:{port}",
        "run",
        "--token", token,
    ]

    first_run = True
    while True:
        if first_run:
            print(f"{_CYAN}◈ Tunnel: connecting to Cloudflare…{_RESET}")
            first_run = False
        else:
            print(f"{_YELLOW}◈ Tunnel: reconnecting…{_RESET}")

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            announced = False
            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue

                # Only surface important lines — suppress the noisy info spam
                low = line.lower()
                if any(k in low for k in ("error", "warn", "registered", "connected", "failed", "unable")):
                    print(f"{_CYAN}  [cloudflared] {line}{_RESET}")

                # Announce the live URL once the tunnel is up
                if not announced and ("registered tunnel connection" in low or "connection registered" in low):
                    announced = True
                    if public_url:
                        print(f"{_GREEN}◈ Tunnel: API is live at  {public_url}{_RESET}")
                        print(f"{_CYAN}  ↳ DASHBOARD_API_URL = {public_url}/api/v1{_RESET}")
                    else:
                        print(f"{_GREEN}◈ Tunnel: connected — check CF_TUNNEL_URL in .env for your public URL{_RESET}")

            proc.wait()
            code = proc.returncode

        except (FileNotFoundError, PermissionError) as exc:
            print(f"{_RED}◈ Tunnel: failed to execute binary at '{binary}' — {exc}{_RESET}")
            print(f"{_RED}  Check: file exists, has execute permission, and matches the server OS/arch.{_RESET}")
            return
        except Exception as exc:
            print(f"{_RED}◈ Tunnel: unexpected error — {exc}{_RESET}")
            code = -1

        print(f"{_YELLOW}◈ Tunnel: exited (code {code}), restarting in 5 s…{_RESET}")
        time.sleep(5)


def start_tunnel() -> None:
    """
    Start the Cloudflare Tunnel in a background daemon thread.
    Called from CodeX.py after keep_alive().
    """
    if not TUNNEL_ENABLED:
        print(f"{_YELLOW}◈ Tunnel: disabled via TUNNEL_ENABLED=false{_RESET}")
        return

    if not CF_TUNNEL_TOKEN:
        print(
            f"{_YELLOW}◈ Tunnel: CF_TUNNEL_TOKEN is not set — tunnel skipped.\n"
            f"  Get your token from https://one.dash.cloudflare.com → Networks → Tunnels{_RESET}"
        )
        return

    binary = _get_binary()
    if not binary:
        print(
            f"{_RED}◈ Tunnel: could not obtain a working cloudflared binary after all attempts.\n"
            f"  Tunnel will not start. Check your network or install manually:\n"
            f"  pip install pycloudflared{_RESET}"
        )
        return

    print(f"{_CYAN}◈ Tunnel: cloudflared binary ready — starting tunnel on port {API_PORT}…{_RESET}")
    t = threading.Thread(target=_run_tunnel, args=(binary, CF_TUNNEL_TOKEN, API_PORT, CF_TUNNEL_URL), daemon=True)
    t.start()
