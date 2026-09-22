#include "turbidity/turbidity.h"
#include "moving_average.h"

#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STREAM_MAX_LINE 512U
#define STREAM_MAX_COLUMNS 16U

typedef struct stream_columns {
    size_t count;
    size_t timestamp_index;
    size_t raw_mv_index;
} stream_columns;

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

/*
 * Reads one line into `buffer` without its line ending (LF or CRLF).
 * Returns 1 for a line, 0 at end of input, and -1 when the line does not fit.
 * A final line without a newline is accepted.
 */
static int read_line(FILE *stream, char *buffer, size_t size)
{
    size_t length;

    if (fgets(buffer, (int)size, stream) == NULL) {
        return 0;
    }

    length = strlen(buffer);
    if ((length > 0U) && (buffer[length - 1U] == '\n')) {
        buffer[--length] = '\0';
    } else if (!feof(stream)) {
        return -1;
    }
    if ((length > 0U) && (buffer[length - 1U] == '\r')) {
        buffer[length - 1U] = '\0';
    }
    return 1;
}

/*
 * Splits `line` in place at every comma. Empty fields are kept so the caller
 * can reject them. Returns the field count, or `max_fields + 1` on overflow.
 */
static size_t split_fields(char *line, char **fields, size_t max_fields)
{
    size_t count = 0U;
    char *cursor = line;

    for (;;) {
        char *comma = strchr(cursor, ',');

        if (count == max_fields) {
            return max_fields + 1U;
        }
        fields[count++] = cursor;
        if (comma == NULL) {
            return count;
        }
        *comma = '\0';
        cursor = comma + 1;
    }
}

static int parse_header(char *line, stream_columns *out_columns)
{
    char *fields[STREAM_MAX_COLUMNS];
    size_t count = split_fields(line, fields, STREAM_MAX_COLUMNS);
    size_t index;
    size_t other;
    int has_timestamp = 0;
    int has_raw_mv = 0;

    if (count > STREAM_MAX_COLUMNS) {
        fprintf(stderr, "line 1 has more than %u columns\n", STREAM_MAX_COLUMNS);
        return 0;
    }

    for (index = 0U; index < count; ++index) {
        if (fields[index][0] == '\0') {
            fprintf(stderr, "line 1 has an empty column name\n");
            return 0;
        }
        for (other = 0U; other < index; ++other) {
            if (strcmp(fields[index], fields[other]) == 0) {
                fprintf(stderr, "line 1 repeats column %s\n", fields[index]);
                return 0;
            }
        }
        if (strcmp(fields[index], "timestamp_ms") == 0) {
            out_columns->timestamp_index = index;
            has_timestamp = 1;
        } else if (strcmp(fields[index], "raw_mv") == 0) {
            out_columns->raw_mv_index = index;
            has_raw_mv = 1;
        }
    }

    if ((!has_timestamp) || (!has_raw_mv)) {
        fprintf(stderr, "line 1 must be a header with timestamp_ms and raw_mv columns\n");
        return 0;
    }

    out_columns->count = count;
    return 1;
}

static int parse_timestamp(const char *text, unsigned long long *out_value)
{
    char *end = NULL;
    unsigned long long value;

    if (!isdigit((unsigned char)text[0])) {
        return 0;
    }

    errno = 0;
    value = strtoull(text, &end, 10);
    if ((errno == ERANGE) || (*end != '\0')) {
        return 0;
    }

    *out_value = value;
    return 1;
}

static int parse_raw_mv(const char *text, double *out_value)
{
    char *end = NULL;
    double value;

    if (isspace((unsigned char)text[0])) {
        return 0;
    }

    value = strtod(text, &end);
    if ((end == text) || (*end != '\0')) {
        return 0;
    }

    *out_value = value;
    return 1;
}

static int parse_row(
    char *line,
    unsigned long line_number,
    const stream_columns *columns,
    unsigned long long *out_timestamp_ms,
    double *out_raw_mv
)
{
    char *fields[STREAM_MAX_COLUMNS];
    size_t count = split_fields(line, fields, STREAM_MAX_COLUMNS);
    size_t index;

    if (count != columns->count) {
        fprintf(stderr, "line %lu has %lu fields; the header has %lu\n", line_number, (unsigned long)count, (unsigned long)columns->count);
        return 0;
    }
    for (index = 0U; index < count; ++index) {
        if (fields[index][0] == '\0') {
            fprintf(stderr, "line %lu has an empty field in column %lu\n", line_number, (unsigned long)(index + 1U));
            return 0;
        }
    }
    if (!parse_timestamp(fields[columns->timestamp_index], out_timestamp_ms)) {
        fprintf(stderr, "line %lu has an invalid timestamp_ms\n", line_number);
        return 0;
    }
    if (!parse_raw_mv(fields[columns->raw_mv_index], out_raw_mv)) {
        fprintf(stderr, "line %lu has an invalid raw_mv\n", line_number);
        return 0;
    }
    return 1;
}

int main(int argc, char **argv)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    moving_average_filter filter;
    stream_columns columns = {0U, 0U, 0U};
    double *filter_buffer = NULL;
    size_t filter_window = 8U;
    char line[STREAM_MAX_LINE];
    unsigned long line_number = 0UL;
    int sensor_set = 0;
    int header_seen = 0;
    int read_status;
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

    while ((read_status = read_line(stdin, line, sizeof(line))) != 0) {
        turbidity_estimate estimate;
        turbidity_status status;
        unsigned long long timestamp_ms;
        double raw_mv;
        double filtered_mv;

        line_number += 1UL;
        if (read_status < 0) {
            fprintf(stderr, "line %lu is longer than %u characters\n", line_number, STREAM_MAX_LINE - 2U);
            free(filter_buffer);
            return 1;
        }

        if (!header_seen) {
            if (!parse_header(line, &columns)) {
                free(filter_buffer);
                return 1;
            }
            header_seen = 1;
            continue;
        }

        if (!parse_row(line, line_number, &columns, &timestamp_ms, &raw_mv)) {
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
            "%llu,%s,%.3f,%.3f,%.3f,%.6f,%s\n",
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
