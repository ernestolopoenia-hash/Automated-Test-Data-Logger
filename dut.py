"""
dut.py
======
Defines the DeviceUnderTest (DUT) class: the identity and full test history
of a single physical unit moving through the stress test station.

A DUT accumulates one or more Measurement attempts (an initial attempt, and
optionally one automatic retest) and arrives at a final TestResult and
FailureMode once StressTest has evaluated it.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from measurement import FailureMode, Measurement, TestResult


@dataclass
class DeviceUnderTest:
    """
    Represents one physical unit under test (DUT), including its
    manufacturing identity, every measurement attempt taken against it,
    and its final adjudicated result.
    """
    serial_number: str
    test_id: str
    batch_number: str
    operator: str
    timestamp: datetime = field(default_factory=datetime.now)

    attempts: List[Measurement] = field(default_factory=list)
    result: TestResult = TestResult.FAIL
    failure_reason: FailureMode = FailureMode.NONE
    failure_reasons: List[FailureMode] = field(default_factory=list)
    error_code: Optional[str] = None
    retested: bool = False

    @classmethod
    def create(cls, index: int, batch_number: str, operator: str) -> "DeviceUnderTest":
        """
        Factory that generates a realistic serial number and test ID for
        the DUT at the given position in the test run.
        """
        serial_number = f"DUT{index:04d}"
        test_id = f"TID-{uuid.uuid4().hex[:8].upper()}"
        return cls(
            serial_number=serial_number,
            test_id=test_id,
            batch_number=batch_number,
            operator=operator,
        )

    @property
    def final_measurement(self) -> Measurement:
        """The measurement attempt that determined the DUT's final result."""
        return self.attempts[-1]

    @property
    def initial_measurement(self) -> Measurement:
        """The first measurement attempt (before any retest)."""
        return self.attempts[0]

    @property
    def passed(self) -> bool:
        return self.result in (TestResult.PASS, TestResult.PASS_AFTER_RETEST)

    def add_attempt(self, measurement: Measurement) -> None:
        self.attempts.append(measurement)

    def to_row(self) -> dict:
        """Flat dictionary representation used for CSV/Excel export and tables."""
        m = self.final_measurement
        row = {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "test_id": self.test_id,
            "serial_number": self.serial_number,
            "batch": self.batch_number,
            "operator": self.operator,
            "result": self.result.value,
            "failure_reason": self.failure_reason.value if self.failure_reason != FailureMode.NONE else "",
            "retested": self.retested,
            "error_code": self.error_code or "",
        }
        row.update(m.as_dict())
        return row
