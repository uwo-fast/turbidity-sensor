#!/usr/bin/env python3
import csv
import math
from bisect import bisect_left
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "calibration"
VENDOR_DIR = DATA_DIR / "vendor-data"
HEADER_PATH = PROJECT_ROOT / "src" / "turbidity_model_data.generated.h"

SENSORS = [
    {"slug": "tst10", "enum": "TURBIDITY_SENSOR_TST10", "label": "TST-10", "max_ntu": 4000},
    {"slug": "tsw10", "enum": "TURBIDITY_SENSOR_TSW10", "label": "TSW-10", "max_ntu": 2000},
]


def load_vendor_curve(csv_path: Path):
    buckets = defaultdict(list)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for line_number, row in enumerate(reader, start=1):
            if not row:
                continue
            if len(row) != 2:
                raise ValueError(f"Malformed row in {csv_path}:{line_number}")
            voltage = float(row[0].strip())
            ntu = float(row[1].strip())
            buckets[ntu].append(voltage)
    if len(buckets) < 2:
        raise ValueError(f"Not enough points in {csv_path}")
    return [(ntu, sum(values) / len(values)) for ntu, values in sorted(buckets.items())]


def interpolate_curve(curve, target_ntu):
    ntu_values = [point[0] for point in curve]
    index = bisect_left(ntu_values, target_ntu)
    if index < len(curve) and curve[index][0] == target_ntu:
        return curve[index][1]
    if index == 0:
        left, right = curve[0], curve[1]
    elif index == len(curve):
        left, right = curve[-2], curve[-1]
    else:
        left, right = curve[index - 1], curve[index]
    ntu0, voltage0 = left
    ntu1, voltage1 = right
    if ntu1 == ntu0:
        return voltage0
    fraction = (target_ntu - ntu0) / (ntu1 - ntu0)
    return voltage0 + fraction * (voltage1 - voltage0)


