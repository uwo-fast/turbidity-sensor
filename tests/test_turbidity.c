#include "turbidity/turbidity.h"
#include "turbidity_model_data.generated.h"

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
        fprintf(
            stderr,
            "FAIL: %s (actual=%.12f expected=%.12f tolerance=%.12f)\n",
            message,
            actual,
            expected,
            tolerance
        );
        g_failures += 1;
    }
}

static const turbidity_model_record *find_model_record(turbidity_sensor_kind sensor_kind)
{
    size_t index;

    for (index = 0; index < TURBIDITY_MODEL_RECORD_COUNT; ++index) {
        if (TURBIDITY_MODEL_RECORDS[index].sensor_kind == sensor_kind) {
            return &TURBIDITY_MODEL_RECORDS[index];
        }
    }

    return NULL;
}

static double evaluate_generated_curve(turbidity_quadratic curve, double ntu)
{
    return (curve.a_mv_per_ntu2 * ntu * ntu) + (curve.b_mv_per_ntu * ntu) + curve.c_mv;
}

static void test_profile_validation(void)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);

    expect_true(turbidity_profile_validate(&profile) == TURBIDITY_STATUS_OK, "default profile should validate");

    profile.trim_t = -0.1;
    expect_true(turbidity_profile_validate(&profile) == TURBIDITY_STATUS_INVALID_PROFILE, "trim below 0 should fail validation");

    profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    profile.gain = 0.0;
    expect_true(turbidity_profile_validate(&profile) == TURBIDITY_STATUS_INVALID_PROFILE, "zero gain should fail validation");
}

static void test_generated_endpoints_match_family_eval(void)
{
    const turbidity_model_record *tsw = find_model_record(TURBIDITY_SENSOR_TSW10);
    const turbidity_model_record *tst = find_model_record(TURBIDITY_SENSOR_TST10);
    double ntu_values[] = {0.0, 500.0, 1000.0, 1500.0};
    size_t index;

    expect_true(tsw != NULL, "TSW generated model record should exist");
    expect_true(tst != NULL, "TST generated model record should exist");

    for (index = 0; index < sizeof(ntu_values) / sizeof(ntu_values[0]); ++index) {
        double low_mv = 0.0;
        double high_mv = 0.0;
        double mid_mv = 0.0;
        double ntu = ntu_values[index];

        expect_true(
            turbidity_eval_family_mv(TURBIDITY_SENSOR_TSW10, 0.0, ntu, &low_mv) == TURBIDITY_STATUS_OK,
            "TSW low curve should evaluate"
        );
        expect_true(
            turbidity_eval_family_mv(TURBIDITY_SENSOR_TSW10, 1.0, ntu, &high_mv) == TURBIDITY_STATUS_OK,
            "TSW high curve should evaluate"
        );
        expect_true(
            turbidity_eval_family_mv(TURBIDITY_SENSOR_TSW10, 0.5, ntu, &mid_mv) == TURBIDITY_STATUS_OK,
            "TSW midpoint curve should evaluate"
        );
        expect_close(low_mv, evaluate_generated_curve(tsw->low_curve, ntu), 1e-6, "TSW low endpoint matches generated header");
        expect_close(high_mv, evaluate_generated_curve(tsw->high_curve, ntu), 1e-6, "TSW high endpoint matches generated header");
        expect_close(mid_mv, (low_mv + high_mv) / 2.0, 1e-6, "TSW midpoint is a linear blend");
    }

    {
        double low_mv = 0.0;
        double high_mv = 0.0;
        double max_ntu = 2000.0;

        expect_true(
            turbidity_eval_family_mv(TURBIDITY_SENSOR_TST10, 0.0, max_ntu, &low_mv) == TURBIDITY_STATUS_OK,
            "TST low curve should evaluate at 2000 NTU"
        );
        expect_true(
            turbidity_eval_family_mv(TURBIDITY_SENSOR_TST10, 1.0, max_ntu, &high_mv) == TURBIDITY_STATUS_OK,
            "TST high curve should evaluate at 2000 NTU"
        );
        expect_close(low_mv, evaluate_generated_curve(tst->low_curve, max_ntu), 1e-6, "TST low endpoint matches generated header");
        expect_close(high_mv, evaluate_generated_curve(tst->high_curve, max_ntu), 1e-6, "TST high endpoint matches generated header");
    }
}

static void test_round_trip_estimation(void)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    double ntu_values[] = {100.0, 500.0, 1000.0, 1750.0};
    size_t index;

    profile.trim_t = 0.37;
    profile.gain = 1.08;
    profile.offset_mv = -42.0;

    for (index = 0; index < sizeof(ntu_values) / sizeof(ntu_values[0]); ++index) {
        turbidity_estimate estimate;
        double measured_mv = 0.0;

        expect_true(
            turbidity_predict_measured_mv(&profile, ntu_values[index], &measured_mv) == TURBIDITY_STATUS_OK,
            "synthetic measured voltage should compute"
        );
        expect_true(
            turbidity_estimate_ntu_from_mv(&profile, measured_mv, &estimate) == TURBIDITY_STATUS_OK,
            "round-trip estimate should compute"
        );
        expect_close(estimate.estimated_ntu, ntu_values[index], 1e-3, "estimated NTU should round-trip through the model");
        expect_true(estimate.range_status == TURBIDITY_RANGE_IN_RANGE, "round-trip sample should stay in range");
    }
}

