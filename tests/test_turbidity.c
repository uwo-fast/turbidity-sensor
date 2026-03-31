#include "turbidity/turbidity.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static int g_failures = 0;

static void expect_true(int condition, const char *message)
{
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        g_failures += 1;
    }
}

static void expect_close(double actual, double expected, double tolerance, const char *message)
{
    if (fabs(actual - expected) > tolerance) {
        fprintf(stderr, "FAIL: %s (actual=%.12f expected=%.12f tolerance=%.12f)\n", message, actual, expected, tolerance);
        g_failures += 1;
    }
}

static double vendor_curve_mv(turbidity_sensor_kind sensor, int high_curve, double ntu)
{
    double a;
    double b;
    double c;

    if (sensor == TURBIDITY_SENSOR_TSW10) {
        if (high_curve) {
            a = 3.391898719130e-04;
            b = -1.721756367203e+00;
            c = 4.782673066064e+03;
        } else {
            a = 3.654358227585e-04;
            b = -1.599118398764e+00;
            c = 3.606403726708e+03;
        }
    } else {
        if (high_curve) {
            a = 1.204569820423e-04;
            b = -1.152056151166e+00;
            c = 4.401205574913e+03;
        } else {
            a = 1.194702773120e-04;
            b = -1.147161597053e+00;
            c = 3.609305647841e+03;
        }
    }

    return (a * ntu * ntu) + (b * ntu) + c;
}

static void test_endpoint_family_matches_vendor_fits(void)
{
    double low_mv = 0.0;
    double high_mv = 0.0;
    double mid_mv = 0.0;
    double ntu = 1000.0;

    expect_true(turbidity_eval_family_mv(TURBIDITY_SENSOR_TSW10, 0.0, ntu, &low_mv) == 0, "TSW low curve should evaluate");
    expect_true(turbidity_eval_family_mv(TURBIDITY_SENSOR_TSW10, 1.0, ntu, &high_mv) == 0, "TSW high curve should evaluate");
    expect_true(turbidity_eval_family_mv(TURBIDITY_SENSOR_TSW10, 0.5, ntu, &mid_mv) == 0, "TSW midpoint curve should evaluate");
    expect_close(low_mv, vendor_curve_mv(TURBIDITY_SENSOR_TSW10, 0, ntu), 1e-6, "TSW low endpoint matches vendor fit");
    expect_close(high_mv, vendor_curve_mv(TURBIDITY_SENSOR_TSW10, 1, ntu), 1e-6, "TSW high endpoint matches vendor fit");
    expect_close(mid_mv, (low_mv + high_mv) / 2.0, 1e-6, "TSW midpoint is linear blend");

    ntu = 2000.0;
    expect_true(turbidity_eval_family_mv(TURBIDITY_SENSOR_TST10, 0.0, ntu, &low_mv) == 0, "TST low curve should evaluate");
    expect_true(turbidity_eval_family_mv(TURBIDITY_SENSOR_TST10, 1.0, ntu, &high_mv) == 0, "TST high curve should evaluate");
    expect_true(turbidity_eval_family_mv(TURBIDITY_SENSOR_TST10, 0.5, ntu, &mid_mv) == 0, "TST midpoint curve should evaluate");
    expect_close(low_mv, vendor_curve_mv(TURBIDITY_SENSOR_TST10, 0, ntu), 1e-6, "TST low endpoint matches vendor fit");
    expect_close(high_mv, vendor_curve_mv(TURBIDITY_SENSOR_TST10, 1, ntu), 1e-6, "TST high endpoint matches vendor fit");
    expect_close(mid_mv, (low_mv + high_mv) / 2.0, 1e-6, "TST midpoint is linear blend");
}

