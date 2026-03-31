#include "turbidity/turbidity.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int parse_output_row(
    const char *line,
    unsigned *timestamp_ms,
    char *sensor,
    size_t sensor_size,
    double *raw_mv,
    double *filtered_mv,
    double *estimated_ntu,
    char *status,
    size_t status_size
)
{
    return sscanf(
        line,
        "%u,%31[^,],%lf,%lf,%lf,%31s",
        timestamp_ms,
        sensor,
        raw_mv,
        filtered_mv,
        estimated_ntu,
        status
    ) == 6;
}

int main(int argc, char **argv)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    turbidity_context context;
    turbidity_sample samples[3];
    turbidity_result expected[3];
    char input_path[128];
    char output_path[128];
    char command[512];
    FILE *input = NULL;
    FILE *output = NULL;
    char line[256];
    size_t index;

    if (argc != 2) {
        fprintf(stderr, "Expected stream executable path.\n");
        return EXIT_FAILURE;
    }

    profile.trim_t = 0.25;
    profile.gain = 1.02;
    profile.offset_mv = -12.0;
    profile.filter_window = 2;

    samples[0].timestamp_ms = 100U;
    samples[1].timestamp_ms = 200U;
    samples[2].timestamp_ms = 300U;

    if ((turbidity_predict_measured_mv(&profile, 100.0, &samples[0].raw_mv) != 0) ||
        (turbidity_predict_measured_mv(&profile, 700.0, &samples[1].raw_mv) != 0) ||
        (turbidity_predict_measured_mv(&profile, 1500.0, &samples[2].raw_mv) != 0)) {
        fprintf(stderr, "Failed to build fixture data.\n");
        return EXIT_FAILURE;
    }

    snprintf(input_path, sizeof(input_path), "stream_input_%ld.csv", (long)getpid());
    snprintf(output_path, sizeof(output_path), "stream_output_%ld.csv", (long)getpid());

    input = fopen(input_path, "w");
    if (input == NULL) {
        perror("fopen input");
        return EXIT_FAILURE;
    }

    fprintf(input, "timestamp_ms,raw_mv\n");
    for (index = 0; index < 3U; ++index) {
        fprintf(input, "%u,%.6f\n", samples[index].timestamp_ms, samples[index].raw_mv);
    }
    fclose(input);
    input = NULL;

    snprintf(
        command,
        sizeof(command),
        "\"%s\" --sensor tsw10 --trim %.17g --gain %.17g --offset-mv %.17g --filter-window %u < \"%s\" > \"%s\"",
        argv[1],
        profile.trim_t,
        profile.gain,
        profile.offset_mv,
        (unsigned)profile.filter_window,
        input_path,
        output_path
    );

    if (system(command) != 0) {
        fprintf(stderr, "Stream app command failed: %s\n", command);
        remove(input_path);
        return EXIT_FAILURE;
    }

    turbidity_init(&context, &profile);
    for (index = 0; index < 3U; ++index) {
        if (turbidity_process_sample(&context, &samples[index], &expected[index]) != 0) {
            fprintf(stderr, "Failed to compute expected fixture row %zu\n", index);
            remove(input_path);
            remove(output_path);
            return EXIT_FAILURE;
        }
    }

    output = fopen(output_path, "r");
    if (output == NULL) {
        perror("fopen output");
        remove(input_path);
        remove(output_path);
        return EXIT_FAILURE;
    }

    if ((fgets(line, sizeof(line), output) == NULL) ||
        (strcmp(line, "timestamp_ms,sensor,raw_mv,filtered_mv,estimated_ntu,range_status\n") != 0)) {
        fprintf(stderr, "Unexpected output header: %s\n", line);
        fclose(output);
        remove(input_path);
        remove(output_path);
        return EXIT_FAILURE;
    }

    for (index = 0; index < 3U; ++index) {
        unsigned timestamp_ms = 0U;
        char sensor[32] = {0};
        char status[32] = {0};
        double raw_mv = 0.0;
        double filtered_mv = 0.0;
        double estimated_ntu = 0.0;

        if (fgets(line, sizeof(line), output) == NULL) {
            fprintf(stderr, "Missing output row %zu\n", index);
            fclose(output);
            remove(input_path);
            remove(output_path);
            return EXIT_FAILURE;
        }
        if (!parse_output_row(line, &timestamp_ms, sensor, sizeof(sensor), &raw_mv, &filtered_mv, &estimated_ntu, status, sizeof(status))) {
            fprintf(stderr, "Malformed output row %zu: %s\n", index, line);
            fclose(output);
            remove(input_path);
            remove(output_path);
            return EXIT_FAILURE;
        }
        if ((timestamp_ms != expected[index].timestamp_ms) ||
            (strcmp(sensor, "tsw10") != 0) ||
            (strcmp(status, turbidity_range_status_name(expected[index].range_status)) != 0) ||
            (fabs(raw_mv - expected[index].raw_mv) > 1e-3) ||
            (fabs(filtered_mv - expected[index].filtered_mv) > 1e-3) ||
            (fabs(estimated_ntu - expected[index].estimated_ntu) > 1e-3)) {
            fprintf(stderr, "Output row %zu did not match expected values.\n", index);
            fclose(output);
            remove(input_path);
            remove(output_path);
            return EXIT_FAILURE;
        }
    }

    fclose(output);
    remove(input_path);
    remove(output_path);
    return EXIT_SUCCESS;
}
