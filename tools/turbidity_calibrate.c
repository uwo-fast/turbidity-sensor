#include "turbidity/turbidity.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct calibration_input {
    double ntu[3];
    double mv[3];
    size_t count;
} calibration_input;

static void print_usage(const char *program)
{
    fprintf(stderr,
        "Usage: %s --sensor tsw10|tst10 --point NTU,MV --point NTU,MV --point NTU,MV\n",
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

static int parse_point(const char *text, double *out_ntu, double *out_mv)
{
    char *end = NULL;
    double ntu;
    double mv;

    if ((text == NULL) || (out_ntu == NULL) || (out_mv == NULL)) {
        return -1;
    }

    ntu = strtod(text, &end);
    if ((end == text) || (*end != ',')) {
        return -1;
    }
    mv = strtod(end + 1, &end);
    if ((end == NULL) || (*end != '\0')) {
        return -1;
    }

    *out_ntu = ntu;
    *out_mv = mv;
    return 0;
}

int main(int argc, char **argv)
{
    turbidity_sensor_kind sensor = TURBIDITY_SENSOR_TSW10;
    turbidity_profile profile;
    calibration_input input = {{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, 0U};
    double rmse_mv = 0.0;
    double max_abs_error_mv = 0.0;
    int sensor_set = 0;
    int index;

    for (index = 1; index < argc; ++index) {
        if (strcmp(argv[index], "--sensor") == 0) {
            if ((index + 1 >= argc) || (parse_sensor(argv[index + 1], &sensor) != 0)) {
                print_usage(argv[0]);
                return 1;
            }
            sensor_set = 1;
            index += 1;
        } else if (strcmp(argv[index], "--point") == 0) {
            if ((index + 1 >= argc) || (input.count >= 3U) ||
                (parse_point(argv[index + 1], &input.ntu[input.count], &input.mv[input.count]) != 0)) {
                print_usage(argv[0]);
                return 1;
            }
            input.count += 1U;
            index += 1;
        } else if ((strcmp(argv[index], "--help") == 0) || (strcmp(argv[index], "-h") == 0)) {
            print_usage(argv[0]);
            return 0;
        } else {
            print_usage(argv[0]);
            return 1;
        }
    }

    if ((!sensor_set) || (input.count != 3U)) {
        print_usage(argv[0]);
        return 1;
    }

    if (turbidity_solve_profile_3point(sensor, input.ntu, input.mv, &profile, &rmse_mv, &max_abs_error_mv) != 0) {
        fprintf(stderr, "Failed to solve calibration profile.\n");
        return 1;
    }

    printf("sensor=%s\n", turbidity_sensor_name(profile.sensor_kind));
    printf("trim_t=%.9f\n", profile.trim_t);
    printf("gain=%.9f\n", profile.gain);
    printf("offset_mv=%.9f\n", profile.offset_mv);
    printf("filter_window=%u\n", (unsigned)profile.filter_window);
    printf("rmse_mv=%.9f\n", rmse_mv);
    printf("max_abs_error_mv=%.9f\n", max_abs_error_mv);
    return 0;
}
