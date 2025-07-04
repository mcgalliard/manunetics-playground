#include "math.h"

int max(uint8_t a, uint8_t b)
{
    if (a > b) return a;
    if (b > a) return b;
    return 0;
}