#ifndef TURBIDITY_TURBIDITY_H
#define TURBIDITY_TURBIDITY_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define TURBIDITY_MAX_FILTER_WINDOW 64U
#define TURBIDITY_DEFAULT_FILTER_WINDOW 8U

typedef enum turbidity_sensor_kind {
    TURBIDITY_SENSOR_TSW10 = 0,
    TURBIDITY_SENSOR_TST10 = 1
} turbidity_sensor_kind;

typedef enum turbidity_range_status {
    TURBIDITY_RANGE_IN_RANGE = 0,
    TURBIDITY_RANGE_CLAMPED_LOW = 1,
    TURBIDITY_RANGE_CLAMPED_HIGH = 2,
    TURBIDITY_RANGE_INVALID = 3
} turbidity_range_status;

typedef struct turbidity_profile {
    turbidity_sensor_kind sensor_kind;
    double trim_t;
    double gain;
    double offset_mv;
    uint16_t filter_window;
} turbidity_profile;

typedef struct turbidity_sample {
    uint32_t timestamp_ms;
    double raw_mv;
} turbidity_sample;

typedef struct turbidity_result {
    uint32_t timestamp_ms;
    double raw_mv;
    double filtered_mv;
    double estimated_ntu;
    turbidity_range_status range_status;
} turbidity_result;

typedef struct turbidity_context {
    turbidity_profile profile;
    double window_samples[TURBIDITY_MAX_FILTER_WINDOW];
    double sum_mv;
    uint16_t next_index;
    uint16_t sample_count;
} turbidity_context;

turbidity_profile turbidity_default_profile(turbidity_sensor_kind sensor_kind);
int turbidity_profile_validate(const turbidity_profile *profile);
void turbidity_init(turbidity_context *context, const turbidity_profile *profile);
void turbidity_reset(turbidity_context *context);

double turbidity_sensor_max_ntu(turbidity_sensor_kind sensor_kind);
const char *turbidity_sensor_name(turbidity_sensor_kind sensor_kind);
const char *turbidity_range_status_name(turbidity_range_status status);

int turbidity_eval_family_mv(
    turbidity_sensor_kind sensor_kind,
    double trim_t,
    double ntu,
    double *out_mv
);

int turbidity_predict_measured_mv(
    const turbidity_profile *profile,
    double ntu,
    double *out_mv
);

int turbidity_process_sample(
    turbidity_context *context,
    const turbidity_sample *sample,
    turbidity_result *out_result
);

int turbidity_solve_profile_3point(
    turbidity_sensor_kind sensor_kind,
    const double ntu[3],
    const double mv[3],
    turbidity_profile *out_profile,
    double *out_rmse_mv,
    double *out_max_abs_error_mv
);

#ifdef __cplusplus
}
#endif

#endif
