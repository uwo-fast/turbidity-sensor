#include "turbidity/turbidity.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static int g_failures = 0;

static void expect_true(int condition, const char *message)
{
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        g_failures += 1;
    }
}

static void expect_close(double actual, double expected, double tolerance, const char *message)
{
    if (fabs(actual - expected) > tolerance) {
        fprintf(
            stderr,
            "FAIL: %s (actual=%.12f expected=%.12f tolerance=%.12f)\n",
            message,
            actual,
            expected,
            tolerance
        );
        g_failures += 1;
    }
}

static double average_prefix(const double *values, size_t window, size_t index)
{
    size_t start = 0U;
    double sum = 0.0;
    size_t sample_count = 0U;
    size_t cursor;

    if (index + 1U > window) {
        start = index + 1U - window;
    }

    for (cursor = start; cursor <= index; ++cursor) {
        sum += values[cursor];
        sample_count += 1U;
    }

    return sum / (double)sample_count;
}

static int parse_stream_row(
    const char *line,
    unsigned int *timestamp_ms,
    char *sensor,
    double *raw_mv,
    double *filtered_mv,
    double *equivalent_mv,
    double *estimated_ntu,
    char *range_status
)
{
    return sscanf(
               line,
               "%u,%31[^,],%lf,%lf,%lf,%lf,%31s",
               timestamp_ms,
               sensor,
               raw_mv,
               filtered_mv,
               equivalent_mv,
               estimated_ntu,
               range_status
           ) == 7;
}

static int parse_calibration_json(
    const char *text,
    char *sensor,
    double *trim_t,
    double *gain,
    double *offset_mv,
    double *rmse_mv,
    double *max_abs_error_mv
)
{
    return sscanf(
               text,
               "{\"sensor\":\"%31[^\"]\",\"trim_t\":%lf,\"gain\":%lf,\"offset_mv\":%lf,\"rmse_mv\":%lf,\"max_abs_error_mv\":%lf}",
               sensor,
               trim_t,
               gain,
               offset_mv,
               rmse_mv,
               max_abs_error_mv
           ) == 6;
}

static void test_calibration_cli(const char *calibrate_executable)
{
    turbidity_profile source = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    double ntu[3] = {100.0, 900.0, 1700.0};
    double mv[3] = {0.0, 0.0, 0.0};
    char output_path[256];
    char command[1024];
    FILE *output = NULL;
    char line[256];
    char sensor[32] = {0};
    double trim_t = 0.0;
    double gain = 0.0;
    double offset_mv = 0.0;
    double rmse_mv = 0.0;
    double max_abs_error_mv = 0.0;
    size_t index;

    source.trim_t = 0.28;
    source.gain = 1.04;
    source.offset_mv = -21.0;

    for (index = 0; index < 3U; ++index) {
        expect_true(turbidity_predict_measured_mv(&source, ntu[index], &mv[index]) == TURBIDITY_STATUS_OK, "calibration fixture voltage should compute");
    }

    snprintf(output_path, sizeof(output_path), "calibration_output_%ld.json", (long)getpid());
    snprintf(
        command,
        sizeof(command),
        "\"%s\" --sensor tsw10 --point %.9f,%.9f --point %.9f,%.9f --point %.9f,%.9f > \"%s\"",
        calibrate_executable,
        ntu[0], mv[0],
        ntu[1], mv[1],
        ntu[2], mv[2],
        output_path
    );

    expect_true(system(command) == 0, "calibration CLI should exit successfully");

    output = fopen(output_path, "r");
    expect_true(output != NULL, "calibration CLI output file should open");
    if (output != NULL) {
        expect_true(fgets(line, sizeof(line), output) != NULL, "calibration CLI should emit JSON");
        if (line[0] != '\0') {
            expect_true(
                parse_calibration_json(line, sensor, &trim_t, &gain, &offset_mv, &rmse_mv, &max_abs_error_mv),
                "calibration JSON should match the documented schema"
            );
            expect_true(strcmp(sensor, "tsw10") == 0, "calibration JSON sensor should match CLI input");
            expect_close(trim_t, source.trim_t, 1e-5, "calibration JSON trim_t should recover the synthetic source profile");
            expect_close(gain, source.gain, 1e-6, "calibration JSON gain should recover the synthetic source profile");
            expect_close(offset_mv, source.offset_mv, 1e-3, "calibration JSON offset should recover the synthetic source profile");
            expect_close(rmse_mv, 0.0, 1e-6, "calibration JSON rmse should be zero for exact points");
            expect_close(max_abs_error_mv, 0.0, 1e-6, "calibration JSON max_abs_error should be zero for exact points");
        }
        fclose(output);
    }

    remove(output_path);
}

