"""
measurement.py
==============
Data model for a single electrical measurement taken during a stress test,
plus the enumerations used to classify test outcomes and failure modes.

Kept separate from dut.py so that "what was measured" (this module) is
decoupled from "who/what was tested" (dut.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TestResult(str, Enum):
    """Overall disposition of a DUT after one full test sequence."""
    PASS = "PASS"
    PASS_AFTER_RETEST = "PASS AFTER RETEST"
    FAIL = "FAIL"


class FailureMode(str, Enum):
    """Enumerated, engineering-meaningful failure classifications."""
    NONE = "None"
    VOLTAGE_TOO_HIGH = "Voltage Too High"
    VOLTAGE_TOO_LOW = "Voltage Too Low"
    OVER_TEMPERATURE = "Over Temperature"
    HIGH_LEAKAGE = "High Leakage Current"
    HIGH_RIPPLE = "High Voltage Ripple"
    EXCESS_SPIKES = "Excessive Voltage Spikes"
    CURRENT_OUT_OF_SPEC = "Current Out of Specification"
    HUMIDITY_OUT_OF_SPEC = "Humidity Out of Specification"
    POWER_FAILURE = "Power Supply Instability"
    CALIBRATION_ERROR = "Calibration Error"
    SENSOR_FAULT = "Sensor Fault"
    INTERMITTENT_FAILURE = "Intermittent Failure"
    MULTIPLE_FAILURES = "Multiple Failures"


@dataclass
class Measurement:
    """
    A single set of electrical/environmental readings captured for one
    test attempt (initial attempt or retest) on a DUT.
    """
    measured_voltage_v: float
    current_a: float
    temperature_c: float
    humidity_pct: float
    leakage_current_ma: float
    voltage_ripple_mv: float
    voltage_spikes: int
    calibration_offset_v: float
    sensor_noise_v: float
    environmental_temp_c: float
    test_duration_s: float

    @property
    def power_w(self) -> float:
        """Instantaneous power delivered to the DUT (P = V * I)."""
        return round(self.measured_voltage_v * self.current_a, 4)

    def as_dict(self) -> dict:
        """Flat dictionary representation, convenient for CSV/Excel export."""
        return {
            "measured_voltage_v": self.measured_voltage_v,
            "current_a": self.current_a,
            "power_w": self.power_w,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "leakage_current_ma": self.leakage_current_ma,
            "voltage_ripple_mv": self.voltage_ripple_mv,
            "voltage_spikes": self.voltage_spikes,
            "calibration_offset_v": self.calibration_offset_v,
            "sensor_noise_v": self.sensor_noise_v,
            "environmental_temp_c": self.environmental_temp_c,
            "test_duration_s": self.test_duration_s,
        }
