#ifndef TURBIDITY_TURBIDITY_H
#define TURBIDITY_TURBIDITY_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum turbidity_status {
    TURBIDITY_STATUS_OK = 0,
    TURBIDITY_STATUS_INVALID_ARGUMENT = 1,
    TURBIDITY_STATUS_INVALID_SENSOR = 2,
    TURBIDITY_STATUS_INVALID_PROFILE = 3,
    TURBIDITY_STATUS_NO_SOLUTION = 4
} turbidity_status;

typedef enum turbidity_sensor_kind {
    TURBIDITY_SENSOR_TSW10 = 0,
    TURBIDITY_SENSOR_TST10 = 1
} turbidity_sensor_kind;

typedef enum turbidity_range_status {
    TURBIDITY_RANGE_IN_RANGE = 0,
    TURBIDITY_RANGE_CLAMPED_LOW = 1,
    TURBIDITY_RANGE_CLAMPED_HIGH = 2
} turbidity_range_status;

typedef struct turbidity_profile {
    turbidity_sensor_kind sensor_kind;
    double trim_t;
    double gain;
    double offset_mv;
} turbidity_profile;

typedef struct turbidity_estimate {
    double equivalent_mv;
    double estimated_ntu;
    turbidity_range_status range_status;
} turbidity_estimate;

turbidity_profile turbidity_default_profile(turbidity_sensor_kind sensor_kind);

turbidity_status turbidity_profile_validate(const turbidity_profile *profile);
turbidity_status turbidity_sensor_max_ntu(
    turbidity_sensor_kind sensor_kind,
    double *out_max_ntu
);

turbidity_status turbidity_eval_family_mv(
    turbidity_sensor_kind sensor_kind,
    double trim_t,
    double ntu,
    double *out_mv
);

turbidity_status turbidity_predict_measured_mv(
    const turbidity_profile *profile,
    double ntu,
    double *out_mv
);

turbidity_status turbidity_estimate_ntu_from_mv(
    const turbidity_profile *profile,
    double measured_mv,
    turbidity_estimate *out_estimate
);

turbidity_status turbidity_solve_profile_3point(
    turbidity_sensor_kind sensor_kind,
    const double ntu[3],
    const double mv[3],
    turbidity_profile *out_profile,
    double *out_rmse_mv,
    double *out_max_abs_error_mv
);

const char *turbidity_sensor_name(turbidity_sensor_kind sensor_kind);
const char *turbidity_status_name(turbidity_status status);
const char *turbidity_range_status_name(turbidity_range_status status);

#ifdef __cplusplus
}
#endif

#endif