static void test_stream_cli(const char *stream_executable)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    double raw_mv[3] = {0.0, 0.0, 0.0};
    char input_path[256];
    char output_path[256];
    char command[1024];
    FILE *input = NULL;
    FILE *output = NULL;
    char line[256];
    size_t index;

    profile.trim_t = 0.25;
    profile.gain = 1.02;
    profile.offset_mv = -12.0;

    expect_true(turbidity_predict_measured_mv(&profile, 100.0, &raw_mv[0]) == TURBIDITY_STATUS_OK, "stream fixture point 1 should compute");
    expect_true(turbidity_predict_measured_mv(&profile, 700.0, &raw_mv[1]) == TURBIDITY_STATUS_OK, "stream fixture point 2 should compute");
    expect_true(turbidity_predict_measured_mv(&profile, 1500.0, &raw_mv[2]) == TURBIDITY_STATUS_OK, "stream fixture point 3 should compute");

    snprintf(input_path, sizeof(input_path), "stream_input_%ld.csv", (long)getpid());
    snprintf(output_path, sizeof(output_path), "stream_output_%ld.csv", (long)getpid());

    input = fopen(input_path, "w");
    expect_true(input != NULL, "stream fixture input file should open");
    if (input == NULL) {
        return;
    }

    fprintf(input, "timestamp_ms,raw_mv\n");
    for (index = 0; index < 3U; ++index) {
        fprintf(input, "%u,%.9f\n", (unsigned int)((index + 1U) * 100U), raw_mv[index]);
    }
    fclose(input);

    snprintf(
        command,
        sizeof(command),
        "\"%s\" --sensor tsw10 --trim %.9f --gain %.9f --offset-mv %.9f --filter-window 2 < \"%s\" > \"%s\"",
        stream_executable,
        profile.trim_t,
        profile.gain,
        profile.offset_mv,
        input_path,
        output_path
    );
    expect_true(system(command) == 0, "stream CLI should exit successfully on valid input");

    output = fopen(output_path, "r");
    expect_true(output != NULL, "stream output file should open");
    if (output != NULL) {
        expect_true(fgets(line, sizeof(line), output) != NULL, "stream output should contain a header");
        expect_true(
            strcmp(line, "timestamp_ms,sensor,raw_mv,filtered_mv,equivalent_mv,estimated_ntu,range_status\n") == 0,
            "stream output header should match the documented schema"
        );

        for (index = 0; index < 3U; ++index) {
            unsigned int timestamp_ms = 0U;
            char sensor[32] = {0};
            char range_status[32] = {0};
            double actual_raw_mv = 0.0;
            double actual_filtered_mv = 0.0;
            double actual_equivalent_mv = 0.0;
            double actual_estimated_ntu = 0.0;
            double expected_filtered_mv;
            turbidity_estimate expected_estimate;

            expect_true(fgets(line, sizeof(line), output) != NULL, "stream output should contain every expected row");
            if (line[0] == '\0') {
                continue;
            }

            expect_true(
                parse_stream_row(
                    line,
                    &timestamp_ms,
                    sensor,
                    &actual_raw_mv,
                    &actual_filtered_mv,
                    &actual_equivalent_mv,
                    &actual_estimated_ntu,
                    range_status
                ),
                "stream output row should match the documented schema"
            );

            expected_filtered_mv = average_prefix(raw_mv, 2U, index);
            expect_true(turbidity_estimate_ntu_from_mv(&profile, expected_filtered_mv, &expected_estimate) == TURBIDITY_STATUS_OK, "expected stream estimate should compute");

            expect_true(timestamp_ms == (unsigned int)((index + 1U) * 100U), "stream output timestamp should be preserved");
            expect_true(strcmp(sensor, "tsw10") == 0, "stream output sensor should match CLI input");
            expect_close(actual_raw_mv, raw_mv[index], 1e-3, "stream output raw_mv should match the input row");
            expect_close(actual_filtered_mv, expected_filtered_mv, 1e-3, "stream output filtered_mv should match the moving average");
            expect_close(actual_equivalent_mv, expected_estimate.equivalent_mv, 1e-3, "stream output equivalent_mv should match the model estimate");
            expect_close(actual_estimated_ntu, expected_estimate.estimated_ntu, 1e-3, "stream output estimated_ntu should match the model estimate");
            expect_true(strcmp(range_status, turbidity_range_status_name(expected_estimate.range_status)) == 0, "stream output range_status should match the model estimate");
        }

        fclose(output);
    }

    remove(input_path);
    remove(output_path);
}

