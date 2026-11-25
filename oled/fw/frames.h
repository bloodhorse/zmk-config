#pragma once
#include <stdint.h>

#define COLUMN_FRAMES 72
#define COLUMN_FRAME_MS 83
extern const uint8_t column_frames[COLUMN_FRAMES][512];
#define GEM_FRAMES 16
#define GEM_FRAME_MS 59
extern const uint8_t gem_frames[GEM_FRAMES][512];
