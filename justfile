# Project task runner

set dotenv-load := false

build_dir := "build"
c_files := "git ls-files '*.c' '*.h' '*.cpp'"

# Default: show available recipes
default:
    @just --list

# Configure the CMake build (tests, tools, examples; warnings are errors)
setup:
    cmake -S . -B {{build_dir}} -DBUILD_TESTS=ON -DBUILD_TOOLS=ON -DBUILD_EXAMPLES=ON -DTURBIDITY_WARNINGS_AS_ERRORS=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# Compile the library, tools, examples, and tests
build: setup
    cmake --build {{build_dir}} --parallel

# Format C/C++ sources in place (mutates working tree — use locally)
fmt:
    {{c_files}} | xargs clang-format -i

# Verify formatting (non-mutating — use in CI)
fmt-check:
    {{c_files}} | xargs clang-format --dry-run --Werror

# Static analysis over the compile database, plus a Python syntax check
lint: setup
    clang-tidy --quiet -p {{build_dir}} $(git ls-files '*.c')
    python3 -c "import ast, sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]" $(git ls-files '*.py')

# Format-check + lint (non-mutating — CI-equivalent)
check: fmt-check lint

# Build and run the test suite
test: build
    ctest --test-dir {{build_dir}} --output-on-failure

# Install the pinned scadman and the OpenSCAD libraries scadman.lock pins, into .scadman/env
scad-setup:
    @scripts/install-libraries.sh

# Fail when the sampler case stops fitting its board, tube, screws, drivers or actuator
check-sampler-case:
    OPENSCADPATH={{justfile_directory()}}/.scadman/env scripts/check-sampler-case.sh

# Render the pictures in hardware/sampler-case/views.tsv to build/figures: all, or `just render 'case_*'`
render filter="*":
    OPENSCADPATH={{justfile_directory()}}/.scadman/env scripts/render-views.sh "{{filter}}"

# Regenerate calibration tables, fit reports, and the runtime header
regen:
    python3 tools/generate_vendor_calibration.py

# Export the tube case and flange STLs from the OpenSCAD source
tube-case:
    openscad --export-format binstl -D 'part="base"' -D 'orient="print"' -o hardware/tube-case/base.stl hardware/tube-case/tube_case.scad
    openscad --export-format binstl -D 'part="lid"' -D 'orient="print"' -o hardware/tube-case/lid.stl hardware/tube-case/tube_case.scad
    openscad --export-format binstl -o hardware/tst-flange/flange.stl hardware/tst-flange/flange.scad

# Compile both Arduino examples for every board in their platformio.ini
arduino:
    pio run -d examples/arduino
    pio run -d examples/arduino-multichannel

# Flash an Arduino example (arduino: single head with the model; arduino-multichannel: raw counts from A0-A3)
upload env="uno" example="arduino":
    pio run -d examples/{{example}} -e {{env}} -t upload

# Record the board's CSV log to a file until Ctrl+C (or pass --duration SECONDS)
capture port output *args:
    python3 tools/capture_serial.py --port {{port}} --output {{output}} {{args}}

# Summarize capture files: count, mean, std, min, max per signal column
summarize +files:
    python3 tools/summarize_capture.py {{files}}

# Plot a concentration series to SVG in build/plots (tools/plot_series.py --help)
plot +args:
    python3 tools/plot_series.py {{args}}

# Remove build artifacts
clean:
    rm -rf {{build_dir}}
