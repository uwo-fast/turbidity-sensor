#include "turbidity/turbidity.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_usage(const char *program)
{
    fprintf(stderr,
        "Usage: %s --sensor tsw10|tst10 [--trim T] [--gain G] [--offset-mv O] [--filter-window N]\n",
        program);
}

static int parse_sensor(const char *text, turbidity_sensor_kind *out_sensor)
{
    if ((text == NULL) || (out_sensor == NULL)) {
        return -1;
    }
    if (strcmp(text, "tsw10") == 0) {
        *out_sensor = TURBIDITY_SENSOR_TSW10;
        return 0;
    }
    if (strcmp(text, "tst10") == 0) {
        *out_sensor = TURBIDITY_SENSOR_TST10;
        return 0;
    }
    return -1;
}

static int parse_u32(const char *text, uint32_t *out_value)
{
    char *end = NULL;
    unsigned long parsed;

    parsed = strtoul(text, &end, 10);
    if ((end == text) || (*end != '\0')) {
        return -1;
    }
    *out_value = (uint32_t)parsed;
    return 0;
}

static int parse_double(const char *text, double *out_value)
{
    char *end = NULL;
    double parsed = strtod(text, &end);

    if ((end == text) || (*end != '\0')) {
        return -1;
    }
    *out_value = parsed;
    return 0;
}

static int parse_input_line(const char *line, turbidity_sample *out_sample)
{
    char buffer[256];
    char *first;
    char *second;
    char *cursor;

    if ((line == NULL) || (out_sample == NULL)) {
        return -1;
    }

    while (isspace((unsigned char)*line)) {
        ++line;
    }
    if ((*line == '\0') || (*line == '#')) {
        return 1;
    }

    if (strlen(line) >= sizeof(buffer)) {
        return -1;
    }
    strcpy(buffer, line);

    cursor = strchr(buffer, '\n');
    if (cursor != NULL) {
        *cursor = '\0';
    }

    first = strtok(buffer, ",");
    second = strtok(NULL, ",");
    if ((first == NULL) || (second == NULL)) {
        return 1;
    }

    while (isspace((unsigned char)*first)) {
        ++first;
    }
    while (isspace((unsigned char)*second)) {
        ++second;
    }

    if (!isdigit((unsigned char)first[0])) {
        return 1;
    }

    if ((parse_u32(first, &out_sample->timestamp_ms) != 0) || (parse_double(second, &out_sample->raw_mv) != 0)) {
        return -1;
    }

    return 0;
}

int main(int argc, char **argv)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    turbidity_context context;
    char line[256];
    int sensor_set = 0;
    int index;

    for (index = 1; index < argc; ++index) {
        if (strcmp(argv[index], "--sensor") == 0) {
            if ((index + 1 >= argc) || (parse_sensor(argv[index + 1], &profile.sensor_kind) != 0)) {
                print_usage(argv[0]);
                return 1;
            }
            sensor_set = 1;
            index += 1;
        } else if (strcmp(argv[index], "--trim") == 0) {
            if ((index + 1 >= argc) || (parse_double(argv[index + 1], &profile.trim_t) != 0)) {
                print_usage(argv[0]);
                return 1;
            }
            index += 1;
        } else if (strcmp(argv[index], "--gain") == 0) {
            if ((index + 1 >= argc) || (parse_double(argv[index + 1], &profile.gain) != 0)) {
                print_usage(argv[0]);
                return 1;
            }
            index += 1;
        } else if (strcmp(argv[index], "--offset-mv") == 0) {
            if ((index + 1 >= argc) || (parse_double(argv[index + 1], &profile.offset_mv) != 0)) {
                print_usage(argv[0]);
                return 1;
            }
            index += 1;
        } else if (strcmp(argv[index], "--filter-window") == 0) {
            uint32_t parsed_window = 0U;
            if ((index + 1 >= argc) || (parse_u32(argv[index + 1], &parsed_window) != 0)) {
                print_usage(argv[0]);
                return 1;
            }
            profile.filter_window = (uint16_t)parsed_window;
            index += 1;
        } else if ((strcmp(argv[index], "--help") == 0) || (strcmp(argv[index], "-h") == 0)) {
            print_usage(argv[0]);
            return 0;
        } else {
            print_usage(argv[0]);
            return 1;
        }
    }

    if (!sensor_set || !turbidity_profile_validate(&profile)) {
        print_usage(argv[0]);
        return 1;
    }

    turbidity_init(&context, &profile);
    printf("timestamp_ms,sensor,raw_mv,filtered_mv,estimated_ntu,range_status\n");

    while (fgets(line, sizeof(line), stdin) != NULL) {
        turbidity_sample sample;
        turbidity_result result;
        int parse_status = parse_input_line(line, &sample);

        if (parse_status == 1) {
            continue;
        }
        if (parse_status != 0) {
            fprintf(stderr, "Failed to parse input line: %s", line);
            return 1;
        }
        if (turbidity_process_sample(&context, &sample, &result) != 0) {
            fprintf(stderr, "Failed to process sample at timestamp %u\n", sample.timestamp_ms);
            return 1;
        }

        printf(
            "%u,%s,%.3f,%.3f,%.6f,%s\n",
            result.timestamp_ms,
            turbidity_sensor_name(profile.sensor_kind),
            result.raw_mv,
            result.filtered_mv,
            result.estimated_ntu,
            turbidity_range_status_name(result.range_status)
        );
    }

    return 0;
}
