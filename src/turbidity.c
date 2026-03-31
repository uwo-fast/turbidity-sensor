#include "turbidity/turbidity.h"

#include <float.h>
#include <math.h>
#include <stddef.h>
#include <string.h>

typedef struct quadratic_coefficients {
    double a;
    double b;
    double c;
} quadratic_coefficients;

typedef struct turbidity_sensor_model {
    turbidity_sensor_kind sensor_kind;
    const char *name;
    double max_ntu;
    quadratic_coefficients low_mv;
    quadratic_coefficients high_mv;
} turbidity_sensor_model;

static const turbidity_sensor_model TURBIDITY_SENSOR_MODELS[] = {
    {
        TURBIDITY_SENSOR_TSW10,
        "tsw10",
        2000.0,
        {3.654358227585e-04, -1.599118398764e+00, 3.606403726708e+03},
        {3.391898719130e-04, -1.721756367203e+00, 4.782673066064e+03},
    },
    {
        TURBIDITY_SENSOR_TST10,
        "tst10",
        4000.0,
        {1.194702773120e-04, -1.147161597053e+00, 3.609305647841e+03},
        {1.204569820423e-04, -1.152056151166e+00, 4.401205574913e+03},
    },
};

static const turbidity_sensor_model *find_sensor_model(turbidity_sensor_kind sensor_kind)
{
    size_t index;

    for (index = 0; index < sizeof(TURBIDITY_SENSOR_MODELS) / sizeof(TURBIDITY_SENSOR_MODELS[0]); ++index) {
        if (TURBIDITY_SENSOR_MODELS[index].sensor_kind == sensor_kind) {
            return &TURBIDITY_SENSOR_MODELS[index];
        }
    }

    return NULL;
}

static double clamp_double(double value, double min_value, double max_value)
{
    if (value < min_value) {
        return min_value;
    }
    if (value > max_value) {
        return max_value;
    }
    return value;
}

static quadratic_coefficients interpolate_coefficients(
    const turbidity_sensor_model *model,
    double trim_t
)
{
    quadratic_coefficients coefficients;
    double t = clamp_double(trim_t, 0.0, 1.0);

    coefficients.a = model->low_mv.a + ((model->high_mv.a - model->low_mv.a) * t);
    coefficients.b = model->low_mv.b + ((model->high_mv.b - model->low_mv.b) * t);
    coefficients.c = model->low_mv.c + ((model->high_mv.c - model->low_mv.c) * t);
    return coefficients;
}

static double evaluate_quadratic(quadratic_coefficients coefficients, double ntu)
{
    return (coefficients.a * ntu * ntu) + (coefficients.b * ntu) + coefficients.c;
}

static int compute_ntu_from_equivalent_mv(
    const turbidity_profile *profile,
    double equivalent_mv,
    double *out_ntu,
    turbidity_range_status *out_status
)
{
    const turbidity_sensor_model *model = find_sensor_model(profile->sensor_kind);
    quadratic_coefficients coefficients;
    double max_mv;
    double min_mv;
    double discriminant;
    double denominator;
    double root1;
    double root2;
    double best_root = -1.0;

    if ((model == NULL) || (out_ntu == NULL) || (out_status == NULL)) {
        return -1;
    }

    coefficients = interpolate_coefficients(model, profile->trim_t);
    max_mv = evaluate_quadratic(coefficients, 0.0);
    min_mv = evaluate_quadratic(coefficients, model->max_ntu);

    if (equivalent_mv >= max_mv) {
        *out_ntu = 0.0;
        *out_status = TURBIDITY_RANGE_CLAMPED_LOW;
        return 0;
    }

    if (equivalent_mv <= min_mv) {
        *out_ntu = model->max_ntu;
        *out_status = TURBIDITY_RANGE_CLAMPED_HIGH;
        return 0;
    }

    coefficients.c -= equivalent_mv;

    if (fabs(coefficients.a) < 1e-12) {
        if (fabs(coefficients.b) < 1e-12) {
            return -1;
        }
        best_root = -coefficients.c / coefficients.b;
    } else {
        discriminant = (coefficients.b * coefficients.b) - (4.0 * coefficients.a * coefficients.c);
        if (discriminant < 0.0) {
            if (discriminant > -1e-6) {
                discriminant = 0.0;
            } else {
                return -1;
            }
        }

        denominator = 2.0 * coefficients.a;
        root1 = (-coefficients.b - sqrt(discriminant)) / denominator;
        root2 = (-coefficients.b + sqrt(discriminant)) / denominator;

        if ((root1 >= -1e-6) && (root1 <= (model->max_ntu + 1e-6))) {
            best_root = root1;
        }
        if ((root2 >= -1e-6) && (root2 <= (model->max_ntu + 1e-6)) && ((best_root < 0.0) || (root2 < best_root))) {
            best_root = root2;
        }
    }

    if (best_root < 0.0) {
        return -1;
    }

    *out_ntu = clamp_double(best_root, 0.0, model->max_ntu);
    *out_status = TURBIDITY_RANGE_IN_RANGE;
    return 0;
}

