import statistics
import math


def calculate_metrics(results, total_time_seconds):

    total = len(results)

    if total == 0:
        return {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate_percent": 0.0,
            "validation_accuracy_percent": 0.0,
            "error_rate_percent": 0.0,
            "average_latency_ms": 0.0,
            "minimum_latency_ms": 0.0,
            "maximum_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "throughput_requests_per_second": 0.0
        }

    passed = sum(
        1 for result in results
        if result["passed"]
    )

    errors = sum(
        1 for result in results
        if result["error"]
    )

    latencies = sorted(
        result["latency_ms"]
        for result in results
    )

    # Calculate validation accuracy.
    total_checks = sum(
        result["validation_checks"]
        for result in results
    )

    correct_checks = sum(
        result["correct_checks"]
        for result in results
    )

    validation_accuracy = (
        correct_checks / total_checks * 100
        if total_checks > 0 else 0.0
    )

    # Calculate throughput.
    throughput = (
        total / total_time_seconds
        if total_time_seconds > 0 else 0.0
    )

    # Calculate nearest-rank percentiles.
    def percentile(values, percentage):
        rank = math.ceil(
            percentage / 100 * len(values)
        )
        return values[max(0, rank - 1)]

    return {
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": total - passed,

        "success_rate_percent": round(
            passed / total * 100, 2
        ),

        "validation_accuracy_percent": round(
            validation_accuracy, 2
        ),

        "correct_validation_checks": correct_checks,
        "total_validation_checks": total_checks,

        "error_rate_percent": round(
            errors / total * 100, 2
        ),

        "average_latency_ms": round(
            statistics.mean(latencies), 4
        ),

        "minimum_latency_ms": round(
            min(latencies), 4
        ),

        "maximum_latency_ms": round(
            max(latencies), 4
        ),

        "p50_latency_ms": round(
            percentile(latencies, 50), 4
        ),

        "p95_latency_ms": round(
            percentile(latencies, 95), 4
        ),

        "total_execution_time_seconds": round(
            total_time_seconds, 6
        ),

        "throughput_requests_per_second": round(
            throughput, 2
        )
    }