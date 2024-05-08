import asyncio
import socket
import urllib.parse


def build_url(ip_addr, port):
    parsed_ip = urllib.parse.urlparse(ip_addr)
    scheme = parsed_ip.scheme if parsed_ip.scheme else "http"
    netloc = parsed_ip.netloc if parsed_ip.netloc else ip_addr
    return f"{scheme}://{netloc}:{port}"


async def is_live(host: str, port: int = 80, timeout=2):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    try:
        await asyncio.wait_for(
            asyncio.get_event_loop().sock_connect(sock, (host, port)), timeout
        )
    except asyncio.TimeoutError:
        return False
    except Exception:
        return False
    else:
        sock.close()
        return True
