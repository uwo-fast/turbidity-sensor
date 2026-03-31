# Vendor Data

This directory holds the raw calibration inputs extracted from the Amphenol datasheet plots with WebPlotDigitizer.

Files:

- `tst10-datasheet-plot.png`
- `tsw10-datasheet-plot.png`
- `tst10-high.csv`
- `tst10-low.csv`
- `tsw10-high.csv`
- `tsw10-low.csv`

Each CSV contains two columns in the original extracted order:

- voltage in volts
- turbidity in NTU

These files are the source inputs for `tools/generate_vendor_calibration.py`.
