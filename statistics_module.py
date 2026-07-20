"""
statistics_module.py
=====================
Aggregate statistics computation over a completed batch of DUTs.

Named `statistics_module` (rather than `statistics`) so it does not shadow
Python's standard-library `statistics` module on the import path.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from dut import DeviceUnderTest
from measurement import FailureMode, TestResult


@dataclass
class RunStatistics:
    """Computed summary statistics for one complete stress test run."""

    units_tested: int = 0
    units_passed: int = 0
    units_passed_after_retest: int = 0
    units_failed: int = 0

    pass_rate_pct: float = 0.0
    fail_rate_pct: float = 0.0

    avg_voltage_v: float = 0.0
    avg_current_a: float = 0.0
    avg_temperature_c: float = 0.0
    avg_leakage_ma: float = 0.0

    max_temperature_c: float = 0.0
    min_voltage_v: float = 0.0
    max_voltage_v: float = 0.0

    total_test_time_s: float = 0.0
    average_test_time_s: float = 0.0

    failure_mode_counts: Dict[str, int] = field(default_factory=dict)
    most_common_failure_mode: str = "None"

    @classmethod
    def from_duts(cls, duts: List[DeviceUnderTest]) -> "RunStatistics":
        """Computes a RunStatistics snapshot from a list of tested DUTs."""
        stats = cls()
        n = len(duts)
        stats.units_tested = n
        if n == 0:
            return stats

        stats.units_passed = sum(1 for d in duts if d.result == TestResult.PASS)
        stats.units_passed_after_retest = sum(
            1 for d in duts if d.result == TestResult.PASS_AFTER_RETEST
        )
        stats.units_failed = sum(1 for d in duts if d.result == TestResult.FAIL)

        passed_total = stats.units_passed + stats.units_passed_after_retest
        stats.pass_rate_pct = round(100 * passed_total / n, 2)
        stats.fail_rate_pct = round(100 * stats.units_failed / n, 2)

        voltages = [d.final_measurement.measured_voltage_v for d in duts]
        currents = [d.final_measurement.current_a for d in duts]
        temps = [d.final_measurement.temperature_c for d in duts]
        leakages = [d.final_measurement.leakage_current_ma for d in duts]
        durations = [sum(m.test_duration_s for m in d.attempts) for d in duts]

        stats.avg_voltage_v = round(sum(voltages) / n, 4)
        stats.avg_current_a = round(sum(currents) / n, 4)
        stats.avg_temperature_c = round(sum(temps) / n, 2)
        stats.avg_leakage_ma = round(sum(leakages) / n, 3)

        stats.max_temperature_c = round(max(temps), 2)
        stats.min_voltage_v = round(min(voltages), 4)
        stats.max_voltage_v = round(max(voltages), 4)

        stats.total_test_time_s = round(sum(durations), 2)
        stats.average_test_time_s = round(stats.total_test_time_s / n, 2)

        failure_counter: Counter = Counter()
        for d in duts:
            if d.result == TestResult.FAIL:
                for mode in (d.failure_reasons or [d.failure_reason]):
                    if mode != FailureMode.NONE:
                        failure_counter[mode.value] += 1

        stats.failure_mode_counts = dict(failure_counter)
        if failure_counter:
            stats.most_common_failure_mode = failure_counter.most_common(1)[0][0]
        else:
            stats.most_common_failure_mode = "None"

        return stats

    def as_dict(self) -> dict:
        return {
            "units_tested": self.units_tested,
            "units_passed": self.units_passed,
            "units_passed_after_retest": self.units_passed_after_retest,
            "units_failed": self.units_failed,
            "pass_rate_pct": self.pass_rate_pct,
            "fail_rate_pct": self.fail_rate_pct,
            "avg_voltage_v": self.avg_voltage_v,
            "avg_current_a": self.avg_current_a,
            "avg_temperature_c": self.avg_temperature_c,
            "avg_leakage_ma": self.avg_leakage_ma,
            "max_temperature_c": self.max_temperature_c,
            "min_voltage_v": self.min_voltage_v,
            "max_voltage_v": self.max_voltage_v,
            "total_test_time_s": self.total_test_time_s,
            "average_test_time_s": self.average_test_time_s,
            "failure_mode_counts": self.failure_mode_counts,
            "most_common_failure_mode": self.most_common_failure_mode,
        }
