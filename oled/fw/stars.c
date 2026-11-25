#include <zephyr/kernel.h>
#include <lvgl.h>
#include "star_frames.h"

static lv_obj_t *img;
static uint16_t frame;

static void next_frame(lv_timer_t *timer) {
    frame = (frame + 1) % STAR_FRAMES;
    lv_img_set_src(img, star_frames[frame]);
}

lv_obj_t *zmk_display_status_screen(void) {
    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_set_style_bg_color(screen, lv_color_white(), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, LV_PART_MAIN);

    img = lv_img_create(screen);
    lv_obj_align(img, LV_ALIGN_TOP_LEFT, 0, 0);
    lv_img_set_src(img, star_frames[0]);

    lv_timer_create(next_frame, STAR_FRAME_MS, NULL);
    return screen;
}
