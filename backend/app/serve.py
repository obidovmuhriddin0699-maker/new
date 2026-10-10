"""Production HTTP server: uvicorn on one dual-stack (IPv6 + IPv4) socket.

``uvicorn --host ::`` gives an IPv6-only socket (asyncio sets IPV6_V6ONLY), and
``--host 0.0.0.0`` is IPv4-only. Docker networks reach the API over IPv4, while
platforms with an IPv6 private network (Railway's ``*.railway.internal``) reach it over
IPv6. This launcher binds ``[::]:PORT`` with IPV6_V6ONLY off, so both work, and falls back
to ``0.0.0.0`` when the kernel has no IPv6.

    python -m app.serve            # PORT (default 8000), WEB_CONCURRENCY (default 2)

Proxy headers stay off: the app resolves client IPs itself from TRUSTED_PROXIES.
"""

import logging
import os
import socket

import uvicorn
from uvicorn.supervisors import Multiprocess

logger = logging.getLogger("app.serve")


def dual_stack_socket(port: int) -> socket.socket:
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("::", port))
    except OSError as exc:  # no IPv6 in this kernel/container
        logger.warning("ipv6_unavailable_binding_ipv4", extra={"error": str(exc)})
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", port))  # noqa: S104 - a server must listen on all interfaces
    sock.set_inheritable(True)
    return sock


def main() -> None:
    port = int(os.environ.get("PORT") or 8000)
    workers = max(1, int(os.environ.get("WEB_CONCURRENCY") or 2))
    config = uvicorn.Config(
        "app.main:app",
        port=port,
        workers=workers,
        proxy_headers=False,
        server_header=False,
    )
    sock = dual_stack_socket(port)
    server = uvicorn.Server(config)
    if workers > 1:
        Multiprocess(config, sockets=[sock]).run()
    else:
        server.run(sockets=[sock])


if __name__ == "__main__":
    main()
