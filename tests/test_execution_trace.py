
import json

from execution_trace import ExecutionTrace


def test_execution_trace_exports_json(tmp_path):
    trace = ExecutionTrace()

    trace.record(
        action="Confirm Order",
        strategy="original_selector",
        result="executed",
        verification="passed",
    )

    saved_path = trace.export_json(str(tmp_path))

    assert saved_path.exists()
    assert saved_path.suffix == ".json"

    with saved_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert report["total_events"] == 1
    assert report["events"][0]["action"] == "Confirm Order"
    assert report["events"][0]["result"] == "executed"
    assert report["events"][0]["verification"] == "passed"