static void test_round_trip_estimation(void)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    turbidity_context context;
    turbidity_result result;
    turbidity_sample sample;
    double measured_mv = 0.0;
    double ntu_values[] = {100.0, 500.0, 1000.0, 1750.0};
    size_t index;

    profile.trim_t = 0.37;
    profile.gain = 1.08;
    profile.offset_mv = -42.0;
    profile.filter_window = 1;
    turbidity_init(&context, &profile);

    for (index = 0; index < sizeof(ntu_values) / sizeof(ntu_values[0]); ++index) {
        expect_true(turbidity_predict_measured_mv(&profile, ntu_values[index], &measured_mv) == 0, "Synthetic measured voltage should compute");
        sample.timestamp_ms = (uint32_t)(index + 1U);
        sample.raw_mv = measured_mv;
        expect_true(turbidity_process_sample(&context, &sample, &result) == 0, "Round-trip sample should process");
        expect_close(result.estimated_ntu, ntu_values[index], 1e-3, "Estimated NTU should round-trip through the model");
        expect_true(result.range_status == TURBIDITY_RANGE_IN_RANGE, "Round-trip sample should stay in range");
    }
}

static void test_monotonic_response(void)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TST10);
    turbidity_context context;
    turbidity_sample sample;
    turbidity_result low_result;
    turbidity_result high_result;
    double low_mv = 0.0;
    double high_mv = 0.0;

    profile.trim_t = 0.6;
    profile.gain = 0.94;
    profile.offset_mv = 18.0;
    profile.filter_window = 1;

    expect_true(turbidity_predict_measured_mv(&profile, 400.0, &low_mv) == 0, "Low turbidity voltage should compute");
    expect_true(turbidity_predict_measured_mv(&profile, 3200.0, &high_mv) == 0, "High turbidity voltage should compute");
    expect_true(low_mv > high_mv, "Measured voltage should drop as NTU rises");

    turbidity_init(&context, &profile);
    sample.timestamp_ms = 1U;
    sample.raw_mv = low_mv;
    expect_true(turbidity_process_sample(&context, &sample, &low_result) == 0, "Low turbidity sample should process");

    turbidity_reset(&context);
    sample.timestamp_ms = 2U;
    sample.raw_mv = high_mv;
    expect_true(turbidity_process_sample(&context, &sample, &high_result) == 0, "High turbidity sample should process");

    expect_true(low_result.estimated_ntu < high_result.estimated_ntu, "Lower voltage should map to higher NTU");
}

static void test_solver_exact_recovery(void)
{
    turbidity_profile source = turbidity_default_profile(TURBIDITY_SENSOR_TST10);
    turbidity_profile solved;
    double ntu[3] = {100.0, 1800.0, 3600.0};
    double mv[3] = {0.0, 0.0, 0.0};
    double rmse_mv = 0.0;
    double max_abs_error_mv = 0.0;
    size_t index;

    source.trim_t = 0.72;
    source.gain = 0.93;
    source.offset_mv = 57.0;

    for (index = 0; index < 3U; ++index) {
        expect_true(turbidity_predict_measured_mv(&source, ntu[index], &mv[index]) == 0, "Synthetic calibration point should compute");
    }

    expect_true(turbidity_solve_profile_3point(source.sensor_kind, ntu, mv, &solved, &rmse_mv, &max_abs_error_mv) == 0, "Solver should recover exact synthetic profile");
    expect_close(solved.trim_t, source.trim_t, 1e-5, "Solved trim_t matches source");
    expect_close(solved.gain, source.gain, 1e-6, "Solved gain matches source");
    expect_close(solved.offset_mv, source.offset_mv, 1e-3, "Solved offset matches source");
    expect_close(rmse_mv, 0.0, 1e-6, "Exact points should fit with zero RMSE");
    expect_close(max_abs_error_mv, 0.0, 1e-6, "Exact points should fit with zero max error");
}

