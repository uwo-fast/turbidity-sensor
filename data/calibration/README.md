# Calibration Data

`vendor-data/` contains the raw `voltage,ntu` point clouds digitized from the Amphenol datasheet plots.

`tools/generate_vendor_calibration.py` is the single-source-of-truth pipeline for the generated artifacts in this directory. Running it regenerates:

- `tst10-calibration.csv`
- `tsw10-calibration.csv`
- `tst10-fit.txt`
- `tsw10-fit.txt`
- `src/turbidity_model_data.generated.h`

If `matplotlib` is available, it also refreshes the plot images:

- `tst10-plot.png`
- `tsw10-plot.png`

Generated calibration CSVs use this schema:

- `NTU`
- `Voltage (High)`
- `Voltage (Low)`

The runtime library does not parse these CSV files. It consumes the checked-in generated header in `src/`.
