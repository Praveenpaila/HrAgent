import csv
import json
import time
import logging

from pathlib import Path
from datetime import datetime, timezone
from contextlib import redirect_stdout
from io import StringIO

from agents.hr_manager_agent import hr_manager_agent
from evaluation.benchmark_dataset import create_benchmark_dataset
from evaluation.metrics import calculate_metrics


BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def evaluate_validation(report, case):

    checks = []

    # Check each required employee field.
    required_fields = [
        "name",
        "employee_id",
        "department",
        "role"
    ]

    expected_missing_fields = [
        field for field in required_fields
        if not case["employee"].get(field, "").strip()
    ]

    actual_missing_fields = report["information"]["missing_fields"]

    for field in required_fields:
        checks.append(
            (field in expected_missing_fields)
            ==
            (field in actual_missing_fields)
        )

    # Check each required document.
    required_documents = [
        "identity_document",
        "educational_certificate",
        "signed_offer_letter"
    ]

    expected_missing_documents = [
        document for document in required_documents
        if not case["documents"].get(document, False)
    ]

    actual_missing_documents = report["documents"]["missing_documents"]

    for document in required_documents:
        checks.append(
            (document in expected_missing_documents)
            ==
            (document in actual_missing_documents)
        )

    # Check expected overall onboarding status.
    checks.append(
        report["overall_status"] == case["expected_status"]
    )

    correct_checks = sum(checks)

    return correct_checks, len(checks)


def run_benchmark():

    cases = create_benchmark_dataset()
    results = []

    print("\nStarting HR Onboarding Benchmark...")
    print("-" * 50)

    benchmark_start = time.perf_counter()

    for case in cases:

        case_start = time.perf_counter()

        try:
            # Suppress individual agent console output.
            with redirect_stdout(StringIO()):
                report = hr_manager_agent(
                    case["employee"],
                    case["documents"]
                )

            latency_ms = (
                time.perf_counter() - case_start
            ) * 1000

            actual_status = report["overall_status"]

            passed = (
                actual_status == case["expected_status"]
            )

            correct_checks, total_checks = evaluate_validation(
                report, case
            )

            result = {
                "test_id": case["id"],
                "description": case["description"],
                "expected_status": case["expected_status"],
                "actual_status": actual_status,
                "passed": passed,
                "latency_ms": latency_ms,
                "error": "",
                "validation_checks": total_checks,
                "correct_checks": correct_checks,
                "agent_timings_ms": report.get(
                    "agent_timings_ms", {}
                )
            }

            logging.info(
                "%s | %s | %.4f ms",
                case["id"],
                "PASS" if passed else "FAIL",
                latency_ms
            )

        except Exception as exc:

            latency_ms = (
                time.perf_counter() - case_start
            ) * 1000

            result = {
                "test_id": case["id"],
                "description": case["description"],
                "expected_status": case["expected_status"],
                "actual_status": "EXECUTION ERROR",
                "passed": False,
                "latency_ms": latency_ms,
                "error": str(exc),
                "validation_checks": 0,
                "correct_checks": 0,
                "agent_timings_ms": {}
            }

            logging.error(
                "%s | EXECUTION ERROR | %s",
                case["id"],
                exc
            )

        results.append(result)

    total_time_seconds = (
        time.perf_counter() - benchmark_start
    )

    metrics = calculate_metrics(
        results,
        total_time_seconds
    )

    # Aggregate agent-level timings.
    agent_totals = {}

    for result in results:
        for agent, duration in result["agent_timings_ms"].items():
            agent_totals.setdefault(agent, []).append(duration)

    agent_average_timings = {
        agent: round(sum(times) / len(times), 4)
        for agent, times in agent_totals.items()
        if times
    }

    # Cost accounting.
    cost_report = {
        "external_api_cost_usd": 0.0,
        "llm_token_cost_usd": 0.0,
        "api_calls": 0,
        "local_compute_cost_usd": None
    }

    # Generate CSV report.
    csv_path = REPORT_DIR / "benchmark_results.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "test_id",
                "description",
                "expected_status",
                "actual_status",
                "passed",
                "latency_ms",
                "error"
            ]
        )

        writer.writeheader()

        for result in results:
            writer.writerow({
                "test_id": result["test_id"],
                "description": result["description"],
                "expected_status": result["expected_status"],
                "actual_status": result["actual_status"],
                "passed": result["passed"],
                "latency_ms": round(result["latency_ms"], 4),
                "error": result["error"]
            })

    # Generate JSON summary.
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark_version": "1.0",
        "metrics": metrics,
        "average_agent_latency_ms": agent_average_timings,
        "cost": cost_report,
        "individual_results": [
            {
                **result,
                "latency_ms": round(result["latency_ms"], 4)
            }
            for result in results
        ]
    }

    json_path = REPORT_DIR / "evaluation_summary.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    # Display final report.
    print("\n")
    print("=" * 55)
    print("       HR ONBOARDING EVALUATION REPORT")
    print("=" * 55)

    print("Total Tests:", metrics["total_tests"])
    print("Passed Tests:", metrics["passed_tests"])
    print("Failed Tests:", metrics["failed_tests"])

    print(
        "Task Success Rate:",
        f'{metrics["success_rate_percent"]}%'
    )

    print(
        "Validation Accuracy:",
        f'{metrics["validation_accuracy_percent"]}%'
    )

    print(
        "Correct Validation Checks:",
        f'{metrics.get("correct_validation_checks", 0)}/'
        f'{metrics.get("total_validation_checks", 0)}'
    )

    print(
        "Execution Error Rate:",
        f'{metrics["error_rate_percent"]}%'
    )

    print("\nLATENCY")
    print("Average:", metrics["average_latency_ms"], "ms")
    print("Minimum:", metrics["minimum_latency_ms"], "ms")
    print("Maximum:", metrics["maximum_latency_ms"], "ms")
    print("P50:", metrics["p50_latency_ms"], "ms")
    print("P95:", metrics["p95_latency_ms"], "ms")

    print("\nTHROUGHPUT")
    print(
        "Requests/Second:",
        metrics["throughput_requests_per_second"]
    )

    print("\nAVERAGE AGENT LATENCY")

    for agent, duration in agent_average_timings.items():
        print(f"{agent}: {duration} ms")

    print("\nCOST")
    print("External API Cost: $0.00")
    print("LLM Token Cost: $0.00")
    print("API Calls: 0")
    print("Local Compute Cost: Not configured")

    print("\nREPORT FILES")
    print("CSV:", csv_path)
    print("JSON:", json_path)

    print("=" * 55)

    return summary


if __name__ == "__main__":
    run_benchmark()