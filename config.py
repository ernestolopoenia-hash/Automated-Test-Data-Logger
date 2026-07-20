"""
config.py
=========
Central configuration for the Electronics Reliability Stress Test Simulator.

Every engineering limit, environmental bound, and simulation parameter lives
here. Changing a value in this file automatically changes the pass/fail
behavior of the whole application -- no other module hard-codes a limit.

This module intentionally uses simple dataclasses (rather than a JSON file)
so that limits are type-checked and easy to import, while still being the
single source of truth an engineer would edit before a test run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class VoltageLimits:
    """Engineering limits for the voltage stress test."""
    nominal_v: float = 12.0
    pass_min_v: float = 11.80
    pass_max_v: float = 12.20
    ripple_max_mv: float = 150.0
    max_spikes: int = 2


@dataclass(frozen=True)
class CurrentLimits:
    """Engineering limits for supply current."""
    nominal_a: float = 1.20
    tolerance_pct: float = 10.0

    @property
    def min_a(self) -> float:
        return self.nominal_a * (1 - self.tolerance_pct / 100)

    @property
    def max_a(self) -> float:
        return self.nominal_a * (1 + self.tolerance_pct / 100)


@dataclass(frozen=True)
class ThermalLimits:
    """Temperature-related engineering limits."""
    max_temp_c: float = 70.0
    ambient_nominal_c: float = 25.0
    ambient_drift_c: float = 3.0


@dataclass(frozen=True)
class EnvironmentalLimits:
    """Environmental (humidity) engineering limits."""
    humidity_min_pct: float = 20.0
    humidity_max_pct: float = 80.0


@dataclass(frozen=True)
class LeakageLimits:
    """Leakage current engineering limits."""
    max_leakage_ma: float = 3.0


@dataclass(frozen=True)
class SimulationParameters:
    """Tunable parameters that control the realism of generated data."""
    voltage_noise_std_v: float = 0.06
    current_noise_std_a: float = 0.02
    calibration_offset_std_v: float = 0.015
    sensor_noise_std_v: float = 0.01
    temp_drift_std_c: float = 6.0
    humidity_mean_pct: float = 45.0
    humidity_std_pct: float = 12.0
    ripple_mean_mv: float = 55.0
    ripple_std_mv: float = 30.0
    spike_poisson_lambda: float = 0.6
    leakage_mean_ma: float = 1.1
    leakage_std_ma: float = 0.6
    intermittent_failure_rate: float = 0.04
    power_instability_rate: float = 0.03
    test_duration_mean_s: float = 45.0
    test_duration_std_s: float = 8.0
    retest_improvement_factor: float = 0.5
    """Fraction by which out-of-spec deltas shrink on an automatic retest."""


@dataclass(frozen=True)
class CompanyInfo:
    """Report branding / identification info."""
    company_name: str = "Meridian Semiconductor Labs"
    lab_name: str = "Reliability & DVT Engineering Lab"
    default_operator: str = "J. Alvarez"
    report_title: str = "Voltage Stress Qualification Test Report"


@dataclass(frozen=True)
class AppConfig:
    """Top level configuration bundle passed around the application."""
    voltage: VoltageLimits = field(default_factory=VoltageLimits)
    current: CurrentLimits = field(default_factory=CurrentLimits)
    thermal: ThermalLimits = field(default_factory=ThermalLimits)
    environment: EnvironmentalLimits = field(default_factory=EnvironmentalLimits)
    leakage: LeakageLimits = field(default_factory=LeakageLimits)
    simulation: SimulationParameters = field(default_factory=SimulationParameters)
    company: CompanyInfo = field(default_factory=CompanyInfo)

    output_dir: str = "reports"
    plots_subdir: str = "plots"
    csv_filename: str = "stress_test_results.csv"
    xlsx_filename: str = "stress_test_results.xlsx"
    json_filename: str = "summary.json"
    pdf_filename: str = "Stress_Test_Report.pdf"
    log_filename: str = "stress_test.log"

    random_seed: int | None = None
    """Set to an int for fully reproducible simulation runs."""


CONFIG = AppConfig()
