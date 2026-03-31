#include "turbidity/turbidity.h"
#include "moving_average.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_usage(const char *program)
{
    fprintf(
        stderr,
        "Usage: %s --sensor tsw10|tst10 [--trim T] [--gain G] [--offset-mv O] [--filter-window N]\n",
        program
    );
}

static turbidity_status parse_sensor(const char *text, turbidity_sensor_kind *out_sensor)
{
    if ((text == NULL) || (out_sensor == NULL)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }
    if (strcmp(text, "tsw10") == 0) {
        *out_sensor = TURBIDITY_SENSOR_TSW10;
        return TURBIDITY_STATUS_OK;
    }
    if (strcmp(text, "tst10") == 0) {
        *out_sensor = TURBIDITY_SENSOR_TST10;
        return TURBIDITY_STATUS_OK;
    }
    return TURBIDITY_STATUS_INVALID_SENSOR;
}

static turbidity_status parse_size(const char *text, size_t *out_value)
{
    char *end = NULL;
    unsigned long value;

    if ((text == NULL) || (out_value == NULL)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    value = strtoul(text, &end, 10);
    if ((end == text) || (*end != '\0') || (value == 0UL)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    *out_value = (size_t)value;
    return TURBIDITY_STATUS_OK;
}

static turbidity_status parse_double(const char *text, double *out_value)
{
    char *end = NULL;
    double value;

    if ((text == NULL) || (out_value == NULL)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    value = strtod(text, &end);
    if ((end == text) || (*end != '\0')) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    *out_value = value;
    return TURBIDITY_STATUS_OK;
}

static turbidity_status parse_row(
    const char *line,
    unsigned long line_number,
    unsigned int *out_timestamp_ms,
    double *out_raw_mv
)
{
    char buffer[256];
    char *first;
    char *second;
    char *end = NULL;
    unsigned long timestamp_ms;
    double raw_mv;

    if ((line == NULL) || (out_timestamp_ms == NULL) || (out_raw_mv == NULL)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }
    if (strlen(line) >= sizeof(buffer)) {
        fprintf(stderr, "line %lu is too long\n", line_number);
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    strcpy(buffer, line);
    first = strtok(buffer, ",");
    second = strtok(NULL, ",");
    if ((first == NULL) || (second == NULL) || (strtok(NULL, ",") != NULL)) {
        fprintf(stderr, "line %lu must have exactly two comma-separated columns\n", line_number);
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    while (isspace((unsigned char)*first)) {
        ++first;
    }
    while (isspace((unsigned char)*second)) {
        ++second;
    }

    timestamp_ms = strtoul(first, &end, 10);
    if ((end == first) || ((*end != '\0') && (*end != '\n'))) {
        fprintf(stderr, "line %lu has an invalid timestamp\n", line_number);
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    raw_mv = strtod(second, &end);
    if ((end == second) || ((*end != '\0') && (*end != '\n'))) {
        fprintf(stderr, "line %lu has an invalid raw_mv\n", line_number);
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    *out_timestamp_ms = (unsigned int)timestamp_ms;
    *out_raw_mv = raw_mv;
    return TURBIDITY_STATUS_OK;
}

int main(int argc, char **argv)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    moving_average_filter filter;
    double *filter_buffer = NULL;
    size_t filter_window = 8U;
    char line[256];
    unsigned long line_number = 0UL;
    int sensor_set = 0;
    int header_seen = 0;
    int index;

    for (index = 1; index < argc; ++index) {
        turbidity_status status = TURBIDITY_STATUS_OK;

        if (strcmp(argv[index], "--sensor") == 0) {
            if (index + 1 >= argc) {
                print_usage(argv[0]);
                return 1;
            }
            status = parse_sensor(argv[index + 1], &profile.sensor_kind);
            sensor_set = (status == TURBIDITY_STATUS_OK);
            index += 1;
        } else if (strcmp(argv[index], "--trim") == 0) {
            if (index + 1 >= argc) {
                print_usage(argv[0]);
                return 1;
            }
            status = parse_double(argv[index + 1], &profile.trim_t);
            index += 1;
        } else if (strcmp(argv[index], "--gain") == 0) {
            if (index + 1 >= argc) {
                print_usage(argv[0]);
                return 1;
            }
            status = parse_double(argv[index + 1], &profile.gain);
            index += 1;
        } else if (strcmp(argv[index], "--offset-mv") == 0) {
            if (index + 1 >= argc) {
                print_usage(argv[0]);
                return 1;
            }
            status = parse_double(argv[index + 1], &profile.offset_mv);
            index += 1;
        } else if (strcmp(argv[index], "--filter-window") == 0) {
            if (index + 1 >= argc) {
                print_usage(argv[0]);
                return 1;
            }
            status = parse_size(argv[index + 1], &filter_window);
            index += 1;
        } else if ((strcmp(argv[index], "--help") == 0) || (strcmp(argv[index], "-h") == 0)) {
            print_usage(argv[0]);
            return 0;
        } else {
            print_usage(argv[0]);
            return 1;
        }

        if (status != TURBIDITY_STATUS_OK) {
            fprintf(stderr, "argument error: %s\n", turbidity_status_name(status));
            return 1;
        }
    }

    if (!sensor_set) {
        print_usage(argv[0]);
        return 1;
    }
    if (turbidity_profile_validate(&profile) != TURBIDITY_STATUS_OK) {
        fprintf(stderr, "invalid profile\n");
        return 1;
    }

    filter_buffer = (double *)calloc(filter_window, sizeof(*filter_buffer));
    if (filter_buffer == NULL) {
        fprintf(stderr, "failed to allocate filter buffer\n");
        return 1;
    }

    moving_average_init(&filter, filter_buffer, filter_window);
    moving_average_reset(&filter);

    printf("timestamp_ms,sensor,raw_mv,filtered_mv,equivalent_mv,estimated_ntu,range_status\n");

    while (fgets(line, sizeof(line), stdin) != NULL) {
        turbidity_estimate estimate;
        turbidity_status status;
        unsigned int timestamp_ms;
        double raw_mv;
        double filtered_mv;

        line_number += 1UL;
        if (!header_seen) {
            if (strcmp(line, "timestamp_ms,raw_mv\n") != 0 && strcmp(line, "timestamp_ms,raw_mv") != 0) {
                fprintf(stderr, "line 1 must be the exact header: timestamp_ms,raw_mv\n");
                free(filter_buffer);
                return 1;
            }
            header_seen = 1;
            continue;
        }

        status = parse_row(line, line_number, &timestamp_ms, &raw_mv);
        if (status != TURBIDITY_STATUS_OK) {
            free(filter_buffer);
            return 1;
        }

        filtered_mv = moving_average_push(&filter, raw_mv);
        status = turbidity_estimate_ntu_from_mv(&profile, filtered_mv, &estimate);
        if (status != TURBIDITY_STATUS_OK) {
            fprintf(stderr, "line %lu estimate failed: %s\n", line_number, turbidity_status_name(status));
            free(filter_buffer);
            return 1;
        }

        printf(
            "%u,%s,%.3f,%.3f,%.3f,%.6f,%s\n",
            timestamp_ms,
            turbidity_sensor_name(profile.sensor_kind),
            raw_mv,
            filtered_mv,
            estimate.equivalent_mv,
            estimate.estimated_ntu,
            turbidity_range_status_name(estimate.range_status)
        );
    }

    if (!header_seen) {
        fprintf(stderr, "stdin is empty; expected a CSV header\n");
        free(filter_buffer);
        return 1;
    }

    free(filter_buffer);
    return 0;
}
