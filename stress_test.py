"""
stress_test.py
==============
Core simulation and evaluation engine for the Voltage Stress Qualification
Test. This module is intentionally designed so that additional stress test
profiles (Temperature Cycling, Thermal Shock, Power Cycling, Humidity,
ESD, HALT, Vibration, Mechanical Shock, Battery Cycling, ...) can be added
later as sibling subclasses of the abstract StressTestBase class without
touching DUT, reporting, or plotting code.
"""

from __future__ import annotations

import logging
import random
from abc import ABC, abstractmethod
from typing import List, Tuple

from config import AppConfig
from dut import DeviceUnderTest
from measurement import FailureMode, Measurement, TestResult

logger = logging.getLogger("stress_test_simulator")


class StressTestBase(ABC):
    """
    Abstract base class for a stress test profile. Concrete subclasses
    implement `generate_measurement` (how raw readings are simulated) and
    `evaluate` (how those readings map to PASS/FAIL + failure mode).

    This is the extension point for future profiles such as Temperature
    Cycling, Thermal Shock, Power Cycling, Humidity Testing, ESD, HALT,
    Vibration, Mechanical Shock, and Battery Cycling.
    """

    name: str = "Generic Stress Test"

    def __init__(self, config: AppConfig):
        self.config = config

    @abstractmethod
    def generate_measurement(self, retest: bool = False,
                              prior: Measurement | None = None) -> Measurement:
        """Simulate one set of readings for a single test attempt."""
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, measurement: Measurement) -> Tuple[bool, List[FailureMode]]:
        """Return (passed, list_of_failure_modes) for a measurement."""
        raise NotImplementedError

    def run(self, dut: DeviceUnderTest) -> DeviceUnderTest:
        """
        Executes the full test sequence -- including the mandatory single
        automatic retest on failure -- and stamps the DUT with its final
        result and failure reason.
        """
        measurement = self.generate_measurement()
        dut.add_attempt(measurement)
        passed, failures = self.evaluate(measurement)

        logger.info(
            "DUT %s attempt 1: V=%.3fV I=%.3fA T=%.1fC Leak=%.3fmA -> %s",
            dut.serial_number, measurement.measured_voltage_v,
            measurement.current_a, measurement.temperature_c,
            measurement.leakage_current_ma, "PASS" if passed else "FAIL",
        )

        if passed:
            dut.result = TestResult.PASS
            dut.failure_reason = FailureMode.NONE
            dut.failure_reasons = []
            return dut

        # Automatic single retest on failure.
        dut.retested = True
        retest_measurement = self.generate_measurement(retest=True, prior=measurement)
        dut.add_attempt(retest_measurement)
        retest_passed, retest_failures = self.evaluate(retest_measurement)

        logger.info(
            "DUT %s RETEST: V=%.3fV I=%.3fA T=%.1fC Leak=%.3fmA -> %s",
            dut.serial_number, retest_measurement.measured_voltage_v,
            retest_measurement.current_a, retest_measurement.temperature_c,
            retest_measurement.leakage_current_ma,
            "PASS" if retest_passed else "FAIL",
        )

        if retest_passed:
            dut.result = TestResult.PASS_AFTER_RETEST
            dut.failure_reason = FailureMode.NONE
            dut.failure_reasons = []
        else:
            dut.result = TestResult.FAIL
            dut.failure_reasons = retest_failures
            dut.failure_reason = (
                FailureMode.MULTIPLE_FAILURES if len(retest_failures) > 1
                else retest_failures[0]
            )

        return dut


