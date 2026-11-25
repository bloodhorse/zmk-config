// &scr_l / &scr_r: the next pattern on one half's screen. global, so the central hands the press to
// the peripheral too; each half acts only when the side is its own (left is the central).
#define DT_DRV_COMPAT zmk_behavior_screen_next

#include <zephyr/device.h>
#include <drivers/behavior.h>
#include <zmk/behavior.h>
#include "screen.h"

#if DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT)

struct screen_next_config {
    uint8_t side;
};

static int on_pressed(struct zmk_behavior_binding *binding, struct zmk_behavior_binding_event event) {
    const struct device *dev = zmk_behavior_get_binding(binding->behavior_dev);
    const struct screen_next_config *cfg = dev->config;
    if (cfg->side == (IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL) ? 0 : 1))
        oled_screen_next();
    return ZMK_BEHAVIOR_OPAQUE;
}

static int on_released(struct zmk_behavior_binding *binding, struct zmk_behavior_binding_event event) {
    return ZMK_BEHAVIOR_OPAQUE;
}

static const struct behavior_driver_api screen_next_api = {
    .binding_pressed = on_pressed,
    .binding_released = on_released,
    .locality = BEHAVIOR_LOCALITY_GLOBAL,
#if IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)
    .get_parameter_metadata = zmk_behavior_get_empty_param_metadata,
#endif
};

#define SCREEN_NEXT_INST(n)                                                                        \
    static const struct screen_next_config screen_next_config_##n = {.side = DT_INST_PROP(n, side)}; \
    BEHAVIOR_DT_INST_DEFINE(n, NULL, NULL, NULL, &screen_next_config_##n, POST_KERNEL,             \
                            CONFIG_KERNEL_INIT_PRIORITY_DEFAULT, &screen_next_api);

DT_INST_FOREACH_STATUS_OKAY(SCREEN_NEXT_INST)

#endif
