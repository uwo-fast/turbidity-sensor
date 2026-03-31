#!/usr/bin/env python3
import os

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_sensor(csv_path, sensor_label, output_path):
    """
    Reads a CSV with columns [NTU, Voltage (Curve 1), Voltage (Curve 2)],
    then plots raw data + quadratic fits for both curves on its own figure.
    """
    df = pd.read_csv(csv_path)
    x = df["NTU"].values

    fig, ax = plt.subplots(figsize=(8, 5))
    for curve_col, color in zip(
        ["Voltage (Curve 1)", "Voltage (Curve 2)"], ["C0", "C1"]
    ):
        y = df[curve_col].values

        # scatter raw data
        ax.scatter(x, y, label=f"{curve_col} data", color=color, s=40, alpha=0.7)

        # fit quadratic
        coeffs = np.polyfit(x, y, deg=2)
        poly = np.poly1d(coeffs)
        xs = np.linspace(x.min(), x.max(), 400)
        ys = poly(xs)

        eqn = f"{coeffs[0]:.2e}·x² + {coeffs[1]:.2e}·x + {coeffs[2]:.2f}"
        ax.plot(xs, ys, "--", label=f"{curve_col} fit:\n{eqn}", color=color)

    ax.set_title(f"{sensor_label}: Voltage vs NTU with Quadratic Fits")
    ax.set_xlabel("NTU")
    ax.set_ylabel("Voltage (V)")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="best", fontsize="small")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    print(f"Saved plot: {output_path}")


if __name__ == "__main__":
    cal_dir = os.path.dirname(os.path.abspath(__file__))
    sensors = [
        ("Voltage_vs_NTU_TST-10.csv", "TST-10", "tst10-plot.png"),
        ("Voltage_vs_NTU_TSW-10.csv", "TSW-10", "tsw10-plot.png"),
    ]

    for csv_name, label, output_name in sensors:
        csv_path = os.path.join(cal_dir, csv_name)
        output_path = os.path.join(cal_dir, output_name)
        if not os.path.isfile(csv_path):
            print(f"WARNING: missing file: {csv_path}")
            continue
        plot_sensor(csv_path, label, output_path)
