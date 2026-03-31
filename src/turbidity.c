#include "turbidity/turbidity.h"

#include <float.h>
#include <math.h>
#include <stddef.h>

#include "turbidity_model_data.generated.h"

static const turbidity_model_record *find_model(turbidity_sensor_kind sensor_kind)
{
    size_t index;

    for (index = 0; index < TURBIDITY_MODEL_RECORD_COUNT; ++index) {
        if (TURBIDITY_MODEL_RECORDS[index].sensor_kind == sensor_kind) {
            return &TURBIDITY_MODEL_RECORDS[index];
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

static int is_finite_double(double value)
{
    return isfinite(value) ? 1 : 0;
}

static turbidity_quadratic interpolate_curve(
    const turbidity_model_record *model,
    double trim_t
)
{
    turbidity_quadratic curve;
    double t = clamp_double(trim_t, 0.0, 1.0);

    curve.a_mv_per_ntu2 = model->low_curve.a_mv_per_ntu2 +
        ((model->high_curve.a_mv_per_ntu2 - model->low_curve.a_mv_per_ntu2) * t);
    curve.b_mv_per_ntu = model->low_curve.b_mv_per_ntu +
        ((model->high_curve.b_mv_per_ntu - model->low_curve.b_mv_per_ntu) * t);
    curve.c_mv = model->low_curve.c_mv +
        ((model->high_curve.c_mv - model->low_curve.c_mv) * t);
    return curve;
}

static double evaluate_curve(turbidity_quadratic curve, double ntu)
{
    return (curve.a_mv_per_ntu2 * ntu * ntu) + (curve.b_mv_per_ntu * ntu) + curve.c_mv;
}

static turbidity_status solve_gain_offset(
    const double family_mv[3],
    const double measured_mv[3],
    double *out_gain,
    double *out_offset_mv,
    double *out_sse,
    double *out_max_abs_error_mv
)
{
    double sum_x = 0.0;
    double sum_y = 0.0;
    double sum_xx = 0.0;
    double sum_xy = 0.0;
    double denominator;
    double gain;
    double offset_mv;
    double sse = 0.0;
    double max_abs_error_mv = 0.0;
    size_t index;

    for (index = 0; index < 3U; ++index) {
        sum_x += family_mv[index];
        sum_y += measured_mv[index];
        sum_xx += family_mv[index] * family_mv[index];
        sum_xy += family_mv[index] * measured_mv[index];
    }

    denominator = (3.0 * sum_xx) - (sum_x * sum_x);
    if (fabs(denominator) < 1e-9) {
        return TURBIDITY_STATUS_NO_SOLUTION;
    }

    gain = ((3.0 * sum_xy) - (sum_x * sum_y)) / denominator;
    if ((!is_finite_double(gain)) || (gain <= 0.0)) {
        return TURBIDITY_STATUS_NO_SOLUTION;
    }

    offset_mv = (sum_y - (gain * sum_x)) / 3.0;
    if (!is_finite_double(offset_mv)) {
        return TURBIDITY_STATUS_NO_SOLUTION;
    }

    for (index = 0; index < 3U; ++index) {
        double residual = measured_mv[index] - ((gain * family_mv[index]) + offset_mv);
        double abs_residual = fabs(residual);

        sse += residual * residual;
        if (abs_residual > max_abs_error_mv) {
            max_abs_error_mv = abs_residual;
        }
    }

    *out_gain = gain;
    *out_offset_mv = offset_mv;
    *out_sse = sse;
    *out_max_abs_error_mv = max_abs_error_mv;
    return TURBIDITY_STATUS_OK;
}

turbidity_profile turbidity_default_profile(turbidity_sensor_kind sensor_kind)
{
    turbidity_profile profile;

    profile.sensor_kind = sensor_kind;
    profile.trim_t = 0.5;
    profile.gain = 1.0;
    profile.offset_mv = 0.0;
    return profile;
}

turbidity_status turbidity_profile_validate(const turbidity_profile *profile)
{
    if (profile == NULL) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }
    if (find_model(profile->sensor_kind) == NULL) {
        return TURBIDITY_STATUS_INVALID_SENSOR;
    }
    if ((!is_finite_double(profile->trim_t)) || (profile->trim_t < 0.0) || (profile->trim_t > 1.0)) {
        return TURBIDITY_STATUS_INVALID_PROFILE;
    }
    if ((!is_finite_double(profile->gain)) || (profile->gain <= 0.0)) {
        return TURBIDITY_STATUS_INVALID_PROFILE;
    }
    if (!is_finite_double(profile->offset_mv)) {
        return TURBIDITY_STATUS_INVALID_PROFILE;
    }
    return TURBIDITY_STATUS_OK;
}

turbidity_status turbidity_sensor_max_ntu(
    turbidity_sensor_kind sensor_kind,
    double *out_max_ntu
)
{
    const turbidity_model_record *model = find_model(sensor_kind);

    if (out_max_ntu == NULL) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }
    if (model == NULL) {
        return TURBIDITY_STATUS_INVALID_SENSOR;
    }

    *out_max_ntu = model->max_ntu;
    return TURBIDITY_STATUS_OK;
}

turbidity_status turbidity_eval_family_mv(
    turbidity_sensor_kind sensor_kind,
    double trim_t,
    double ntu,
    double *out_mv
)
{
    const turbidity_model_record *model = find_model(sensor_kind);
    turbidity_quadratic curve;

    if (out_mv == NULL) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }
    if (model == NULL) {
        return TURBIDITY_STATUS_INVALID_SENSOR;
    }
    if ((!is_finite_double(trim_t)) || (trim_t < 0.0) || (trim_t > 1.0) ||
        (!is_finite_double(ntu)) || (ntu < 0.0) || (ntu > model->max_ntu)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    curve = interpolate_curve(model, trim_t);
    *out_mv = evaluate_curve(curve, ntu);
    return TURBIDITY_STATUS_OK;
}

turbidity_status turbidity_predict_measured_mv(
    const turbidity_profile *profile,
    double ntu,
    double *out_mv
)
{
    double family_mv;
    turbidity_status status;

    if (out_mv == NULL) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    status = turbidity_profile_validate(profile);
    if (status != TURBIDITY_STATUS_OK) {
        return status;
    }

    status = turbidity_eval_family_mv(profile->sensor_kind, profile->trim_t, ntu, &family_mv);
    if (status != TURBIDITY_STATUS_OK) {
        return status;
    }

    *out_mv = (profile->gain * family_mv) + profile->offset_mv;
    return TURBIDITY_STATUS_OK;
}

turbidity_status turbidity_estimate_ntu_from_mv(
    const turbidity_profile *profile,
    double measured_mv,
    turbidity_estimate *out_estimate
)
{
    const turbidity_model_record *model;
    turbidity_quadratic curve;
    double max_mv;
    double min_mv;
    double discriminant;
    double denominator;
    double root1;
    double root2;
    double best_root = -1.0;
    double equivalent_mv;
    turbidity_status status;

    if ((out_estimate == NULL) || (!is_finite_double(measured_mv))) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }

    status = turbidity_profile_validate(profile);
    if (status != TURBIDITY_STATUS_OK) {
        return status;
    }

    model = find_model(profile->sensor_kind);
    if (model == NULL) {
        return TURBIDITY_STATUS_INVALID_SENSOR;
    }

    curve = interpolate_curve(model, profile->trim_t);
    equivalent_mv = (measured_mv - profile->offset_mv) / profile->gain;
    max_mv = evaluate_curve(curve, 0.0);
    min_mv = evaluate_curve(curve, model->max_ntu);

    out_estimate->equivalent_mv = equivalent_mv;

    if (equivalent_mv >= max_mv) {
        out_estimate->estimated_ntu = 0.0;
        out_estimate->range_status = TURBIDITY_RANGE_CLAMPED_LOW;
        return TURBIDITY_STATUS_OK;
    }

    if (equivalent_mv <= min_mv) {
        out_estimate->estimated_ntu = model->max_ntu;
        out_estimate->range_status = TURBIDITY_RANGE_CLAMPED_HIGH;
        return TURBIDITY_STATUS_OK;
    }

    curve.c_mv -= equivalent_mv;

    if (fabs(curve.a_mv_per_ntu2) < 1e-12) {
        if (fabs(curve.b_mv_per_ntu) < 1e-12) {
            return TURBIDITY_STATUS_NO_SOLUTION;
        }
        best_root = -curve.c_mv / curve.b_mv_per_ntu;
    } else {
        discriminant = (curve.b_mv_per_ntu * curve.b_mv_per_ntu) -
            (4.0 * curve.a_mv_per_ntu2 * curve.c_mv);
        if (discriminant < 0.0) {
            if (discriminant > -1e-6) {
                discriminant = 0.0;
            } else {
                return TURBIDITY_STATUS_NO_SOLUTION;
            }
        }

        denominator = 2.0 * curve.a_mv_per_ntu2;
        root1 = (-curve.b_mv_per_ntu - sqrt(discriminant)) / denominator;
        root2 = (-curve.b_mv_per_ntu + sqrt(discriminant)) / denominator;

        if ((root1 >= -1e-6) && (root1 <= (model->max_ntu + 1e-6))) {
            best_root = root1;
        }
        if ((root2 >= -1e-6) && (root2 <= (model->max_ntu + 1e-6)) &&
            ((best_root < 0.0) || (root2 < best_root))) {
            best_root = root2;
        }
    }

    if ((!is_finite_double(best_root)) || (best_root < 0.0)) {
        return TURBIDITY_STATUS_NO_SOLUTION;
    }

    out_estimate->estimated_ntu = clamp_double(best_root, 0.0, model->max_ntu);
    out_estimate->range_status = TURBIDITY_RANGE_IN_RANGE;
    return TURBIDITY_STATUS_OK;
}

