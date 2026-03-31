#!/usr/bin/env python3
import os

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def fit_curve(x, y):
    coeffs = np.polyfit(x, y, deg=2)
    poly = np.poly1d(coeffs)
    fitted = poly(x)
    residual_sum_squares = np.sum((y - fitted) ** 2)
    total_sum_squares = np.sum((y - np.mean(y)) ** 2)
    r_squared = (
        1.0 if np.isclose(total_sum_squares, 0.0) else 1.0 - residual_sum_squares / total_sum_squares
    )
    return coeffs, poly, r_squared


def write_fit_report(csv_path, sensor_label, report_path, fit_results, ntu_min, ntu_max):
    lines = [
        f"Sensor: {sensor_label}",
        f"Source CSV: {os.path.basename(csv_path)}",
        "Model: quadratic fit of voltage as a function of NTU",
        f"Valid NTU range: {ntu_min:.0f} to {ntu_max:.0f}",
        "",
    ]

    for curve_col in ["Voltage (High)", "Voltage (Low)"]:
        coeffs, _, r_squared = fit_results[curve_col]
        lines.extend(
            [
                curve_col,
                "Equation:",
                "V = a*NTU^2 + b*NTU + c",
                (
                    f"V = {coeffs[0]:.12e}*NTU^2 + "
                    f"{coeffs[1]:.12e}*NTU + {coeffs[2]:.12e}"
                ),
                "Copy/paste form:",
                (
                    f"voltage = ({coeffs[0]:.12e} * ntu * ntu) + "
                    f"({coeffs[1]:.12e} * ntu) + {coeffs[2]:.12e}"
                ),
                "Coefficients:",
                f"a = {coeffs[0]:.12e}",
                f"b = {coeffs[1]:.12e}",
                f"c = {coeffs[2]:.12e}",
                f"R^2 = {r_squared:.9f}",
                "",
            ]
        )

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")

    print(f"Saved fit report: {report_path}")


def plot_sensor(csv_path, sensor_label, output_path, report_path):
    """
    Reads a CSV with columns [NTU, Voltage (High), Voltage (Low)],
    then plots raw data + quadratic fits for both curves on its own figure.
    """
    df = pd.read_csv(csv_path)
    x = df["NTU"].values
    fit_results = {}

    fig, ax = plt.subplots(figsize=(8, 5))
    for curve_col, color in zip(
        ["Voltage (High)", "Voltage (Low)"], ["C0", "C1"]
    ):
        y = df[curve_col].values

        # scatter raw data
        ax.scatter(x, y, label=f"{curve_col} data", color=color, s=40, alpha=0.7)

        # fit quadratic
        coeffs, poly, r_squared = fit_curve(x, y)
        fit_results[curve_col] = (coeffs, poly, r_squared)
        xs = np.linspace(x.min(), x.max(), 400)
        ys = poly(xs)

        eqn = f"{coeffs[0]:.2e}·x² + {coeffs[1]:.2e}·x + {coeffs[2]:.2f}"
        ax.plot(
            xs,
            ys,
            "--",
            label=f"{curve_col} fit:\n{eqn}\nR^2={r_squared:.4f}",
            color=color,
        )

    ax.set_title(f"{sensor_label}: Voltage vs NTU with Quadratic Fits")
    ax.set_xlabel("NTU")
    ax.set_ylabel("Voltage (V)")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best", fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    print(f"Saved plot: {output_path}")
    write_fit_report(csv_path, sensor_label, report_path, fit_results, x.min(), x.max())


if __name__ == "__main__":
    cal_dir = os.path.dirname(os.path.abspath(__file__))
    sensors = [
        ("tst10-calibration.csv", "TST-10", "tst10-plot.png", "tst10-fit.txt"),
        ("tsw10-calibration.csv", "TSW-10", "tsw10-plot.png", "tsw10-fit.txt"),
    ]

    for csv_name, label, output_name, report_name in sensors:
        csv_path = os.path.join(cal_dir, csv_name)
        output_path = os.path.join(cal_dir, output_name)
        report_path = os.path.join(cal_dir, report_name)
        if not os.path.isfile(csv_path):
            print(f"WARNING: missing file: {csv_path}")
            continue
        plot_sensor(csv_path, label, output_path, report_path)
