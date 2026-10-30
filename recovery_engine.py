
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from execution_trace import ExecutionTrace


def build_result(trace, **result):
    report = trace.get_report()

    metadata = {
        "workflow_outcome": (
            "success" if result["success"] else "failed"
        ),
        "scenario": result.pop("scenario", "unknown"),
    }

    trace.export_json("reports", metadata=metadata)

    result["attempts"] = report["events"]
    result["trace"] = report

    return result


def recover_and_confirm(page: Page) -> dict:
    trace = ExecutionTrace()

    # Strategy 1: Original selector
    try:
        page.locator("#confirm-order").click(timeout=1200)

    except PlaywrightTimeoutError:
        trace.record(
            "Confirm Order",
            "original_selector",
            "timed_out",
            reason="Original selector was not clickable",
        )

    else:
        status = page.locator("#status").inner_text()
        success = status == "Order status: Confirmed"

        trace.record(
            "Confirm Order",
            "original_selector",
            "executed",
            "passed" if success else "failed",
            None if success else "Expected status was not reached",
        )

        return build_result(
            trace,
            success=success,
            reason=None if success else "Click executed but outcome was not verified",
            verified_status=status,
            successful_strategy="original_selector" if success else None,
            scenario=(
                "normal_execution" if success
                else "verification_failure"
            ),
        )

    # Strategy 2: Find the button using its accessible name.
    button_locator = page.get_by_role(
        "button",
        name="Confirm Order",
        exact=True
    )

    # Wait for asynchronously loaded buttons.
    try:
        button_locator.first.wait_for(
            state="visible",
            timeout=3000
        )
    except PlaywrightTimeoutError:
        pass

    matching_buttons = button_locator.all()

    if len(matching_buttons) == 0:
        status = page.locator("#status").inner_text()

        trace.record(
            "Confirm Order",
            "inspect_and_match_button",
            "not_found",
            reason="No matching button found within the waiting window",
        )

        return build_result(
            trace,
            success=False,
            reason="No matching button found",
            verified_status=status,
            successful_strategy=None,
            scenario="missing_element",
        )

    if len(matching_buttons) > 1:
        status = page.locator("#status").inner_text()

        trace.record(
            "Confirm Order",
            "inspect_and_match_button",
            "ambiguous",
            reason="Multiple matching buttons found",
        )

        return build_result(
            trace,
            success=False,
            reason="Multiple matching buttons; refusing to guess",
            verified_status=status,
            successful_strategy=None,
            scenario="ambiguous_target",
        )

    # Strategy 3: Execute the recovery action once.
    try:
        matching_buttons[0].click(timeout=2000)

    except PlaywrightTimeoutError:
        status = page.locator("#status").inner_text()

        trace.record(
            "Confirm Order",
            "inspect_and_match_button",
            "timed_out",
            reason="Matching button could not be clicked",
        )

        return build_result(
            trace,
            success=False,
            reason="Matching button could not be clicked",
            verified_status=status,
            successful_strategy=None,
            scenario="recovery_execution_failure",
        )

    # Verify the actual outcome.
    status = page.locator("#status").inner_text()
    success = status == "Order status: Confirmed"

    trace.record(
        "Confirm Order",
        "inspect_and_match_button",
        "executed",
        "passed" if success else "failed",
        None if success else "Expected status was not reached",
    )

    return build_result(
        trace,
        success=success,
        reason=None if success else "Expected outcome was not verified",
        verified_status=status,
        successful_strategy=(
            "inspect_and_match_button" if success else None
        ),
        scenario=(
            "selector_recovery" if success
            else "verification_failure"
        ),
    )