static double update_filter(turbidity_context *context, double raw_mv)
{
    uint16_t window = context->profile.filter_window;
    uint16_t slot;

    if (window == 0U) {
        window = 1U;
    }
    if (window > TURBIDITY_MAX_FILTER_WINDOW) {
        window = TURBIDITY_MAX_FILTER_WINDOW;
    }

    slot = context->next_index;
    if (context->sample_count < window) {
        context->window_samples[slot] = raw_mv;
        context->sum_mv += raw_mv;
        context->sample_count += 1U;
    } else {
        context->sum_mv -= context->window_samples[slot];
        context->window_samples[slot] = raw_mv;
        context->sum_mv += raw_mv;
    }

    context->next_index = (uint16_t)((slot + 1U) % window);
    return context->sum_mv / (double)context->sample_count;
}

static int solve_gain_offset(
    const double family_mv[3],
    const double measured_mv[3],
    double *out_gain,
    double *out_offset,
    double *out_sse,
    double *out_max_abs_error
)
{
    double sum_x = 0.0;
    double sum_y = 0.0;
    double sum_xx = 0.0;
    double sum_xy = 0.0;
    double denominator;
    double gain;
    double offset;
    double sse = 0.0;
    double max_abs = 0.0;
    size_t index;

    for (index = 0; index < 3U; ++index) {
        sum_x += family_mv[index];
        sum_y += measured_mv[index];
        sum_xx += family_mv[index] * family_mv[index];
        sum_xy += family_mv[index] * measured_mv[index];
    }

    denominator = (3.0 * sum_xx) - (sum_x * sum_x);
    if (fabs(denominator) < 1e-9) {
        return -1;
    }

    gain = ((3.0 * sum_xy) - (sum_x * sum_y)) / denominator;
    if (gain <= 0.0) {
        return -1;
    }

    offset = (sum_y - (gain * sum_x)) / 3.0;

    for (index = 0; index < 3U; ++index) {
        double residual = measured_mv[index] - ((gain * family_mv[index]) + offset);
        double abs_residual = fabs(residual);

        sse += residual * residual;
        if (abs_residual > max_abs) {
            max_abs = abs_residual;
        }
    }

    *out_gain = gain;
    *out_offset = offset;
    *out_sse = sse;
    *out_max_abs_error = max_abs;
    return 0;
}

turbidity_profile turbidity_default_profile(turbidity_sensor_kind sensor_kind)
{
    turbidity_profile profile;

    profile.sensor_kind = sensor_kind;
    profile.trim_t = 0.5;
    profile.gain = 1.0;
    profile.offset_mv = 0.0;
    profile.filter_window = TURBIDITY_DEFAULT_FILTER_WINDOW;
    return profile;
}

int turbidity_profile_validate(const turbidity_profile *profile)
{
    if ((profile == NULL) || (find_sensor_model(profile->sensor_kind) == NULL)) {
        return 0;
    }
    if ((profile->trim_t < 0.0) || (profile->trim_t > 1.0)) {
        return 0;
    }
    if (profile->gain <= 0.0) {
        return 0;
    }
    if ((profile->filter_window == 0U) || (profile->filter_window > TURBIDITY_MAX_FILTER_WINDOW)) {
        return 0;
    }
    return 1;
}

void turbidity_init(turbidity_context *context, const turbidity_profile *profile)
{
    if (context == NULL) {
        return;
    }

    memset(context, 0, sizeof(*context));
    if (profile != NULL) {
        context->profile = *profile;
    } else {
        context->profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    }
}

void turbidity_reset(turbidity_context *context)
{
    turbidity_profile profile;

    if (context == NULL) {
        return;
    }

    profile = context->profile;
    memset(context, 0, sizeof(*context));
    context->profile = profile;
}

double turbidity_sensor_max_ntu(turbidity_sensor_kind sensor_kind)
{
    const turbidity_sensor_model *model = find_sensor_model(sensor_kind);
    return (model != NULL) ? model->max_ntu : 0.0;
}

const char *turbidity_sensor_name(turbidity_sensor_kind sensor_kind)
{
    const turbidity_sensor_model *model = find_sensor_model(sensor_kind);
    return (model != NULL) ? model->name : "unknown";
}

const char *turbidity_range_status_name(turbidity_range_status status)
{
    switch (status) {
    case TURBIDITY_RANGE_IN_RANGE:
        return "in_range";
    case TURBIDITY_RANGE_CLAMPED_LOW:
        return "clamped_low";
    case TURBIDITY_RANGE_CLAMPED_HIGH:
        return "clamped_high";
    case TURBIDITY_RANGE_INVALID:
    default:
        return "invalid";
    }
}

