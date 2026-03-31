#include <Arduino.h>
#include <turbidity/turbidity.h>

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

static turbidity_context g_context;
static unsigned long g_last_sample_ms = 0UL;

static turbidity_profile make_profile()
{
    turbidity_profile profile = turbidity_default_profile((turbidity_sensor_kind)TURBIDITY_SENSOR_KIND);
    profile.trim_t = TURBIDITY_TRIM_T;
    profile.gain = TURBIDITY_GAIN;
    profile.offset_mv = TURBIDITY_OFFSET_MV;
    profile.filter_window = TURBIDITY_FILTER_WINDOW;
    return profile;
}

void setup()
{
    turbidity_profile profile = make_profile();

    Serial.begin(115200);
    while (!Serial) {
    }

    turbidity_init(&g_context, &profile);
    Serial.println("timestamp_ms,sensor,raw_mv,filtered_mv,estimated_ntu,range_status");
}

void loop()
{
    unsigned long now = millis();
    if ((now - g_last_sample_ms) < TURBIDITY_SAMPLE_PERIOD_MS) {
        return;
    }

    g_last_sample_ms = now;

    int raw_counts = analogRead(TURBIDITY_ANALOG_PIN);
    double raw_mv = ((double)raw_counts * TURBIDITY_ADC_REF_MV) / TURBIDITY_ADC_MAX_COUNT;
    turbidity_sample sample;
    turbidity_result result;

    sample.timestamp_ms = (uint32_t)now;
    sample.raw_mv = raw_mv;

    if (turbidity_process_sample(&g_context, &sample, &result) != 0) {
        Serial.println("0,unknown,0.000,0.000,0.000000,invalid");
        return;
    }

    Serial.print(result.timestamp_ms);
    Serial.print(',');
    Serial.print(turbidity_sensor_name(g_context.profile.sensor_kind));
    Serial.print(',');
    Serial.print(result.raw_mv, 3);
    Serial.print(',');
    Serial.print(result.filtered_mv, 3);
    Serial.print(',');
    Serial.print(result.estimated_ntu, 6);
    Serial.print(',');
    Serial.println(turbidity_range_status_name(result.range_status));
}
