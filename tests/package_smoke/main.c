#include "turbidity/turbidity.h"

#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    turbidity_profile profile = turbidity_default_profile(TURBIDITY_SENSOR_TSW10);
    turbidity_estimate estimate;
    double measured_mv = 0.0;

    if (turbidity_profile_validate(&profile) != TURBIDITY_STATUS_OK) {
        return EXIT_FAILURE;
    }
    if (turbidity_predict_measured_mv(&profile, 500.0, &measured_mv) != TURBIDITY_STATUS_OK) {
        return EXIT_FAILURE;
    }
    if (turbidity_estimate_ntu_from_mv(&profile, measured_mv, &estimate) != TURBIDITY_STATUS_OK) {
        return EXIT_FAILURE;
    }
    if (estimate.range_status != TURBIDITY_RANGE_IN_RANGE) {
        return EXIT_FAILURE;
    }

    printf("%.3f %.3f\n", measured_mv, estimate.estimated_ntu);
    return EXIT_SUCCESS;
}
