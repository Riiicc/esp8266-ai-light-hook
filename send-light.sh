#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 3 ]]; then
  echo "Usage: $0 <A|B|C|D|E|F|G|H|I|J|L|N|Q|R|T|U|V|W> [host] [port]" >&2
  exit 2
fi

state="$1"
host="${2:-192.168.1.88}"
port="${3:-8899}"

case "$state" in
  A|B|C|D|E|F|G|H|I|J|L|N|Q|R|T|U|V|W)
    ;;
  *)
    echo "Invalid state: $state" >&2
    exit 2
    ;;
esac

python3 - "$state" "$host" "$port" <<'PY'
import socket
import sys
import time

state = sys.argv[1].encode("ascii")
host = sys.argv[2]
port = int(sys.argv[3])
retries = 3
connect_timeout_s = 1.0
ack_timeout_s = 1.0

last_error = None

for attempt in range(retries):
    try:
        with socket.create_connection((host, port), timeout=connect_timeout_s) as sock:
            sock.settimeout(ack_timeout_s)
            sock.sendall(state)
            ack = sock.recv(16)
            if ack == b"OK\n":
                raise SystemExit(0)
            last_error = RuntimeError(f"unexpected ack: {ack!r}")
    except OSError as exc:
        last_error = exc

    if attempt + 1 < retries:
        time.sleep(0.1)

raise SystemExit(f"send-light failed after {retries} attempts: {last_error}")
PY
