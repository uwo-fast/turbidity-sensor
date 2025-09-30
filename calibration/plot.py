#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_sensor(csv_path, sensor_label):
    """
    Reads a CSV with columns [NTU, Voltage (Curve 1), Voltage (Curve 2)],
    then plots raw data + quadratic fits for both curves on its own figure.
    """
    df = pd.read_csv(csv_path)
    x = df["NTU"].values

    plt.figure(figsize=(8, 5))
    for curve_col, color in zip(
        ["Voltage (Curve 1)", "Voltage (Curve 2)"], ["C0", "C1"]
    ):
        y = df[curve_col].values

        # scatter raw data
        plt.scatter(x, y, label=f"{curve_col} data", color=color, s=40, alpha=0.7)

        # fit quadratic
        coeffs = np.polyfit(x, y, deg=2)
        poly = np.poly1d(coeffs)
        xs = np.linspace(x.min(), x.max(), 400)
        ys = poly(xs)

        eqn = f"{coeffs[0]:.2e}·x² + {coeffs[1]:.2e}·x + {coeffs[2]:.2f}"
        plt.plot(xs, ys, "--", label=f"{curve_col} fit:\n{eqn}", color=color)

    plt.title(f"{sensor_label}: Voltage vs NTU with Quadratic Fits")
    plt.xlabel("NTU")
    plt.ylabel("Voltage (V)")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.legend(loc="best", fontsize="small")
    plt.tight_layout()


if __name__ == "__main__":
    cal_dir = "calibration"
    sensors = [
        ("Voltage_vs_NTU_TST-10.csv", "TST-10"),
        ("Voltage_vs_NTU_TSW-10.csv", "TSW-10"),
    ]

    for fname, label in sensors:
        path = os.path.join(cal_dir, fname)
        if not os.path.isfile(path):
            print(f"WARNING: missing file: {path}")
            continue
        plot_sensor(path, label)

    plt.show()
