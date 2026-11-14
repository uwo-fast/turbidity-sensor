# Column rig: Pi logger

Runs the syringe actuator in bursts from a Raspberry Pi and logs the turbidity head to CSV over
days. The setup is in `data/bench/2026-11-05/notes.md`. The schedule and level settings in
`rig.toml` are placeholders until the bench test (`docs/bench/sampler-waveform.md`) replaces them.

**Status:** the picking is tested against real motor runs (`data/bench/2026-11-05/`), and the cycle against a simulated
Nano and a stub motor (`tests/test_rig.py`). Nothing here depends on knowing where the crank is.

## Hardware

```text
head -> SEN0189 adapter -> Nano analog input -> USB -> Pi 4B -> Adafruit 2348 HAT -> motor on M4
```

- **Sensor:** through the Nano, never straight to the Pi. The Pi has no analog inputs, and the adapter's
  output reaches about 4.8 V, too much for a GPIO pin. The Nano keeps the ADC chain of the bench data.
- **Nano firmware:** the multichannel logger at 50 Hz:

  ```sh
  PLATFORMIO_BUILD_FLAGS=-DTURBIDITY_SAMPLE_PERIOD_MS=20 just upload nano arduino-multichannel
  ```

- **Motor:** the HAT terminal set by `motor.number` in `rig.toml` (M4 here), with 12 V on the HAT's power terminal, and the Pi on its own supply. The HAT
  is rated 4.5–13.5 V and 1.2 A per channel. That covers the N20 (0.75 A stall, extrapolated) but not
  the GA25's stall of up to 2.1 A.

## Setup

On a current Raspberry Pi OS:

```sh
sudo raspi-config nonint do_i2c 0   # then reboot
python3 -m venv ~/rig-venv
~/rig-venv/bin/pip install -r requirements.txt
```

With the HAT on, `/usr/sbin/i2cdetect -y 1` shows `60` (and `70`, the chip's all-call address). Copy
this folder to `~/rig`. Set `channel` and `air_reference` in `rig.toml` for the head in use.

## Use

```sh
~/rig-venv/bin/python rig.py motor --throttle 0.5 --seconds 3   # try the motor, up to 60 s
~/rig-venv/bin/python rig.py stop                               # motor channel off
~/rig-venv/bin/python rig.py run                                # the cycle, until Ctrl+C
```

For a long run, install the service. It restarts after a failure, and after a reboot if enabled:

```sh
sudo cp turbidity-rig.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now turbidity-rig
journalctl -u turbidity-rig -f
```

## The cycle

Every `period_s`, the motor runs for `burst_s`, with every row logged at the Nano's full rate. Air and culture pass the
beam in turn, so a burst holds short steady stretches at the culture's level, and those are its reading. Meniscus
crossings and droplets swing far from any level, and are skipped. Each start runs at `kick_throttle` for `kick_s`, then
drops to `throttle`, in case the crank rests somewhere stiff.

## Output

Written to `data_dir`:

- **`summary.csv`:** one row per burst: the culture level picked from it, how many rows it came from, and a verdict.
- **`raw-YYYYMMDD.csv`:** every Nano row during bursts, 1 Hz otherwise. `clock_synced` is 0 until NTP has synced, since the
  Pi has no battery clock: those times can be wrong after a power cut.
- **`events.csv`:** starts, stops, lost links and board resets.

`pick_samples.py` repeats the picking on any saved raw file and changes nothing, so the limits can be changed and the whole
run re-picked afterwards.

| Verdict | Means |
| --- | --- |
| `ok` | At least `min_sample_rows` of culture in the burst: use it |
| `thin` | Culture reached the beam, but too briefly: a meniscus can skew it, so it stays off the chart |
| `no_sample` | Only air and dips: the line did not bring culture to the beam, or the culture reads like air |
| `no_motion` | The signal barely moved: the crank may have stalled |
| `aborted` | The Nano was lost or reset mid-burst; the motor was stopped |

## Results page

A read-only page for watching a run, on the Pi's own browser. It needs nothing installed, and `rig.py`
runs the same with or without it.

```sh
python3 view_server.py     # then open http://127.0.0.1:8080/ on the Pi
```

It shows whether new data is arriving, the latest good reading, a chart of good readings, and the last
10 cycles with their results. It checks every 30 s, and a run updates every 15 minutes. Only `ok` cycles
count as readings; every other cycle is listed with what went wrong and no number. After 45 minutes
with no new cycle the page says "Not updating", which is a fixed limit in `view/view.js`: change it if
`period_s` changes much.

**To keep it safe:**

- It listens on `127.0.0.1` only, a fixed address with no option to widen it, so other computers cannot
  connect. From another computer, use an SSH tunnel, with `-t` so that Ctrl+C
  also stops the program on the Pi: `ssh -t -L 8080:127.0.0.1:8080 cam@<pi> python3 rig/view_server.py`,
  then open the same address there. Without `-t` it keeps running there and holds the port;
  `pkill -f view_server.py` on the Pi stops it.
- It serves its three page files and a copy of `summary.csv`, and refuses anything else. Requests other
  than `GET` are refused too.
- It opens the real `summary.csv` read-only, keeps its copy in memory, replaced whole, and writes no files.
- It shares no code or state with `rig.py`, and has no way to reach the motor or the Nano.

To start it at boot, install `turbidity-view.service` the same way as the rig's service.

## Limits

- **A crash can leave the motor running.** The HAT's PWM chip holds its last setting with no
  heartbeat. A clean stop, a failed process (`ExecStopPost`) and a restart all stop the motor, but a
  frozen or unpowered Pi cannot. The motor would keep cycling the syringe until power is removed.
- **Picking needs culture that reads above air,** by more than `near_air`. A culture dense enough to read at or below air gives
  `no_sample`, not a wrong number. The raw rows are kept, for a different pick then.