turbidity_status turbidity_solve_profile_3point(
    turbidity_sensor_kind sensor_kind,
    const double ntu[3],
    const double mv[3],
    turbidity_profile *out_profile,
    double *out_rmse_mv,
    double *out_max_abs_error_mv
)
{
    const turbidity_model_record *model = find_model(sensor_kind);
    double left = 0.0;
    double right = 1.0;
    double best_trim_t = 0.5;
    double best_gain = 1.0;
    double best_offset_mv = 0.0;
    double best_sse = DBL_MAX;
    double best_max_abs_error_mv = DBL_MAX;
    size_t pass_index;
    size_t point_index;

    if ((ntu == NULL) || (mv == NULL) || (out_profile == NULL)) {
        return TURBIDITY_STATUS_INVALID_ARGUMENT;
    }
    if (model == NULL) {
        return TURBIDITY_STATUS_INVALID_SENSOR;
    }

    for (point_index = 0; point_index < 3U; ++point_index) {
        if ((!is_finite_double(ntu[point_index])) || (!is_finite_double(mv[point_index])) ||
            (ntu[point_index] < 0.0) || (ntu[point_index] > model->max_ntu)) {
            return TURBIDITY_STATUS_INVALID_ARGUMENT;
        }
    }

    for (pass_index = 0; pass_index < 4U; ++pass_index) {
        double step = (right - left) / 1000.0;
        size_t grid_index;

        if (step <= 0.0) {
            break;
        }

        for (grid_index = 0; grid_index <= 1000U; ++grid_index) {
            double trim_t = left + (step * (double)grid_index);
            double family_mv[3];
            double gain;
            double offset_mv;
            double sse;
            double max_abs_error_mv;
            turbidity_status status;

            for (point_index = 0; point_index < 3U; ++point_index) {
                status = turbidity_eval_family_mv(sensor_kind, trim_t, ntu[point_index], &family_mv[point_index]);
                if (status != TURBIDITY_STATUS_OK) {
                    break;
                }
            }
            if (point_index != 3U) {
                continue;
            }

            status = solve_gain_offset(
                family_mv,
                mv,
                &gain,
                &offset_mv,
                &sse,
                &max_abs_error_mv
            );
            if (status != TURBIDITY_STATUS_OK) {
                continue;
            }

            if (sse < best_sse) {
                best_trim_t = trim_t;
                best_gain = gain;
                best_offset_mv = offset_mv;
                best_sse = sse;
                best_max_abs_error_mv = max_abs_error_mv;
            }
        }

        left = clamp_double(best_trim_t - step, 0.0, 1.0);
        right = clamp_double(best_trim_t + step, 0.0, 1.0);
    }

    if (best_sse == DBL_MAX) {
        return TURBIDITY_STATUS_NO_SOLUTION;
    }

    *out_profile = turbidity_default_profile(sensor_kind);
    out_profile->trim_t = best_trim_t;
    out_profile->gain = best_gain;
    out_profile->offset_mv = best_offset_mv;

    if (out_rmse_mv != NULL) {
        *out_rmse_mv = sqrt(best_sse / 3.0);
    }
    if (out_max_abs_error_mv != NULL) {
        *out_max_abs_error_mv = best_max_abs_error_mv;
    }
    return TURBIDITY_STATUS_OK;
}

const char *turbidity_sensor_name(turbidity_sensor_kind sensor_kind)
{
    const turbidity_model_record *model = find_model(sensor_kind);
    return (model != NULL) ? model->name : "unknown";
}

const char *turbidity_status_name(turbidity_status status)
{
    switch (status) {
    case TURBIDITY_STATUS_OK:
        return "ok";
    case TURBIDITY_STATUS_INVALID_ARGUMENT:
        return "invalid_argument";
    case TURBIDITY_STATUS_INVALID_SENSOR:
        return "invalid_sensor";
    case TURBIDITY_STATUS_INVALID_PROFILE:
        return "invalid_profile";
    case TURBIDITY_STATUS_NO_SOLUTION:
    default:
        return "no_solution";
    }
}

const char *turbidity_range_status_name(turbidity_range_status status)
{
    switch (status) {
    case TURBIDITY_RANGE_IN_RANGE:
        return "in_range";
    case TURBIDITY_RANGE_CLAMPED_LOW:
        return "clamped_low";
    case TURBIDITY_RANGE_CLAMPED_HIGH:
    default:
        return "clamped_high";
    }
}
