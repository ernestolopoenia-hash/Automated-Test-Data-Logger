"""
plotting.py
===========
Generates all engineering plots for a completed stress test run using
matplotlib, saving each as a high-resolution PNG suitable for embedding
in the PDF report or reviewing standalone.
"""

from __future__ import annotations

import os
from typing import List

import matplotlib
matplotlib.use("Agg")  # Headless rendering -- no display server required.
import matplotlib.pyplot as plt

from config import AppConfig
from dut import DeviceUnderTest
from measurement import TestResult

# A restrained, professional palette (avoids default matplotlib "candy" colors).
COLOR_PASS = "#2E8B57"
COLOR_FAIL = "#C0392B"
COLOR_PRIMARY = "#2C3E50"
COLOR_ACCENT = "#2980B9"
COLOR_GRID = "#D5D8DC"


class PlotGenerator:
    """Produces the full standard set of stress-test result plots."""

    def __init__(self, config: AppConfig, duts: List[DeviceUnderTest]):
        self.config = config
        self.duts = duts
        self.plots_dir = os.path.join(config.output_dir, config.plots_subdir)
        os.makedirs(self.plots_dir, exist_ok=True)
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.edgecolor": "#7F8C8D",
            "axes.grid": True,
            "grid.color": COLOR_GRID,
            "grid.linewidth": 0.6,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        })

    def _path(self, filename: str) -> str:
        return os.path.join(self.plots_dir, filename)

    def _save(self, fig, filename: str) -> str:
        path = self._path(filename)
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        return path

    def generate_all(self) -> List[str]:
        """Generates every plot and returns the list of saved file paths."""
        paths = [
            self.voltage_histogram(),
            self.temperature_histogram(),
            self.current_histogram(),
            self.leakage_histogram(),
            self.humidity_histogram(),
            self.pass_fail_pie(),
            self.voltage_vs_temperature_scatter(),
            self.current_vs_temperature_scatter(),
            self.voltage_over_test_time(),
            self.failure_mode_bar_chart(),
        ]
        return [p for p in paths if p]

    # ------------------------------------------------------------------
    # Histograms
    # ------------------------------------------------------------------

    def _histogram(self, values, title, xlabel, filename, limit_lines=None, color=COLOR_ACCENT):
        fig, ax = plt.subplots(figsize=(6.4, 4.2))
        ax.hist(values, bins=20, color=color, edgecolor="white", alpha=0.9)
        if limit_lines:
            for value, label in limit_lines:
                ax.axvline(value, color=COLOR_FAIL, linestyle="--", linewidth=1.3, label=label)
            ax.legend(fontsize=8)
        ax.set_title(title, fontsize=12, fontweight="bold", color=COLOR_PRIMARY)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Number of DUTs")
        return self._save(fig, filename)

    def voltage_histogram(self) -> str:
        values = [d.final_measurement.measured_voltage_v for d in self.duts]
        v = self.config.voltage
        return self._histogram(
            values, "Measured Voltage Distribution", "Voltage (V)",
            "voltage_histogram.png",
            limit_lines=[(v.pass_min_v, "Lower Limit"), (v.pass_max_v, "Upper Limit")],
        )

    def temperature_histogram(self) -> str:
        values = [d.final_measurement.temperature_c for d in self.duts]
        t = self.config.thermal
        return self._histogram(
            values, "Temperature Distribution", "Temperature (\u00b0C)",
            "temperature_histogram.png",
            limit_lines=[(t.max_temp_c, "Max Limit")],
            color="#E67E22",
        )

    def current_histogram(self) -> str:
        values = [d.final_measurement.current_a for d in self.duts]
        c = self.config.current
        return self._histogram(
            values, "Current Distribution", "Current (A)",
            "current_histogram.png",
            limit_lines=[(c.min_a, "Lower Limit"), (c.max_a, "Upper Limit")],
        )

    def leakage_histogram(self) -> str:
        values = [d.final_measurement.leakage_current_ma for d in self.duts]
        lk = self.config.leakage
        return self._histogram(
            values, "Leakage Current Distribution", "Leakage Current (mA)",
            "leakage_histogram.png",
            limit_lines=[(lk.max_leakage_ma, "Max Limit")],
            color="#8E44AD",
        )

    def humidity_histogram(self) -> str:
        values = [d.final_measurement.humidity_pct for d in self.duts]
        e = self.config.environment
        return self._histogram(
            values, "Humidity Distribution", "Humidity (% RH)",
            "humidity_histogram.png",
            limit_lines=[(e.humidity_min_pct, "Lower Limit"), (e.humidity_max_pct, "Upper Limit")],
            color="#16A085",
        )

    # ------------------------------------------------------------------
    # Pass/Fail summary
    # ------------------------------------------------------------------

    def pass_fail_pie(self) -> str:
        passed = sum(1 for d in self.duts if d.passed)
        failed = sum(1 for d in self.duts if not d.passed)
        fig, ax = plt.subplots(figsize=(5.5, 5.5))
        values, labels, colors = [], [], []
        if passed:
            values.append(passed); labels.append(f"PASS ({passed})"); colors.append(COLOR_PASS)
        if failed:
            values.append(failed); labels.append(f"FAIL ({failed})"); colors.append(COLOR_FAIL)
        ax.pie(
            values, labels=labels, colors=colors, autopct="%1.1f%%",
            startangle=90, textprops={"fontsize": 10},
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_title("Pass vs. Fail Distribution", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)
        return self._save(fig, "pass_fail_pie.png")

    # ------------------------------------------------------------------
    # Scatter plots
    # ------------------------------------------------------------------

    def _scatter(self, x, y, xlabel, ylabel, title, filename):
        fig, ax = plt.subplots(figsize=(6.4, 4.2))
        pass_x = [xv for xv, d in zip(x, self.duts) if d.passed]
        pass_y = [yv for yv, d in zip(y, self.duts) if d.passed]
        fail_x = [xv for xv, d in zip(x, self.duts) if not d.passed]
        fail_y = [yv for yv, d in zip(y, self.duts) if not d.passed]
        ax.scatter(pass_x, pass_y, color=COLOR_PASS, label="PASS", alpha=0.7, s=28, edgecolor="white")
        ax.scatter(fail_x, fail_y, color=COLOR_FAIL, label="FAIL", alpha=0.8, s=28, edgecolor="white")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=12, fontweight="bold", color=COLOR_PRIMARY)
        ax.legend(fontsize=8)
        return self._save(fig, filename)

    def voltage_vs_temperature_scatter(self) -> str:
        x = [d.final_measurement.measured_voltage_v for d in self.duts]
        y = [d.final_measurement.temperature_c for d in self.duts]
        return self._scatter(
            x, y, "Voltage (V)", "Temperature (\u00b0C)",
            "Voltage vs. Temperature", "voltage_vs_temperature.png",
        )

    def current_vs_temperature_scatter(self) -> str:
        x = [d.final_measurement.current_a for d in self.duts]
        y = [d.final_measurement.temperature_c for d in self.duts]
        return self._scatter(
            x, y, "Current (A)", "Temperature (\u00b0C)",
            "Current vs. Temperature", "current_vs_temperature.png",
        )

    # ------------------------------------------------------------------
    # Time series
    # ------------------------------------------------------------------

    def voltage_over_test_time(self) -> str:
        fig, ax = plt.subplots(figsize=(7.2, 4.2))
        indices = list(range(1, len(self.duts) + 1))
        voltages = [d.final_measurement.measured_voltage_v for d in self.duts]
        v = self.config.voltage
        ax.plot(indices, voltages, color=COLOR_PRIMARY, linewidth=1.0, marker="o", markersize=2.5)
        ax.axhline(v.pass_min_v, color=COLOR_FAIL, linestyle="--", linewidth=1.0, label="Spec Limits")
        ax.axhline(v.pass_max_v, color=COLOR_FAIL, linestyle="--", linewidth=1.0)
        ax.set_xlabel("DUT Sequence (Simulated Test Time)")
        ax.set_ylabel("Measured Voltage (V)")
        ax.set_title("Voltage Over Simulated Test Sequence", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)
        ax.legend(fontsize=8)
        return self._save(fig, "voltage_over_test_time.png")

    # ------------------------------------------------------------------
    # Failure analysis
    # ------------------------------------------------------------------

    def failure_mode_bar_chart(self) -> str | None:
        counts: dict[str, int] = {}
        for d in self.duts:
            if not d.passed:
                for mode in (d.failure_reasons or [d.failure_reason]):
                    if mode.value != "None":
                        counts[mode.value] = counts.get(mode.value, 0) + 1

        fig, ax = plt.subplots(figsize=(7.2, 4.4))
        if not counts:
            ax.text(0.5, 0.5, "No Failures Recorded", ha="center", va="center", fontsize=13, color=COLOR_PASS)
            ax.axis("off")
        else:
            items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
            labels = [k for k, _ in items]
            values = [v for _, v in items]
            ax.barh(labels, values, color=COLOR_FAIL, edgecolor="white")
            ax.invert_yaxis()
            ax.set_xlabel("Occurrences")
            ax.set_title("Failure Mode Frequency", fontsize=12, fontweight="bold", color=COLOR_PRIMARY)
        return self._save(fig, "failure_mode_bar_chart.png")