static void test_stream_rejects_bad_header(const char *stream_executable)
{
    char input_path[256];
    char output_path[256];
    char command[1024];
    FILE *input = NULL;

    snprintf(input_path, sizeof(input_path), "bad_stream_input_%ld.csv", (long)getpid());
    snprintf(output_path, sizeof(output_path), "bad_stream_output_%ld.csv", (long)getpid());

    input = fopen(input_path, "w");
    expect_true(input != NULL, "bad stream fixture input file should open");
    if (input == NULL) {
        return;
    }

    fprintf(input, "time,value\n0,1000\n");
    fclose(input);

    snprintf(
        command,
        sizeof(command),
        "\"%s\" --sensor tsw10 < \"%s\" > \"%s\" 2>&1",
        stream_executable,
        input_path,
        output_path
    );
    expect_true(system(command) != 0, "stream CLI should reject an invalid header");

    remove(input_path);
    remove(output_path);
}

/*
 * Runs the stream CLI on `input` (written byte-for-byte) and captures stdout.
 * Returns the CLI's exit code, or -1 if it did not exit normally (a crash).
 */
static int run_stream_case(
    const char *stream_executable,
    const char *input,
    char *output,
    size_t output_size
)
{
    char input_path[256];
    char output_path[256];
    char error_path[256];
    char command[1024];
    FILE *file = NULL;
    size_t length = 0U;
    int status;

    snprintf(input_path, sizeof(input_path), "case_input_%ld.csv", (long)getpid());
    snprintf(output_path, sizeof(output_path), "case_output_%ld.csv", (long)getpid());
    snprintf(error_path, sizeof(error_path), "case_error_%ld.txt", (long)getpid());

    output[0] = '\0';
    file = fopen(input_path, "wb");
    if (file == NULL) {
        return 0;
    }
    fputs(input, file);
    fclose(file);

    snprintf(
        command,
        sizeof(command),
        "\"%s\" --sensor tsw10 --filter-window 1 < \"%s\" > \"%s\" 2> \"%s\"",
        stream_executable,
        input_path,
        output_path,
        error_path
    );
    status = system(command);

    file = fopen(output_path, "rb");
    if (file != NULL) {
        length = fread(output, 1U, output_size - 1U, file);
        fclose(file);
    }
    output[length] = '\0';

    remove(input_path);
    remove(output_path);
    remove(error_path);
    if ((status == -1) || !WIFEXITED(status)) {
        return -1;
    }
    return WEXITSTATUS(status);
}