static void test_solver_noisy_recovery(void)
{
    turbidity_profile source = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    turbidity_profile solved;
    double ntu[3] = {100.0, 900.0, 1700.0};
    double mv[3] = {0.0, 0.0, 0.0};
    double noise[3] = {2.0, -3.0, 1.5};
    double rmse_mv = 0.0;
    double max_abs_error_mv = 0.0;
    double predicted_mv = 0.0;
    size_t index;

    source.trim_t = 0.28;
    source.gain = 1.04;
    source.offset_mv = -21.0;

    for (index = 0; index < 3U; ++index) {
        expect_true(turbidity_predict_measured_mv(&source, ntu[index], &mv[index]) == 0, "Noisy synthetic calibration point should compute");
        mv[index] += noise[index];
    }

    expect_true(turbidity_solve_profile_3point(source.sensor_kind, ntu, mv, &solved, &rmse_mv, &max_abs_error_mv) == 0, "Solver should fit noisy points");
    expect_true((solved.trim_t >= 0.0) && (solved.trim_t <= 1.0), "Solved trim_t stays in range");
    expect_true(solved.gain > 0.0, "Solved gain stays positive");
    expect_true(rmse_mv < 5.0, "Noisy fit RMSE stays small");
    expect_true(max_abs_error_mv < 5.0, "Noisy fit max abs error stays small");

    for (index = 0; index < 3U; ++index) {
        expect_true(turbidity_predict_measured_mv(&solved, ntu[index], &predicted_mv) == 0, "Solved profile should predict measured voltage");
        expect_close(predicted_mv, mv[index], 5.0, "Solved profile should stay close to noisy calibration points");
    }
}

static void test_range_clamping(void)
{
    turbidity_profile tsw = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    turbidity_profile tst = turbidity_default_profile(TURBIDITY_SENSOR_TST10);
    turbidity_context context;
    turbidity_sample sample;
    turbidity_result result;
    double zero_mv = 0.0;
    double max_mv = 0.0;

    tsw.filter_window = 1;
    expect_true(turbidity_predict_measured_mv(&tsw, 0.0, &zero_mv) == 0, "TSW clear-water voltage should compute");
    expect_true(turbidity_predict_measured_mv(&tsw, turbidity_sensor_max_ntu(tsw.sensor_kind), &max_mv) == 0, "TSW max-range voltage should compute");
    turbidity_init(&context, &tsw);
    sample.timestamp_ms = 1U;
    sample.raw_mv = zero_mv + 50.0;
    expect_true(turbidity_process_sample(&context, &sample, &result) == 0, "TSW low clamp sample should process");
    expect_true(result.range_status == TURBIDITY_RANGE_CLAMPED_LOW, "TSW above-clear voltage clamps low");
    expect_close(result.estimated_ntu, 0.0, 1e-6, "TSW low clamp returns 0 NTU");

    turbidity_reset(&context);
    sample.timestamp_ms = 2U;
    sample.raw_mv = max_mv - 50.0;
    expect_true(turbidity_process_sample(&context, &sample, &result) == 0, "TSW high clamp sample should process");
    expect_true(result.range_status == TURBIDITY_RANGE_CLAMPED_HIGH, "TSW below-range voltage clamps high");
    expect_close(result.estimated_ntu, 2000.0, 1e-6, "TSW high clamp returns max NTU");

    tst.filter_window = 1;
    expect_true(turbidity_predict_measured_mv(&tst, turbidity_sensor_max_ntu(tst.sensor_kind), &max_mv) == 0, "TST max-range voltage should compute");
    turbidity_init(&context, &tst);
    sample.timestamp_ms = 3U;
    sample.raw_mv = max_mv - 50.0;
    expect_true(turbidity_process_sample(&context, &sample, &result) == 0, "TST high clamp sample should process");
    expect_true(result.range_status == TURBIDITY_RANGE_CLAMPED_HIGH, "TST below-range voltage clamps high");
    expect_close(result.estimated_ntu, 4000.0, 1e-6, "TST high clamp returns max NTU");
}

int main(void)
{
    test_endpoint_family_matches_vendor_fits();
    test_round_trip_estimation();
    test_monotonic_response();
    test_solver_exact_recovery();
    test_solver_noisy_recovery();
    test_range_clamping();

    if (g_failures != 0) {
        fprintf(stderr, "Total failures: %d\n", g_failures);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
