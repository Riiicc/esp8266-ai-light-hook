import json
from pathlib import Path


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    hook_path = Path(".codex/hooks.json")
    hooks = json.loads(hook_path.read_text(encoding="utf-8"))["hooks"]

    expect("SessionStart" in hooks, "Codex hooks must define SessionStart")
    expect("UserPromptSubmit" in hooks, "Codex hooks must define UserPromptSubmit")
    expect("PermissionRequest" in hooks, "Codex hooks must define PermissionRequest")
    expect("Stop" in hooks, "Codex hooks must define Stop")
    expect("Notification" not in hooks, "Codex hooks must not depend on Notification")

    session_start = hooks["SessionStart"][0]
    expect(
        session_start.get("matcher") == "startup|resume|clear|compact",
        "SessionStart matcher must cover startup, resume, clear, and compact",
    )
    expect(
        session_start["hooks"][0]["command"].endswith("send-light.ps1 E"),
        "SessionStart must send E",
    )
    expect(
        hooks["UserPromptSubmit"][0]["hooks"][0]["command"].endswith("send-light.ps1 Q"),
        "UserPromptSubmit must send Q",
    )
    permission_request = hooks["PermissionRequest"][0]
    expect(
        permission_request.get("matcher") == ".*",
        "PermissionRequest matcher must match every approval request",
    )
    expect(
        permission_request["hooks"][0]["command"].endswith("send-light.ps1 G"),
        "PermissionRequest must send G",
    )
    expect(
        hooks["Stop"][0]["hooks"][0]["command"].endswith("send-light.ps1 A"),
        "Stop must send A",
    )

    print("PASS")


if __name__ == "__main__":
    main()