static void test_monotonic_response(void)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TST10);
    turbidity_estimate low_estimate;
    turbidity_estimate high_estimate;
    double low_mv = 0.0;
    double high_mv = 0.0;

    profile.trim_t = 0.6;
    profile.gain = 0.94;
    profile.offset_mv = 18.0;

    expect_true(turbidity_predict_measured_mv(&profile, 400.0, &low_mv) == TURBIDITY_STATUS_OK, "low turbidity voltage should compute");
    expect_true(turbidity_predict_measured_mv(&profile, 3200.0, &high_mv) == TURBIDITY_STATUS_OK, "high turbidity voltage should compute");
    expect_true(low_mv > high_mv, "measured voltage should drop as NTU rises");

    expect_true(turbidity_estimate_ntu_from_mv(&profile, low_mv, &low_estimate) == TURBIDITY_STATUS_OK, "low turbidity estimate should compute");
    expect_true(turbidity_estimate_ntu_from_mv(&profile, high_mv, &high_estimate) == TURBIDITY_STATUS_OK, "high turbidity estimate should compute");
    expect_true(low_estimate.estimated_ntu < high_estimate.estimated_ntu, "lower voltage should map to higher NTU");
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
        expect_true(turbidity_predict_measured_mv(&source, ntu[index], &mv[index]) == TURBIDITY_STATUS_OK, "synthetic calibration point should compute");
    }

    expect_true(
        turbidity_solve_profile_3point(source.sensor_kind, ntu, mv, &solved, &rmse_mv, &max_abs_error_mv) == TURBIDITY_STATUS_OK,
        "solver should recover exact synthetic profile"
    );
    expect_close(solved.trim_t, source.trim_t, 1e-5, "solved trim_t matches source");
    expect_close(solved.gain, source.gain, 1e-6, "solved gain matches source");
    expect_close(solved.offset_mv, source.offset_mv, 1e-3, "solved offset matches source");
    expect_close(rmse_mv, 0.0, 1e-6, "exact points should fit with zero RMSE");
    expect_close(max_abs_error_mv, 0.0, 1e-6, "exact points should fit with zero max error");
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
        expect_true(turbidity_predict_measured_mv(&source, ntu[index], &mv[index]) == TURBIDITY_STATUS_OK, "noisy synthetic calibration point should compute");
        mv[index] += noise[index];
    }

    expect_true(
        turbidity_solve_profile_3point(source.sensor_kind, ntu, mv, &solved, &rmse_mv, &max_abs_error_mv) == TURBIDITY_STATUS_OK,
        "solver should fit noisy points"
    );
    expect_true((solved.trim_t >= 0.0) && (solved.trim_t <= 1.0), "solved trim_t stays in range");
    expect_true(solved.gain > 0.0, "solved gain stays positive");
    expect_true(rmse_mv < 5.0, "noisy fit RMSE stays small");
    expect_true(max_abs_error_mv < 5.0, "noisy fit max abs error stays small");

    for (index = 0; index < 3U; ++index) {
        expect_true(turbidity_predict_measured_mv(&solved, ntu[index], &predicted_mv) == TURBIDITY_STATUS_OK, "solved profile should predict measured voltage");
        expect_close(predicted_mv, mv[index], 5.0, "solved profile should stay close to noisy calibration points");
    }
}

static void test_range_clamping(void)
{
    turbidity_profile tsw = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    turbidity_profile tst = turbidity_default_profile(TURBIDITY_SENSOR_TST10);
    turbidity_estimate estimate;
    double zero_mv = 0.0;
    double tsw_max_mv = 0.0;
    double tst_max_mv = 0.0;
    double max_ntu = 0.0;

    expect_true(turbidity_predict_measured_mv(&tsw, 0.0, &zero_mv) == TURBIDITY_STATUS_OK, "TSW clear-water voltage should compute");
    expect_true(turbidity_sensor_max_ntu(tsw.sensor_kind, &max_ntu) == TURBIDITY_STATUS_OK, "TSW max NTU should be available");
    expect_true(turbidity_predict_measured_mv(&tsw, max_ntu, &tsw_max_mv) == TURBIDITY_STATUS_OK, "TSW max-range voltage should compute");

    expect_true(turbidity_estimate_ntu_from_mv(&tsw, zero_mv + 50.0, &estimate) == TURBIDITY_STATUS_OK, "TSW low clamp sample should process");
    expect_true(estimate.range_status == TURBIDITY_RANGE_CLAMPED_LOW, "TSW above-clear voltage clamps low");
    expect_close(estimate.estimated_ntu, 0.0, 1e-6, "TSW low clamp returns 0 NTU");

    expect_true(turbidity_estimate_ntu_from_mv(&tsw, tsw_max_mv - 50.0, &estimate) == TURBIDITY_STATUS_OK, "TSW high clamp sample should process");
    expect_true(estimate.range_status == TURBIDITY_RANGE_CLAMPED_HIGH, "TSW below-range voltage clamps high");
    expect_close(estimate.estimated_ntu, 2000.0, 1e-6, "TSW high clamp returns max NTU");

    expect_true(turbidity_sensor_max_ntu(tst.sensor_kind, &max_ntu) == TURBIDITY_STATUS_OK, "TST max NTU should be available");
    expect_true(turbidity_predict_measured_mv(&tst, max_ntu, &tst_max_mv) == TURBIDITY_STATUS_OK, "TST max-range voltage should compute");
    expect_true(turbidity_estimate_ntu_from_mv(&tst, tst_max_mv - 50.0, &estimate) == TURBIDITY_STATUS_OK, "TST high clamp sample should process");
    expect_true(estimate.range_status == TURBIDITY_RANGE_CLAMPED_HIGH, "TST below-range voltage clamps high");
    expect_close(estimate.estimated_ntu, 4000.0, 1e-6, "TST high clamp returns max NTU");
}

int main(void)
{
    test_profile_validation();
    test_generated_endpoints_match_family_eval();
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
