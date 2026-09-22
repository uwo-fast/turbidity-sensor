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
    python3 -c "import ast, sys; ast.parse(open(sys.argv[1]).read(), sys.argv[1])" tools/generate_vendor_calibration.py

# Format-check + lint (non-mutating — CI-equivalent)
check: fmt-check lint

# Build and run the test suite
test: build
    ctest --test-dir {{build_dir}} --output-on-failure

# Regenerate calibration tables, fit reports, and the runtime header
regen:
    python3 tools/generate_vendor_calibration.py

# Compile the Arduino example with PlatformIO
arduino:
    pio run -d examples/arduino

# Remove build artifacts
clean:
    rm -rf {{build_dir}}
