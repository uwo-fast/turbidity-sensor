# Column rig: Pi logger

Runs the syringe actuator in bursts from a Raspberry Pi and logs the turbidity head to CSV over
several days. The setup is described in `data/bench/2026-11-05/notes.md`. The schedule and level settings in
`rig.toml` are placeholders until the bench test (`docs/bench/sampler-waveform.md`) replaces them.

**Status:** sample picking is tested against real motor runs (`data/bench/2026-11-05/`). The cycle is tested
against a simulated Nano and a stub motor (`tests/test_rig.py`). Nothing here depends on knowing the crank position.

## Hardware

```text
head -> SEN0189 adapter -> Nano analog input -> USB -> Pi 4B -> Adafruit 2348 HAT -> motor on M4
```

- **Sensor:** connected through the Nano, never directly to the Pi. The Pi has no analog inputs, and the
  adapter output reaches about 4.8 V, which is too high for a GPIO pin. The Nano also keeps the same ADC chain
  as the bench data.
- **Nano firmware:** the multichannel logger at 50 Hz:

  ```sh
  PLATFORMIO_BUILD_FLAGS=-DTURBIDITY_SAMPLE_PERIOD_MS=20 just upload nano arduino-multichannel
  ```

- **Motor:** on the HAT terminal set by `motor.number` in `rig.toml` (M4 here), with 12 V on the HAT power
  terminal. The Pi has its own supply. The HAT is rated 4.5–13.5 V and 1.2 A per channel. This covers the N20
  (0.75 A stall, extrapolated) but not the GA25, whose stall current is up to 2.1 A.

## Setup

On a current Raspberry Pi OS:

```sh
sudo raspi-config nonint do_i2c 0   # then reboot
python3 -m venv ~/rig-venv
~/rig-venv/bin/pip install -r requirements.txt
```

With the HAT on, `/usr/sbin/i2cdetect -y 1` shows `60` (and `70`, the all-call address of the chip). Copy
this folder to `~/rig`. Set `channel` and `air_reference` in `rig.toml` for the head in use.

## Use

```sh
~/rig-venv/bin/python rig.py motor --throttle 0.5 --seconds 3   # test the motor, up to 60 s
~/rig-venv/bin/python rig.py stop                               # turn the motor channel off
~/rig-venv/bin/python rig.py run                                # run the cycle until Ctrl+C
```

For a long run, install the service. It restarts after a failure, and after a reboot if enabled:

```sh
sudo cp turbidity-rig.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now turbidity-rig
journalctl -u turbidity-rig -f
```

## The cycle

Every `period_s`, the motor runs for `burst_s`, and every row is logged at the full Nano rate. Air and culture pass
the beam in turn, so a burst contains short steady stretches at the culture level. Those stretches give the reading.
Meniscus crossings and droplets swing far from any steady level and are skipped. Each start runs at `kick_throttle`
for `kick_s`, then drops to `throttle`, in case the crank has stopped at a stiff position.

## Output

Written to `data_dir`:

- **`summary.csv`:** one row per burst, with the culture level picked from it, the number of rows it came from, and a
  verdict.
- **`raw-YYYYMMDD.csv`:** every Nano row during bursts, and 1 Hz otherwise. `clock_synced` is 0 until NTP has synced.
  The Pi has no battery-backed clock, so those timestamps can be wrong after a power cut.
- **`events.csv`:** starts, stops, lost links and board resets.

`pick_samples.py` repeats the picking on any saved raw file without modifying it, so the limits can be changed and the
whole run re-picked afterwards.

| Verdict | Means |
| --- | --- |
| `ok` | The burst has at least `min_sample_rows` rows of culture. Use it |
| `thin` | Culture reached the beam, but too briefly. A meniscus can skew the value, so it is left off the chart |
| `no_sample` | The signal moved, but culture never held steady in the beam. Either the line did not bring culture to the beam, or the culture reads like air |
| `no_motion` | The signal never swung by `min_swing`, so nothing passed the beam. Check that the crank turns, the syringe is on its fitting and the riser is in the culture |
| `aborted` | The Nano was lost or reset mid-burst. The motor was stopped |

## Results page

A read-only page for monitoring a run in the browser on the Pi. It needs nothing installed, and `rig.py`
runs the same with or without it.

```sh
python3 view_server.py     # then open http://127.0.0.1:8080/ on the Pi
```

It shows whether new data is arriving, the latest good reading, a chart of good readings, and the last
10 cycles with their results. It checks for new data every 30 s, and a run updates every 15 minutes. Only
`ok` cycles count as readings. Every other cycle is listed with what went wrong and no value. After 45 minutes
with no new cycle, the page shows "Not updating". This limit is fixed in `view/view.js`; change it if
`period_s` changes much.

**Security:**

- It listens only on `127.0.0.1`, a fixed address with no option to change it, so other computers cannot
  connect. To view it from another computer, use an SSH tunnel with `-t`, so that Ctrl+C also stops the
  program on the Pi: `ssh -t -L 8080:127.0.0.1:8080 cam@<pi> python3 rig/view_server.py`. Then open the same
  address on that computer. Without `-t`, the server keeps running on the Pi and holds the port. Run
  `pkill -f view_server.py` on the Pi to stop it.
- It serves only its three page files and a copy of `summary.csv`, and refuses any other request. It also
  refuses requests other than `GET`.
- It opens the real `summary.csv` read-only, keeps its copy in memory and replaces the copy whole on each
  update, and writes no files.
- It shares no code or state with `rig.py`, and has no way to reach the motor or the Nano.

To start it at boot, install `turbidity-view.service` the same way as the rig's service.

## Limits

- **A crash can leave the motor running.** The PWM chip on the HAT holds its last setting and has
  no heartbeat. A clean stop, a failed process (`ExecStopPost`) and a restart all stop the motor, but a
  frozen or unpowered Pi cannot. The motor would keep cycling the syringe until power is removed.
- **Picking needs culture that reads above air** by more than `near_air`. A culture dense enough to read at or below air
  gives `no_sample`, not a wrong value. The raw rows are kept, so the run can be re-picked with different settings.
