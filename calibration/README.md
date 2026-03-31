# Calibration

`vendor-data/` contains the raw WebPlotDigitizer exports from the vendor datasheets.

`generate_calibration_csvs.py` converts those raw `voltage, NTU` point clouds into the
canonical calibration tables:

- `tst10-calibration.csv`
- `tsw10-calibration.csv`

Those generated CSVs contain three columns:

- `NTU`
- `Voltage (High)`
- `Voltage (Low)`

`plot.py` reads the generated CSVs and writes the derived plot images and quadratic
fit reports:

- `tst10-plot.png`
- `tsw10-plot.png`
- `tst10-fit.txt`
- `tsw10-fit.txt`
