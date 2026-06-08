from pathlib import Path


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    script = Path("send-light.sh").read_text(encoding="utf-8")
    expect("retries = 3" in script, "Bash sender should retry three times")
    expect("ack = sock.recv(16)" in script, "Bash sender should read an ack from the socket")
    expect('if ack == b"OK\\n":' in script, "Bash sender should require an OK ack")
    expect("time.sleep(0.1)" in script, "Bash sender should sleep briefly between retries")
    print("PASS")


if __name__ == "__main__":
    main()