class VoltageStressTest(StressTestBase):
    """
    Concrete stress test profile: DC Voltage Stress Qualification.

    Simulates supply voltage, current, temperature, humidity, leakage
    current, ripple, and voltage spikes for a DUT held at nominal 12V,
    then evaluates the readings against the engineering limits defined
    in config.py.
    """

    name = "Voltage Stress Qualification Test"

    def generate_measurement(self, retest: bool = False,
                              prior: Measurement | None = None) -> Measurement:
        sim = self.config.simulation
        v_limits = self.config.voltage
        c_limits = self.config.current
        t_limits = self.config.thermal

        # On retest, assume the technician has addressed marginal issues,
        # so drift/noise contributions shrink (models real bench behavior
        # where intermittent contact/noise issues often clear on reseat).
        shrink = sim.retest_improvement_factor if retest else 1.0

        calibration_offset = random.gauss(0, sim.calibration_offset_std_v) * shrink
        sensor_noise = random.gauss(0, sim.sensor_noise_std_v) * shrink

        # Occasional power supply instability injects a larger voltage error.
        power_unstable = random.random() < sim.power_instability_rate * shrink
        instability_error = random.uniform(0.15, 0.45) * random.choice([-1, 1]) if power_unstable else 0.0

        base_noise = random.gauss(0, sim.voltage_noise_std_v) * shrink
        measured_voltage = round(
            v_limits.nominal_v + base_noise + calibration_offset + sensor_noise + instability_error, 4
        )

        current_noise = random.gauss(0, sim.current_noise_std_a) * shrink
        current = round(max(0.0, c_limits.nominal_a + current_noise), 4)

        ambient = t_limits.ambient_nominal_c + random.gauss(0, t_limits.ambient_drift_c)
        # Self-heating under load, larger when current is high.
        self_heating = current * random.uniform(9.0, 14.0)
        temp_drift = random.gauss(0, sim.temp_drift_std_c) * shrink
        temperature = round(max(ambient, ambient + self_heating * 0.4 + temp_drift * 0.3), 2)

        humidity = round(
            min(100.0, max(0.0, random.gauss(sim.humidity_mean_pct, sim.humidity_std_pct))), 1
        )

        leakage = round(max(0.0, random.gauss(sim.leakage_mean_ma, sim.leakage_std_ma) * shrink), 3)

        ripple = round(max(0.0, random.gauss(sim.ripple_mean_mv, sim.ripple_std_mv) * shrink), 2)

        spikes = max(0, int(round(random.gauss(sim.spike_poisson_lambda * shrink, 1.0))))
        spikes = min(spikes, 12)

        duration = round(max(5.0, random.gauss(sim.test_duration_mean_s, sim.test_duration_std_s)), 2)

        return Measurement(
            measured_voltage_v=measured_voltage,
            current_a=current,
            temperature_c=temperature,
            humidity_pct=humidity,
            leakage_current_ma=leakage,
            voltage_ripple_mv=ripple,
            voltage_spikes=spikes,
            calibration_offset_v=round(calibration_offset, 4),
            sensor_noise_v=round(sensor_noise, 4),
            environmental_temp_c=round(ambient, 2),
            test_duration_s=duration,
        )

    def evaluate(self, measurement: Measurement) -> Tuple[bool, List[FailureMode]]:
        v = self.config.voltage
        c = self.config.current
        t = self.config.thermal
        e = self.config.environment
        lk = self.config.leakage

        failures: List[FailureMode] = []

        if measurement.measured_voltage_v > v.pass_max_v:
            failures.append(FailureMode.VOLTAGE_TOO_HIGH)
        elif measurement.measured_voltage_v < v.pass_min_v:
            failures.append(FailureMode.VOLTAGE_TOO_LOW)

        if not (c.min_a <= measurement.current_a <= c.max_a):
            failures.append(FailureMode.CURRENT_OUT_OF_SPEC)

        if measurement.temperature_c >= t.max_temp_c:
            failures.append(FailureMode.OVER_TEMPERATURE)

        if measurement.leakage_current_ma >= lk.max_leakage_ma:
            failures.append(FailureMode.HIGH_LEAKAGE)

        if measurement.voltage_ripple_mv >= v.ripple_max_mv:
            failures.append(FailureMode.HIGH_RIPPLE)

        if measurement.voltage_spikes > v.max_spikes:
            failures.append(FailureMode.EXCESS_SPIKES)

        if not (e.humidity_min_pct <= measurement.humidity_pct <= e.humidity_max_pct):
            failures.append(FailureMode.HUMIDITY_OUT_OF_SPEC)

        passed = len(failures) == 0
        return passed, failures
