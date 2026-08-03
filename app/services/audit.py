import json
from pathlib import Path
from threading import Lock
from typing import Any

from app.models import StatsResponse


_lock = Lock()


def write_event(file_path: str, event: dict[str, Any]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with _lock:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_events(file_path: str) -> list[dict[str, Any]]:
    path = Path(file_path)

    if not path.exists():
        return []

    events: list[dict[str, Any]] = []

    with _lock:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return events


def summarize_events(events: list[dict[str, Any]]) -> StatsResponse:
    total = len(events)
    average_latency = (
        sum(float(event.get("latency_ms", 0)) for event in events) / total
        if total
        else 0.0
    )

    return StatsResponse(
        total_requests=total,
        allowed=sum(event.get("status") == "allowed" for event in events),
        blocked=sum(event.get("status") == "blocked" for event in events),
        rewritten=sum(event.get("status") == "rewritten" for event in events),
        pii_events=sum(bool(event.get("pii_detected")) for event in events),
        injection_events=sum(
            bool(event.get("injection_detected")) for event in events
        ),
        secret_events=sum(bool(event.get("secret_detected")) for event in events),
        average_latency_ms=round(average_latency, 2),
    )
