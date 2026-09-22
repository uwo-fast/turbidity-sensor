# Contributing

## Quick start

Prerequisites: a C99 compiler, CMake >= 3.16, Python 3, [`just`](https://github.com/casey/just),
and clang-format / clang-tidy 18.1.8. PlatformIO is needed only for the Arduino example.

```sh
git clone https://github.com/uwo-fast/turbidity-sensor.git
cd turbidity-sensor
just test
```

`just --list` shows every task:

```sh
just build    # configure and compile (warnings are errors)
just test     # build and run the test suite
just check    # clang-format check + clang-tidy (CI-equivalent)
just fmt      # format C/C++ sources in place
just regen    # regenerate calibration artifacts from vendor data
just arduino  # compile the Arduino example with PlatformIO
```

## Workflow

1. Create a branch from `main`.
2. Make your changes.
3. Run `just check && just test`.
4. Commit using the format below.
5. Open a PR against `main`. CI must pass before merge.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`,
where type is one of `feat`, `fix`, `docs`, `refactor`, `test`, `ci`, `chore`, `build`.

```text
fix(stream): reject rows with empty fields
docs: document sensor wiring
```

Imperative mood, lowercase, no trailing period, subject under 72 characters. Put issue
references in the body, not the subject. One logical change per commit.

## Project conventions

- **Keep the library portable.** It is stateless and allocation-free, and must build for
  AVR, where `double` is 32-bit. CI compiles the Arduino example to check this.
- **Report errors through the API.** Every public function returns `turbidity_status`
  and writes results through out-pointers.
- **Keep vendor-derived calibration separate from empirical calibration.** The current
  model comes from digitized datasheet curves. Do not present its output as measured
  accuracy.
- **Keep the README honest.** Paste every example output in it from a real run.

## Generated files

`src/turbidity_model_data.generated.h` and the tables, fit reports and plots in
`data/calibration/` are generated. Do not edit them by hand. Change
`tools/generate_vendor_calibration.py` or the inputs in `data/calibration/vendor-data/`,
run `just regen`, and commit the results. CI fails if the generated files drift from
their inputs.

## Reference material

Do not commit copyrighted standards or other documents that cannot be redistributed.
Cite them and link to the official source instead.

## Reporting issues

Open a GitHub issue with what you expected, what happened, steps to reproduce, and your
environment. For hardware problems, also give the sensor, MCU board, and wiring.

## License

By contributing, you agree that your contributions are licensed under the project's
license, GPL-3.0-only.
