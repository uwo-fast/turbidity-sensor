#include <Arduino.h>
#include <turbidity/turbidity.h>

#include "../../common/moving_average.h"

#ifndef TURBIDITY_ANALOG_PIN
#define TURBIDITY_ANALOG_PIN A0
#endif

#ifndef TURBIDITY_ADC_MAX_COUNT
#define TURBIDITY_ADC_MAX_COUNT 1023.0
#endif

#ifndef TURBIDITY_ADC_REF_MV
#define TURBIDITY_ADC_REF_MV 5000.0
#endif

#ifndef TURBIDITY_SAMPLE_PERIOD_MS
#define TURBIDITY_SAMPLE_PERIOD_MS 100UL
#endif

#ifndef TURBIDITY_SENSOR_KIND
#define TURBIDITY_SENSOR_KIND TURBIDITY_SENSOR_TSW10
#endif

#ifndef TURBIDITY_TRIM_T
#define TURBIDITY_TRIM_T 0.5
#endif

#ifndef TURBIDITY_GAIN
#define TURBIDITY_GAIN 1.0
#endif

#ifndef TURBIDITY_OFFSET_MV
#define TURBIDITY_OFFSET_MV 0.0
#endif

#ifndef TURBIDITY_FILTER_WINDOW
#define TURBIDITY_FILTER_WINDOW 8
#endif

static turbidity_profile g_profile;
static moving_average_filter g_filter;
static double g_filter_buffer[TURBIDITY_FILTER_WINDOW];
static unsigned long g_last_sample_ms = 0UL;

static turbidity_profile make_profile()
{
    turbidity_profile profile = turbidity_default_profile((turbidity_sensor_kind)TURBIDITY_SENSOR_KIND);
    profile.trim_t = TURBIDITY_TRIM_T;
    profile.gain = TURBIDITY_GAIN;
    profile.offset_mv = TURBIDITY_OFFSET_MV;
    return profile;
}

void setup()
{
    g_profile = make_profile();
    moving_average_init(&g_filter, g_filter_buffer, TURBIDITY_FILTER_WINDOW);
    moving_average_reset(&g_filter);

    Serial.begin(115200);
    Serial.println("timestamp_ms,sensor,raw_mv,filtered_mv,equivalent_mv,estimated_ntu,range_status");
}

void loop()
{
    unsigned long now = millis();
    int raw_counts;
    double raw_mv;
    double filtered_mv;
    turbidity_estimate estimate;
    turbidity_status status;

    if ((now - g_last_sample_ms) < TURBIDITY_SAMPLE_PERIOD_MS) {
        return;
    }
    g_last_sample_ms = now;

    raw_counts = analogRead(TURBIDITY_ANALOG_PIN);
    raw_mv = ((double)raw_counts * TURBIDITY_ADC_REF_MV) / TURBIDITY_ADC_MAX_COUNT;
    filtered_mv = moving_average_push(&g_filter, raw_mv);
    status = turbidity_estimate_ntu_from_mv(&g_profile, filtered_mv, &estimate);

    if (status != TURBIDITY_STATUS_OK) {
        Serial.print(now);
        Serial.print(',');
        Serial.print(turbidity_sensor_name(g_profile.sensor_kind));
        Serial.print(',');
        Serial.print(raw_mv, 3);
        Serial.print(',');
        Serial.print(filtered_mv, 3);
        Serial.print(",0.000,0.000000,");
        Serial.println(turbidity_status_name(status));
        return;
    }

    Serial.print(now);
    Serial.print(',');
    Serial.print(turbidity_sensor_name(g_profile.sensor_kind));
    Serial.print(',');
    Serial.print(raw_mv, 3);
    Serial.print(',');
    Serial.print(filtered_mv, 3);
    Serial.print(',');
    Serial.print(estimate.equivalent_mv, 3);
    Serial.print(',');
    Serial.print(estimate.estimated_ntu, 6);
    Serial.print(',');
    Serial.println(turbidity_range_status_name(estimate.range_status));
}
