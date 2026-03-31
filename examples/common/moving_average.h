#ifndef TURBIDITY_EXAMPLES_MOVING_AVERAGE_H
#define TURBIDITY_EXAMPLES_MOVING_AVERAGE_H

#include <stddef.h>

typedef struct moving_average_filter {
    double *samples;
    size_t capacity;
    size_t count;
    size_t next_index;
    double sum;
} moving_average_filter;

static inline void moving_average_init(
    moving_average_filter *filter,
    double *samples,
    size_t capacity
)
{
    filter->samples = samples;
    filter->capacity = capacity;
    filter->count = 0U;
    filter->next_index = 0U;
    filter->sum = 0.0;
}

static inline void moving_average_reset(moving_average_filter *filter)
{
    size_t index;

    filter->count = 0U;
    filter->next_index = 0U;
    filter->sum = 0.0;
    for (index = 0U; index < filter->capacity; ++index) {
        filter->samples[index] = 0.0;
    }
}

static inline double moving_average_push(moving_average_filter *filter, double sample)
{
    if (filter->capacity == 0U) {
        return sample;
    }

    if (filter->count < filter->capacity) {
        filter->samples[filter->next_index] = sample;
        filter->sum += sample;
        filter->count += 1U;
    } else {
        filter->sum -= filter->samples[filter->next_index];
        filter->samples[filter->next_index] = sample;
        filter->sum += sample;
    }

    filter->next_index = (filter->next_index + 1U) % filter->capacity;
    return filter->sum / (double)filter->count;
}

#endif
