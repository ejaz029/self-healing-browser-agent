
import json
from datetime import datetime, timezone
from pathlib import Path


class ExecutionTrace:
    def __init__(self):
        self.events = []

    def record(
        self,
        action: str,
        strategy: str,
        result: str,
        verification: str = "not_checked",
        reason: str | None = None,
    ):
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "strategy": strategy,
            "result": result,
            "verification": verification,
            "reason": reason,
        }

        self.events.append(event)

    def get_report(self) -> dict:
        return {
            "total_events": len(self.events),
            "events": self.events,
        }

    
    
    def export_json(
        self,
        directory: str = "reports",
        metadata: dict | None = None,
    ):
        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
         )

        report_dir = Path(directory)
        report_dir.mkdir(parents=True, exist_ok=True)

        path = report_dir / f"execution_{timestamp}.json"

        report = self.get_report()
        if metadata:
            report.update(metadata)

        with path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)

        return path

