import http.client
import json
import time
from typing import Any


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def send_http_request(host: str, port: int, method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, str, dict[str, Any]]:
    conn = http.client.HTTPConnection(host, port, timeout=30)
    try:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json; charset=utf-8"}
        conn.request(method, path, payload, headers)
        response = conn.getresponse()
        raw = response.read().decode("utf-8", "replace")
    except OSError as exc:
        return 0, type(exc).__name__, {
            "error": f"Could not connect to http://{host}:{port}{path}",
            "detail": str(exc),
        }
    finally:
        conn.close()

    if not raw.strip():
        return response.status, response.reason, {}
    try:
        return response.status, response.reason, json.loads(raw)
    except json.JSONDecodeError:
        return response.status, response.reason, {"raw": raw}


def print_response(title: str, status: int, reason: str, data: dict[str, Any]) -> None:
    print(f"\n=== {title} ===")
    print(f"status: {status} {reason}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main() -> int:
    host = DEFAULT_HOST
    port = DEFAULT_PORT

    print(f"Testing tarot API at http://{host}:{port}")

    status, reason, data = send_http_request(host, port, "GET", "/health")
    print(f"[health] {status} {reason}: {data}")
    if status != 200:
        print("health check failed")
        return 1
    
    status, reason, data = send_http_request(host, port, "GET", "/spreads")
    print(f"[spreads] {status} {reason}: {data}")
    if status != 200:
        print("list spreads failed")
        return 1

    status, reason, data = send_http_request(host, port, "POST", "/cleanup")
    print(f"[cleanup] {status} {reason}: {data}")
    if status != 200:
        print("cleanup failed")
        return 1
    
    draw_body = {
        "id": f"manual-test-{int(time.time())}",
        "name": "three_card_spread",
        "arcana": "full",
        "orientation": "random",
        "locale": "en"
    }
    status, reason, data = send_http_request(host, port, "POST", "/draw", draw_body)
    print(f"[draw] {status} {reason}: {data}")
    if status != 200:
        print("draw failed")
        return 1
    # with open("sample_draw_response.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False, indent=2)
    
    status, reason, data = send_http_request(host, port, "GET", "/ids")
    print(f"[ids] {status} {reason}: {data}")
    if status != 200:
        print("list ids failed")
        return 1

    status, reason, data = send_http_request(host, port, "POST", "/cleanup")
    print(f"[cleanup] {status} {reason}: {data}")
    if status != 200:
        print("cleanup failed")
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())