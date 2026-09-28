// Bench logger: raw readings from several turbidity heads at once.
//
// Each head (probe + SEN0189 adapter, switch at A) feeds one analog input.
// Every sample period this prints one CSV row with the oversampled ADC counts
// for every channel. It applies no model: normalization against each head's
// dark and clear-water readings happens on the host (just summarize).
#include <Arduino.h>

#ifndef TURBIDITY_SAMPLE_PERIOD_MS
#define TURBIDITY_SAMPLE_PERIOD_MS 100UL
#endif

/* ADC reads averaged into each logged sample, per channel. */
#ifndef TURBIDITY_OVERSAMPLE
#define TURBIDITY_OVERSAMPLE 16
#endif

/*
 * On the ATmega328P, Vcc is estimated from the internal 1.1 V bandgap. The
 * bandgap varies by about 10% between chips, so vcc_mv tracks supply drift
 * within a session; it is not an absolute measurement.
 */
#if defined(__AVR_ATmega328P__)
#define TURBIDITY_HAS_VCC_MONITOR 1
#endif

/* Analog inputs to log, in column order. Column names come from CHANNEL_NAMES. */
static const uint8_t CHANNEL_PINS[] = {A0, A1, A2, A3};
static const char *const CHANNEL_NAMES[] = {"a0", "a1", "a2", "a3"};
static const uint8_t CHANNEL_COUNT = sizeof(CHANNEL_PINS) / sizeof(CHANNEL_PINS[0]);

static unsigned long g_last_sample_ms = 0UL;

static double read_adc_counts(uint8_t pin)
{
    unsigned long sum = 0UL;
    int index;

    /* The first conversion after switching the multiplexer can carry charge from the last channel. */
    (void)analogRead(pin);
    for (index = 0; index < TURBIDITY_OVERSAMPLE; ++index) {
        sum += (unsigned long)analogRead(pin);
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
    return (result != 0U) ? (1100L * 1024L) / (long)result : 0L;
}
#endif

void setup()
{
    uint8_t channel;

    Serial.begin(115200);
    Serial.print("timestamp_ms");
#ifdef TURBIDITY_HAS_VCC_MONITOR
    Serial.print(",vcc_mv");
#endif
    for (channel = 0; channel < CHANNEL_COUNT; ++channel) {
        Serial.print(",adc_counts_");
        Serial.print(CHANNEL_NAMES[channel]);
    }
    Serial.println();
}

void loop()
{
    unsigned long now = millis();
    uint8_t channel;

    if ((now - g_last_sample_ms) < TURBIDITY_SAMPLE_PERIOD_MS) {
        return;
    }
    g_last_sample_ms = now;

    Serial.print(now);
#ifdef TURBIDITY_HAS_VCC_MONITOR
    Serial.print(',');
    Serial.print(read_vcc_mv());
#endif
    for (channel = 0; channel < CHANNEL_COUNT; ++channel) {
        Serial.print(',');
        Serial.print(read_adc_counts(CHANNEL_PINS[channel]), 2);
    }
    Serial.println();
}
