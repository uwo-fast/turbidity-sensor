#include <Arduino.h>
#include <turbidity/turbidity.h>

#include "../../common/moving_average.h"

#ifndef TURBIDITY_ANALOG_PIN
#define TURBIDITY_ANALOG_PIN A0
#endif

/* AVR conversion: counts = V_in * 1024 / V_ref. */
#ifndef TURBIDITY_ADC_MAX_COUNT
#define TURBIDITY_ADC_MAX_COUNT 1024.0
#endif

/* Measure the board's 5 V rail with a multimeter and set this to it. */
#ifndef TURBIDITY_ADC_REF_MV
#define TURBIDITY_ADC_REF_MV 5000.0
#endif

#ifndef TURBIDITY_SAMPLE_PERIOD_MS
#define TURBIDITY_SAMPLE_PERIOD_MS 100UL
#endif

/* ADC reads averaged into each logged sample. */
#ifndef TURBIDITY_OVERSAMPLE
#define TURBIDITY_OVERSAMPLE 16
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

/*
 * Optional: wire the 470 ohm emitter resistor to this pin instead of GND.
 * The pin sinks the emitter current (LOW = emitter on), and each sample then
 * also logs dark_adc_counts with the emitter off, which measures ambient light.
 */
#ifdef TURBIDITY_EMITTER_PIN
#ifndef TURBIDITY_EMITTER_SETTLE_MS
#define TURBIDITY_EMITTER_SETTLE_MS 5UL
#endif
#endif

/*
 * On the ATmega328P, Vcc is estimated from the internal 1.1 V bandgap. The
 * bandgap varies by about 10% between chips, so vcc_mv tracks supply drift
 * within a session; it is not an absolute measurement.
 */
#if defined(__AVR_ATmega328P__)
#define TURBIDITY_HAS_VCC_MONITOR 1
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

static double read_adc_counts()
{
    unsigned long sum = 0UL;
    int index;

    for (index = 0; index < TURBIDITY_OVERSAMPLE; ++index) {
        sum += (unsigned long)analogRead(TURBIDITY_ANALOG_PIN);
    }
    return (double)sum / (double)TURBIDITY_OVERSAMPLE;
}

#ifdef TURBIDITY_HAS_VCC_MONITOR
static long read_vcc_mv()
{
    uint16_t result;

    /* AVcc reference, bandgap input. */
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
    delay(2);
    ADCSRA |= _BV(ADSC);
    while (bit_is_set(ADCSRA, ADSC)) {
    }
    result = ADC;

    /* analogRead() restores ADMUX; discard its first conversion after the switch. */
    (void)analogRead(TURBIDITY_ANALOG_PIN);
    return (result != 0U) ? (1100L * 1024L) / (long)result : 0L;
}
#endif

void setup()
{
    g_profile = make_profile();
    moving_average_init(&g_filter, g_filter_buffer, TURBIDITY_FILTER_WINDOW);
    moving_average_reset(&g_filter);

#ifdef TURBIDITY_EMITTER_PIN
    pinMode(TURBIDITY_EMITTER_PIN, OUTPUT);
    digitalWrite(TURBIDITY_EMITTER_PIN, LOW);
#endif

    Serial.begin(115200);
    Serial.print("timestamp_ms,sensor,adc_counts");
#ifdef TURBIDITY_EMITTER_PIN
    Serial.print(",dark_adc_counts");
#endif
#ifdef TURBIDITY_HAS_VCC_MONITOR
    Serial.print(",vcc_mv");
#endif
    Serial.println(",raw_mv,filtered_mv,equivalent_mv,estimated_ntu,range_status");
}

void loop()
{
    unsigned long now = millis();
    double adc_counts;
    double raw_mv;
    double filtered_mv;
    turbidity_estimate estimate;
    turbidity_status status;
#ifdef TURBIDITY_EMITTER_PIN
    double dark_adc_counts;
#endif
#ifdef TURBIDITY_HAS_VCC_MONITOR
    long vcc_mv;
#endif

    if ((now - g_last_sample_ms) < TURBIDITY_SAMPLE_PERIOD_MS) {
        return;
    }
    g_last_sample_ms = now;

#ifdef TURBIDITY_EMITTER_PIN
    digitalWrite(TURBIDITY_EMITTER_PIN, HIGH);
    delay(TURBIDITY_EMITTER_SETTLE_MS);
    dark_adc_counts = read_adc_counts();
    digitalWrite(TURBIDITY_EMITTER_PIN, LOW);
    delay(TURBIDITY_EMITTER_SETTLE_MS);
#endif

    adc_counts = read_adc_counts();
#ifdef TURBIDITY_HAS_VCC_MONITOR
    vcc_mv = read_vcc_mv();
#endif

    raw_mv = (adc_counts * TURBIDITY_ADC_REF_MV) / TURBIDITY_ADC_MAX_COUNT;
    filtered_mv = moving_average_push(&g_filter, raw_mv);
    status = turbidity_estimate_ntu_from_mv(&g_profile, filtered_mv, &estimate);

    Serial.print(now);
    Serial.print(',');
    Serial.print(turbidity_sensor_name(g_profile.sensor_kind));
    Serial.print(',');
    Serial.print(adc_counts, 2);
#ifdef TURBIDITY_EMITTER_PIN
    Serial.print(',');
    Serial.print(dark_adc_counts, 2);
#endif
#ifdef TURBIDITY_HAS_VCC_MONITOR
    Serial.print(',');
    Serial.print(vcc_mv);
#endif
    Serial.print(',');
    Serial.print(raw_mv, 3);
    Serial.print(',');
    Serial.print(filtered_mv, 3);
    Serial.print(',');

    if (status != TURBIDITY_STATUS_OK) {
        Serial.print("nan,nan,");
        Serial.println(turbidity_status_name(status));
        return;
    }

    Serial.print(estimate.equivalent_mv, 3);
    Serial.print(',');
    Serial.print(estimate.estimated_ntu, 6);
    Serial.print(',');
    Serial.println(turbidity_range_status_name(estimate.range_status));
}