int turbidity_eval_family_mv(
    turbidity_sensor_kind sensor_kind,
    double trim_t,
    double ntu,
    double *out_mv
)
{
    const turbidity_sensor_model *model = find_sensor_model(sensor_kind);
    quadratic_coefficients coefficients;

    if ((model == NULL) || (out_mv == NULL)) {
        return -1;
    }
    if ((trim_t < 0.0) || (trim_t > 1.0)) {
        return -1;
    }
    if ((ntu < 0.0) || (ntu > model->max_ntu)) {
        return -1;
    }

    coefficients = interpolate_coefficients(model, trim_t);
    *out_mv = evaluate_quadratic(coefficients, ntu);
    return 0;
}

int turbidity_predict_measured_mv(
    const turbidity_profile *profile,
    double ntu,
    double *out_mv
)
{
    double family_mv;

    if ((profile == NULL) || (out_mv == NULL) || !turbidity_profile_validate(profile)) {
        return -1;
    }
    if (turbidity_eval_family_mv(profile->sensor_kind, profile->trim_t, ntu, &family_mv) != 0) {
        return -1;
    }

    *out_mv = (profile->gain * family_mv) + profile->offset_mv;
    return 0;
}

int turbidity_process_sample(
    turbidity_context *context,
    const turbidity_sample *sample,
    turbidity_result *out_result
)
{
    double filtered_mv;
    double equivalent_mv;
    double estimated_ntu = 0.0;
    turbidity_range_status status = TURBIDITY_RANGE_INVALID;

    if ((context == NULL) || (sample == NULL) || (out_result == NULL)) {
        return -1;
    }

    out_result->timestamp_ms = sample->timestamp_ms;
    out_result->raw_mv = sample->raw_mv;
    out_result->filtered_mv = sample->raw_mv;
    out_result->estimated_ntu = 0.0;
    out_result->range_status = TURBIDITY_RANGE_INVALID;

    if (!turbidity_profile_validate(&context->profile)) {
        return -1;
    }

    filtered_mv = update_filter(context, sample->raw_mv);
    equivalent_mv = (filtered_mv - context->profile.offset_mv) / context->profile.gain;

    if (compute_ntu_from_equivalent_mv(&context->profile, equivalent_mv, &estimated_ntu, &status) != 0) {
        return -1;
    }

    out_result->filtered_mv = filtered_mv;
    out_result->estimated_ntu = estimated_ntu;
    out_result->range_status = status;
    return 0;
}

int turbidity_solve_profile_3point(
    turbidity_sensor_kind sensor_kind,
    const double ntu[3],
    const double mv[3],
    turbidity_profile *out_profile,
    double *out_rmse_mv,
    double *out_max_abs_error_mv
)
{
    const turbidity_sensor_model *model = find_sensor_model(sensor_kind);
    double left = 0.0;
    double right = 1.0;
    double best_t = 0.5;
    double best_gain = 1.0;
    double best_offset = 0.0;
    double best_sse = DBL_MAX;
    double best_max_abs = DBL_MAX;
    size_t pass_index;
    size_t point_index;

    if ((model == NULL) || (ntu == NULL) || (mv == NULL) || (out_profile == NULL)) {
        return -1;
    }

    for (point_index = 0; point_index < 3U; ++point_index) {
        if ((ntu[point_index] < 0.0) || (ntu[point_index] > model->max_ntu)) {
            return -1;
        }
    }

    for (pass_index = 0; pass_index < 3U; ++pass_index) {
        double step = (right - left) / 1000.0;
        size_t grid_index;

        if (step <= 0.0) {
            break;
        }

        for (grid_index = 0; grid_index <= 1000U; ++grid_index) {
            double t = left + (step * (double)grid_index);
            double family_mv[3];
            double gain;
            double offset;
            double sse;
            double max_abs;
            int valid = 1;

            for (point_index = 0; point_index < 3U; ++point_index) {
                if (turbidity_eval_family_mv(sensor_kind, t, ntu[point_index], &family_mv[point_index]) != 0) {
                    valid = 0;
                    break;
                }
            }
            if (!valid) {
                continue;
            }
            if (solve_gain_offset(family_mv, mv, &gain, &offset, &sse, &max_abs) != 0) {
                continue;
            }

            if (sse < best_sse) {
                best_t = t;
                best_gain = gain;
                best_offset = offset;
                best_sse = sse;
                best_max_abs = max_abs;
            }
        }

        left = clamp_double(best_t - step, 0.0, 1.0);
        right = clamp_double(best_t + step, 0.0, 1.0);
    }

    if (best_sse == DBL_MAX) {
        return -1;
    }

    *out_profile = turbidity_default_profile(sensor_kind);
    out_profile->trim_t = best_t;
    out_profile->gain = best_gain;
    out_profile->offset_mv = best_offset;

    if (out_rmse_mv != NULL) {
        *out_rmse_mv = sqrt(best_sse / 3.0);
    }
    if (out_max_abs_error_mv != NULL) {
        *out_max_abs_error_mv = best_max_abs;
    }
    return 0;
}