def solve_linear_system(matrix, vector):
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row: abs(augmented[row][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1e-12:
            raise ValueError("Singular matrix")
        augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]

        pivot = augmented[pivot_index][pivot_index]
        for column_index in range(pivot_index, size + 1):
            augmented[pivot_index][column_index] /= pivot

        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            for column_index in range(pivot_index, size + 1):
                augmented[row_index][column_index] -= factor * augmented[pivot_index][column_index]

    return [augmented[index][size] for index in range(size)]


def fit_quadratic(x_values, y_values):
    count = len(x_values)
    sum_x = sum(x_values)
    sum_x2 = sum(x * x for x in x_values)
    sum_x3 = sum(x * x * x for x in x_values)
    sum_x4 = sum(x * x * x * x for x in x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2y = sum((x * x) * y for x, y in zip(x_values, y_values))

    matrix = [
        [sum_x4, sum_x3, sum_x2],
        [sum_x3, sum_x2, sum_x],
        [sum_x2, sum_x, count],
    ]
    vector = [sum_x2y, sum_xy, sum_y]
    a, b, c = solve_linear_system(matrix, vector)

    mean_y = sum_y / count
    fitted_values = [(a * x * x) + (b * x) + c for x in x_values]
    residual_sum_squares = sum((y - fitted) ** 2 for y, fitted in zip(y_values, fitted_values))
    total_sum_squares = sum((y - mean_y) ** 2 for y in y_values)
    r_squared = 1.0 if math.isclose(total_sum_squares, 0.0) else 1.0 - (residual_sum_squares / total_sum_squares)
    return (a, b, c), r_squared


def write_calibration_csv(path: Path, low_curve, high_curve, max_ntu: int):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["NTU", "Voltage (High)", "Voltage (Low)"])
        for ntu in range(0, max_ntu + 1, 100):
            writer.writerow([
                ntu,
                f"{interpolate_curve(high_curve, ntu):.3f}",
                f"{interpolate_curve(low_curve, ntu):.3f}",
            ])


def read_generated_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_fit_report(path: Path, sensor_label: str, source_name: str, fit_results, ntu_min: int, ntu_max: int):
    lines = [
        f"Sensor: {sensor_label}",
        f"Source CSV: {source_name}",
        "Model: quadratic fit of voltage as a function of NTU",
        f"Valid NTU range: {ntu_min} to {ntu_max}",
        "",
    ]
    for curve_name in ["Voltage (High)", "Voltage (Low)"]:
        coefficients, r_squared = fit_results[curve_name]
        lines.extend([
            curve_name,
            "Equation:",
            "V = a*NTU^2 + b*NTU + c",
            f"V = {coefficients[0]:.12e}*NTU^2 + {coefficients[1]:.12e}*NTU + {coefficients[2]:.12e}",
            "Copy/paste form:",
            f"voltage = ({coefficients[0]:.12e} * ntu * ntu) + ({coefficients[1]:.12e} * ntu) + {coefficients[2]:.12e}",
            "Coefficients:",
            f"a = {coefficients[0]:.12e}",
            f"b = {coefficients[1]:.12e}",
            f"c = {coefficients[2]:.12e}",
            f"R^2 = {r_squared:.9f}",
            "",
        ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_generated_header(path: Path, sensor_rows):
    lines = [
        "/*",
        " * Generated by tools/generate_vendor_calibration.py.",
        " * Do not edit by hand.",
        " * Include turbidity/turbidity.h before this header.",
        " */",
        "#ifndef TURBIDITY_MODEL_DATA_GENERATED_H",
        "#define TURBIDITY_MODEL_DATA_GENERATED_H",
        "",
        "typedef struct turbidity_quadratic {",
        "    double a_mv_per_ntu2;",
        "    double b_mv_per_ntu;",
        "    double c_mv;",
        "} turbidity_quadratic;",
        "",
        "typedef struct turbidity_model_record {",
        "    turbidity_sensor_kind sensor_kind;",
        "    const char *name;",
        "    double max_ntu;",
        "    turbidity_quadratic low_curve;",
        "    turbidity_quadratic high_curve;",
        "} turbidity_model_record;",
        "",
        f"#define TURBIDITY_MODEL_RECORD_COUNT {len(sensor_rows)}U",
        "",
        "static const turbidity_model_record TURBIDITY_MODEL_RECORDS[TURBIDITY_MODEL_RECORD_COUNT] = {",
    ]
    for row in sensor_rows:
        lines.extend([
            "    {",
            f"        {row['enum']},",
            f"        \"{row['slug']}\",",
            f"        {row['max_ntu']:.1f},",
            f"        {{{row['low'][0] * 1000.0:.12e}, {row['low'][1] * 1000.0:.12e}, {row['low'][2] * 1000.0:.12e}}},",
            f"        {{{row['high'][0] * 1000.0:.12e}, {row['high'][1] * 1000.0:.12e}, {row['high'][2] * 1000.0:.12e}}},",
            "    },",
        ])
    lines.extend([
        "};",
        "",
        "#endif",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def maybe_write_plot(csv_path: Path, output_path: Path, sensor_label: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    rows = read_generated_csv(csv_path)
    x_values = [float(row["NTU"]) for row in rows]
    high_values = [float(row["Voltage (High)"]) for row in rows]
    low_values = [float(row["Voltage (Low)"]) for row in rows]

    figure, axis = plt.subplots(figsize=(8, 5))
    axis.plot(x_values, high_values, label="Voltage (High)", color="C0")
    axis.plot(x_values, low_values, label="Voltage (Low)", color="C1")
    axis.set_title(f"{sensor_label}: Voltage vs NTU")
    axis.set_xlabel("NTU")
    axis.set_ylabel("Voltage (V)")
    axis.grid(True, linestyle=":", alpha=0.5)
    axis.legend(loc="best")
    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def main():
    sensor_rows = []

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HEADER_PATH.parent.mkdir(parents=True, exist_ok=True)

    for sensor in SENSORS:
        high_curve = load_vendor_curve(VENDOR_DIR / f"{sensor['slug']}-high.csv")
        low_curve = load_vendor_curve(VENDOR_DIR / f"{sensor['slug']}-low.csv")
        csv_path = DATA_DIR / f"{sensor['slug']}-calibration.csv"
        fit_path = DATA_DIR / f"{sensor['slug']}-fit.txt"
        plot_path = DATA_DIR / f"{sensor['slug']}-plot.png"

        write_calibration_csv(csv_path, low_curve, high_curve, sensor["max_ntu"])
        rows = read_generated_csv(csv_path)
        ntu_values = [float(row["NTU"]) for row in rows]
        high_values = [float(row["Voltage (High)"]) for row in rows]
        low_values = [float(row["Voltage (Low)"]) for row in rows]
        high_fit = fit_quadratic(ntu_values, high_values)
        low_fit = fit_quadratic(ntu_values, low_values)

        write_fit_report(
            fit_path,
            sensor["label"],
            csv_path.name,
            {"Voltage (High)": high_fit, "Voltage (Low)": low_fit},
            0,
            sensor["max_ntu"],
        )
        maybe_write_plot(csv_path, plot_path, sensor["label"])

        sensor_rows.append({
            "slug": sensor["slug"],
            "enum": sensor["enum"],
            "max_ntu": float(sensor["max_ntu"]),
            "low": low_fit[0],
            "high": high_fit[0],
        })

    write_generated_header(HEADER_PATH, sensor_rows)
    print(f"Wrote generated header: {HEADER_PATH}")


if __name__ == "__main__":
    main()