static void expect_stream_accepts(
    const char *stream_executable,
    const char *input,
    const char *expected_substring,
    const char *message
)
{
    char output[4096];
    int exit_code = run_stream_case(stream_executable, input, output, sizeof(output));

    expect_true(exit_code == 0, message);
    expect_true(strstr(output, expected_substring) != NULL, message);
}

static void expect_stream_rejects(
    const char *stream_executable,
    const char *input,
    const char *message
)
{
    char output[4096];
    int exit_code = run_stream_case(stream_executable, input, output, sizeof(output));
    const char *first_row = strchr(output, '\n');

    /* Exactly 1: a clean rejection, not a crash. */
    expect_true(exit_code == 1, message);
    /* Nothing after the output header: a rejected input must not emit rows. */
    expect_true((first_row == NULL) || (first_row[1] == '\0'), message);
}

static void test_stream_input_contract(const char *stream_executable)
{
    char long_line[700];

    expect_stream_accepts(
        stream_executable,
        "timestamp_ms,raw_mv\r\n0,4195\r\n100,3452\r\n",
        "100,tsw10,3452.000,",
        "stream CLI should accept CRLF line endings"
    );
    expect_stream_accepts(
        stream_executable,
        "timestamp_ms,raw_mv\n100,3452",
        "100,tsw10,3452.000,",
        "stream CLI should accept a final row without a newline"
    );
    expect_stream_accepts(
        stream_executable,
        "timestamp_ms,raw_mv\n5000000000,3452\n",
        "5000000000,tsw10,3452.000,",
        "stream CLI should preserve timestamps above 2^32"
    );
    expect_stream_accepts(
        stream_executable,
        "timestamp_ms,sensor,raw_mv,filtered_mv,equivalent_mv,estimated_ntu,range_status\r\n"
        "100,tsw10,3452.000,3452.000,3452.000,500.304214,in_range\r\n",
        "100,tsw10,3452.000,",
        "stream CLI should read raw_mv by header name and ignore other named columns"
    );
    expect_stream_accepts(
        stream_executable,
        "raw_mv,timestamp_ms\n3452,100\n",
        "100,tsw10,3452.000,",
        "stream CLI should accept required columns in any order"
    );

    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n100,,3350\n",
        "stream CLI should reject an empty field"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,sensor,raw_mv\n100,,3452\n",
        "stream CLI should reject an empty field in an ignored column"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n100,3350,7\n",
        "stream CLI should reject a row with more fields than the header"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n100\n",
        "stream CLI should reject a row with fewer fields than the header"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv,note\n100,3452\n",
        "stream CLI should reject a row missing an ignored column"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n-5,3350\n",
        "stream CLI should reject a negative timestamp"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n99999999999999999999999,3350\n",
        "stream CLI should reject a timestamp that overflows"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n100, 3350\n",
        "stream CLI should reject whitespace inside a field"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n100,nan\n",
        "stream CLI should reject a non-finite raw_mv"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv\n\n",
        "stream CLI should reject a blank row"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,value\n100,3350\n",
        "stream CLI should reject a header without raw_mv"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,raw_mv,raw_mv\n100,3350,3350\n",
        "stream CLI should reject a duplicate header column"
    );
    expect_stream_rejects(
        stream_executable,
        "timestamp_ms,,raw_mv\n100,x,3350\n",
        "stream CLI should reject an empty header column"
    );

    snprintf(long_line, sizeof(long_line), "timestamp_ms,raw_mv\n1,%0600d\n", 5);
    expect_stream_rejects(
        stream_executable,
        long_line,
        "stream CLI should reject an over-long row without emitting a partial row"
    );
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "expected stream and calibrate executable paths\n");
        return EXIT_FAILURE;
    }

    test_calibration_cli(argv[2]);
    test_stream_cli(argv[1]);
    test_stream_rejects_bad_header(argv[1]);
    test_stream_input_contract(argv[1]);

    if (g_failures != 0) {
        fprintf(stderr, "Total failures: %d\n", g_failures);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
