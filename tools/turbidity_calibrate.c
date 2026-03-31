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
    fprintf(
        stderr,
        "Usage: %s --sensor tsw10|tst10 --point NTU,MV --point NTU,MV --point NTU,MV\n",
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

static turbidity_status parse_point(const char *text, double *out_ntu, double *out_mv)
{
    char *end = NULL;
    double ntu;
    double mv;

    if ((text == NULL) || (out_ntu == NULL) || (out_mv == NULL)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    ntu = strtod(text, &end);
    if ((end == text) || (*end != ',')) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    mv = strtod(end + 1, &end);
    if ((end == NULL) || (*end != '\0')) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    *out_ntu = ntu;
    *out_mv = mv;
    return TURBIDITY_STATUS_OK;
}

int main(int argc, char **argv)
{
    turbidity_sensor_kind sensor_kind = TURBIDITY_SENSOR_TSW10;
    calibration_input input = {{0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, 0U};
    turbidity_profile profile;
    turbidity_status status = TURBIDITY_STATUS_OK;
    double rmse_mv = 0.0;
    double max_abs_error_mv = 0.0;
    int sensor_set = 0;
    int index;

    for (index = 1; index < argc; ++index) {
        if (strcmp(argv[index], "--sensor") == 0) {
            if (index + 1 >= argc) {
                print_usage(argv[0]);
                return 1;
            }
            status = parse_sensor(argv[index + 1], &sensor_kind);
            if (status != TURBIDITY_STATUS_OK) {
                fprintf(stderr, "invalid sensor: %s\n", argv[index + 1]);
                return 1;
            }
            sensor_set = 1;
            index += 1;
        } else if (strcmp(argv[index], "--point") == 0) {
            if ((index + 1 >= argc) || (input.count >= 3U)) {
                print_usage(argv[0]);
                return 1;
            }
            status = parse_point(argv[index + 1], &input.ntu[input.count], &input.mv[input.count]);
            if (status != TURBIDITY_STATUS_OK) {
                fprintf(stderr, "invalid point: %s\n", argv[index + 1]);
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

    status = turbidity_solve_profile_3point(
        sensor_kind,
        input.ntu,
        input.mv,
        &profile,
        &rmse_mv,
        &max_abs_error_mv
    );
    if (status != TURBIDITY_STATUS_OK) {
        fprintf(stderr, "calibration solve failed: %s\n", turbidity_status_name(status));
        return 1;
    }

    printf(
        "{\"sensor\":\"%s\",\"trim_t\":%.9f,\"gain\":%.9f,\"offset_mv\":%.9f,\"rmse_mv\":%.9f,\"max_abs_error_mv\":%.9f}\n",
        turbidity_sensor_name(profile.sensor_kind),
        profile.trim_t,
        profile.gain,
        profile.offset_mv,
        rmse_mv,
        max_abs_error_mv
    );
    return 0;
}
