"""SSRF guard for outbound fetches triggered by user-supplied URLs.

Usage:
    from utils.safehttp import assert_safe_fetch_url
    assert_safe_fetch_url(url)            # raises ValueError on internal targets
    # ...then perform the fetch...

Resolves the hostname and rejects loopback / private / link-local / reserved /
multicast / unspecified addresses, plus common cloud-metadata hosts. This
mitigates the common SSRF targets (e.g. AWS metadata at 169.254.169.254,
internal RFC1918 services).

Caveat: a DNS-rebinding attacker could race the check vs. the fetch. Full
protection requires fetching through a custom resolver that pins the resolved
IP; this guard is the strong baseline mitigation.
"""

import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_HOSTS = {"localhost", "metadata.google.internal", "metadata.aws.internal"}


def assert_safe_fetch_url(url: str, allow_hosts: set[str] | None = None) -> str:
    """Validate that `url` points at a public target. Raises ValueError if not.

    If `allow_hosts` is provided, the host MUST be in that set (and is then
    trusted without IP resolution) — use for known-safe domains like
    {"discord.com", "cdn.discordapp.com"}.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Blocked URL: scheme {parsed.scheme!r} not allowed")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("Blocked URL: missing hostname")

    if allow_hosts is not None:
        if host in allow_hosts:
            return url
        raise ValueError(f"Blocked URL: host {host!r} not in allow-list")

    if host in _BLOCKED_HOSTS:
        raise ValueError(f"Blocked URL: host {host!r} is blocked")

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        raise ValueError(f"Blocked URL: cannot resolve {host!r}")

    for info in infos:
        ip = info[4][0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        ):
            raise ValueError(
                f"Blocked URL: {host!r} resolves to non-public IP {ip}"
            )
    return url
