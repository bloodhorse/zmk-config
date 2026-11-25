// the whole screen: four patterns, a 50 ms tick, and both hands driving both halves.
// a port of oled/live.js line for line; the emulator is where these get designed.
#include <string.h>
#include <zephyr/kernel.h>
#include <zephyr/settings/settings.h>
#include <lvgl.h>
#include <zmk/behavior.h>
#include <zmk/event_manager.h>
#include <zmk/events/position_state_changed.h>
#include "frames.h"
#include "screen.h"

#define W 32
#define H 128
#define TICK_MS 50
#define BYTES (W * H / 8)

enum { STORM, WIRE, STARS, GEM, MODES };

static uint8_t mode = IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL) ? STORM : GEM;

static uint8_t pix[BYTES], prev[BYTES];
static uint8_t img_map[8 + BYTES] = {0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0xff};
static lv_img_dsc_t img_dsc = {
    .header.cf = LV_IMG_CF_INDEXED_1BIT,
    .header.w = H,
    .header.h = W,
    .data_size = sizeof(img_map),
    .data = img_map,
};
static lv_obj_t *img;

static uint32_t rs = 0x9e3779b9;
static int rnd(int n) {
    rs ^= rs << 13;
    rs ^= rs >> 17;
    rs ^= rs << 5;
    return rs % (uint32_t)n;
}

static inline void put(int x, int y) {
    if (x >= 0 && x < W && y >= 0 && y < H) {
        int i = y * W + x;
        pix[i >> 3] |= 0x80 >> (i & 7);
    }
}

static void rect(int x, int y, int w, int h) {
    for (int j = 0; j < h; j++)
        for (int i = 0; i < w; i++)
            put(x + i, y + j);
}

static void line(int x0, int y0, int x1, int y1, int fade) {
    int dx = x1 > x0 ? x1 - x0 : x0 - x1, sx = x0 < x1 ? 1 : -1;
    int dy = -(y1 > y0 ? y1 - y0 : y0 - y1), sy = y0 < y1 ? 1 : -1;
    int e = dx + dy;
    for (;;) {
        if (!fade || rnd(10) >= fade)
            put(x0, y0);
        if (x0 == x1 && y0 == y1)
            return;
        int e2 = 2 * e;
        if (e2 >= dy) {
            e += dy;
            x0 += sx;
        }
        if (e2 <= dx) {
            e += dx;
            y0 += sy;
        }
    }
}

// keys: the listener (and on the right half, the forwarded left hand) push, the tick pops.
static uint8_t kq[32];
static atomic_t kh, kt;
static struct k_spinlock kq_lock;

void oled_screen_key(uint8_t position) {
    k_spinlock_key_t key = k_spin_lock(&kq_lock);
    atomic_val_t h = atomic_get(&kh);
    if (h - atomic_get(&kt) < (atomic_val_t)sizeof(kq)) {
        kq[h & 31] = position;
        atomic_set(&kh, h + 1);
    }
    k_spin_unlock(&kq_lock, key);
}

// the switcher, on the central, which sees both halves: a pinky held (fuck, pos 24 / 35)
// plus 1 turns the left screen, plus 0 the right one, handed across as &scr_r.
#define PINKY_L 24
#define PINKY_R 35
#define KEY_LEFT 1
#define KEY_RIGHT 10
#if IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL) && DT_NODE_EXISTS(DT_NODELABEL(scr_r))
static uint8_t pinkies;

static void switcher(const struct zmk_position_state_changed *ev) {
    uint8_t bit = ev->position == PINKY_L ? 1 : ev->position == PINKY_R ? 2 : 0;
    if (bit) {
        pinkies = ev->state ? pinkies | bit : pinkies & ~bit;
        return;
    }
    if (!ev->state || !pinkies)
        return;
    if (ev->position == KEY_LEFT) {
        oled_screen_next();
    } else if (ev->position == KEY_RIGHT) {
        struct zmk_behavior_binding b = {.behavior_dev = DEVICE_DT_GET(DT_NODELABEL(scr_r))->name};
        struct zmk_behavior_binding_event e = {.position = ev->position, .timestamp = ev->timestamp};
        zmk_behavior_invoke_binding(&b, e, true);
        zmk_behavior_invoke_binding(&b, e, false);
    }
}
#else
static void switcher(const struct zmk_position_state_changed *ev) {}
#endif

static int on_position(const zmk_event_t *eh) {
    const struct zmk_position_state_changed *ev = as_zmk_position_state_changed(eh);
    if (ev)
        switcher(ev);
    if (!ev || !ev->state)
        return ZMK_EV_EVENT_BUBBLE;
    bool local = ev->source == ZMK_POSITION_STATE_CHANGE_SOURCE_LOCAL;
#if IS_ENABLED(CONFIG_ZMK_SPLIT_ROLE_CENTRAL)
    // both hands drive both screens: the central hears everything, and hands its own
    // presses across so the right half hears them too
    oled_screen_key(ev->position);
#if DT_NODE_EXISTS(DT_NODELABEL(scr_k))
    if (local) {
        struct zmk_behavior_binding b = {.behavior_dev = DEVICE_DT_GET(DT_NODELABEL(scr_k))->name};
        struct zmk_behavior_binding_event e = {.position = ev->position, .timestamp = ev->timestamp};
        zmk_behavior_invoke_binding(&b, e, true);
    }
#endif
#else
    if (local)
        oled_screen_key(ev->position);
#endif
    return ZMK_EV_EVENT_BUBBLE;
}
ZMK_LISTENER(oled_keys, on_position);
ZMK_SUBSCRIPTION(oled_keys, zmk_position_state_changed);

// rain
struct drop {
    int16_t y;
    int8_t x;
    uint8_t len, v;
};
static struct drop drops[16];
static struct {
    int8_t x, t;
} splash[16];
static int boost;

static void drop_new(struct drop *d) {
    d->x = rnd(W);
    if (rnd(5) == 0) {
        d->len = 1 + rnd(2);
        d->v = 3 + rnd(3);
    } else {
        d->len = 4 + rnd(11);
        d->v = 4 + (d->len >> 1) + rnd(3);
    }
    d->y = -(int16_t)(rnd(48) * 16);
}

static void rain_init(void) {
    for (int i = 0; i < 16; i++) {
        drop_new(&drops[i]);
        drops[i].y = rnd(H + drops[i].len) * 16;
    }
}

static void rain_step(void) {
    boost -= (boost + 15) >> 4;
    for (int i = 0; i < 16; i++) {
        struct drop *d = &drops[i];
        int was = d->y >> 4;
        d->y += (d->v * (16 + boost)) >> 4;
        int now = d->y >> 4;
        if (was < H && now >= H && d->len > 3)
            for (int k = 0; k < 16; k++)
                if (splash[k].t <= 0) {
                    splash[k].x = d->x;
                    splash[k].t = 4;
                    break;
                }
        if (now - d->len >= H)
            drop_new(d);
    }
    for (int k = 0; k < 16; k++)
        if (splash[k].t > 0)
            splash[k].t--;
}

static void rain_draw(void) {
    for (int i = 0; i < 16; i++) {
        int y = drops[i].y >> 4;
        for (int j = 0; j < drops[i].len; j++)
            put(drops[i].x, y - j);
    }
    for (int k = 0; k < 16; k++)
        if (splash[k].t > 0) {
            int s = splash[k].t > 2 ? 1 : 2;
            put(splash[k].x - s, H - s);
            put(splash[k].x + s, H - s);
        }
}

// lightning
#define STRIKE_EVERY 4
#define SEGS 96
static struct {
    uint8_t x0, y0, x1, y1, br;
} segs[SEGS];
static int nsegs, bolt_t = -1;
static bool force;

static void walk(int x, int y, int n, int lean, int br) {
    while (n-- > 0 && y < H - 1 && nsegs < SEGS) {
        int ny = MIN(H - 1, y + 3 + rnd(6) - br);
        int nx = CLAMP(x + rnd(9) - 4 + (br ? lean : (W / 2 - x) >> 3), 0, W - 1);
        segs[nsegs].x0 = x;
        segs[nsegs].y0 = y;
        segs[nsegs].x1 = nx;
        segs[nsegs].y1 = ny;
        segs[nsegs].br = br;
        nsegs++;
        if (!br && rnd(4) == 0)
            walk(nx, ny, 2 + rnd(5), rnd(2) ? 2 : -2, 1);
        x = nx;
        y = ny;
    }
}

static void lightning_key(void) {
    if (rnd(STRIKE_EVERY) == 0)
        force = true;
}

static void lightning_step(void) {
    if (bolt_t >= 0) {
        if (++bolt_t > 16)
            bolt_t = -1;
    } else if (force) {
        force = false;
        nsegs = 0;
        walk(8 + rnd(16), 0, rnd(3) ? 99 : 10 + rnd(10), 0, 0);
        bolt_t = 0;
    }
}

static void lightning_draw(void) {
    int t = bolt_t;
    if (t < 0 || t == 1 || t == 4)
        return;
    if (t == 0)
        for (int y = 0; y < H; y++)
            for (int x = 0; x < W; x++)
                if (((x + 3 * y) & 7) == 0)
                    put(x, y);
    int fade = t > 6 ? t - 6 : 0;
    for (int i = 0; i < nsegs; i++) {
        if (segs[i].br && t > 8)
            continue;
        line(segs[i].x0, segs[i].y0, segs[i].x1, segs[i].y1, fade);
        if (!segs[i].br && t <= 3)
            line(segs[i].x0 + 1, segs[i].y0, segs[i].x1 + 1, segs[i].y1, fade);
    }
}

// the wire
#define ROW 5
#define HEAD (H - 8)
#define SPR 10
static const uint8_t HX[5] = {0, 5, 14, 19, 24};
static uint8_t rows[64], xo[64], wq[24];
static int wq_n, x0 = 2, wander = 2400;
static int32_t pos, last_row = -1;

static void wire_init(void) { memset(xo, 2, sizeof(xo)); }

static void wire_key(uint8_t code) {
    if (wq_n < (int)sizeof(wq))
        wq[wq_n++] = 1 + code % 31;
}

static void wire_step(void) {
    int32_t rh = (pos >> 4) / ROW;
    int i = rh & 63;
    if (rh != last_row) {
        rows[i] = 0;
        xo[i] = x0;
        last_row = rh;
    }
    if (wq_n && !rows[i]) {
        rows[i] = wq[0];
        memmove(wq, wq + 1, --wq_n);
    }
    pos += 4 + (wq_n ? 24 : 0);
    if (--wander <= 0) {
        wander = 1200 + rnd(2400);
        x0 = CLAMP(x0 + (rnd(2) ? 1 : -1), 0, 5);
    }
}

static void wire_draw(void) {
    int32_t p = pos >> 4, rh = p / ROW;
    for (int32_t row = rh; row >= 0 && row > rh - 30; row--) {
        int i = row & 63, top = HEAD - p + ROW * row;
        rect(xo[i] + SPR, top + 2, 2, 2);
        for (int k = 0; k < 5; k++)
            if ((rows[i] >> k) & 1)
                rect(xo[i] + HX[k], top + 1, 3, 3);
    }
}

// stars: a key is a frame; at rest a frame a minute
#define CREEP (60000 / TICK_MS)
static int sf, s_pending, s_idle;

static void stars_key(void) {
    if (s_pending < COLUMN_FRAMES)
        s_pending++;
}

static void stars_step(void) {
    if (s_pending) {
        s_pending--;
        sf = (sf + 1) % COLUMN_FRAMES;
        s_idle = 0;
    } else if (++s_idle >= CREEP) {
        s_idle = 0;
        sf = (sf + 1) % COLUMN_FRAMES;
    }
}

// the tick
static void blit(void) {
    uint8_t *out = img_map + 8;
    memset(out, 0, BYTES);
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            int i = y * W + x;
            if (pix[i >> 3] & (0x80 >> (i & 7))) {
                int X = H - 1 - y;
                out[x * (H / 8) + (X >> 3)] |= 0x80 >> (X & 7);
            }
        }
}

static void tick(lv_timer_t *timer) {
    uint8_t m = mode;
    while (atomic_get(&kt) != atomic_get(&kh)) {
        atomic_val_t t = atomic_get(&kt);
        uint8_t code = kq[t & 31];
        atomic_set(&kt, t + 1);
        switch (m) {
        case STORM: lightning_key(); break;
        case WIRE: wire_key(code); break;
        case STARS: stars_key(); break;
        }
    }
    memset(pix, 0, BYTES);
    switch (m) {
    case STORM: rain_step(); lightning_step(); rain_draw(); lightning_draw(); break;
    case WIRE: wire_step(); wire_draw(); break;
    case STARS: stars_step(); memcpy(pix, column_frames[sf], BYTES); break;
    case GEM: memcpy(pix, gem_frames[(k_uptime_get() / GEM_FRAME_MS) % GEM_FRAMES], BYTES); break;
    }
    if (memcmp(pix, prev, BYTES)) {
        memcpy(prev, pix, BYTES);
        blit();
        lv_obj_invalidate(img);
    }
}

// &scr_l / &scr_r (and the switcher above) land here on the matching half; the pick survives a reboot
static void save_mode(struct k_work *work) { settings_save_one("oled/pick", &mode, sizeof(mode)); }
static K_WORK_DELAYABLE_DEFINE(save_work, save_mode);

void oled_screen_next(void) {
    mode = (mode + 1) % MODES;
    k_work_reschedule(&save_work, K_SECONDS(3));
}

static int mode_set(const char *name, size_t len, settings_read_cb read_cb, void *cb_arg) {
    uint8_t m;
    if (settings_name_steq(name, "pick", NULL) && len == 1 && read_cb(cb_arg, &m, 1) == 1 &&
        m < MODES)
        mode = m;
    return 0;
}
SETTINGS_STATIC_HANDLER_DEFINE(oled_screen, "oled", NULL, mode_set, NULL, NULL);

lv_obj_t *zmk_display_status_screen(void) {
    rs ^= k_cycle_get_32() | 1;
    rain_init();
    wire_init();

    lv_obj_t *screen = lv_obj_create(NULL);
    lv_obj_set_style_bg_color(screen, lv_color_white(), LV_PART_MAIN);
    lv_obj_set_style_bg_opa(screen, LV_OPA_COVER, LV_PART_MAIN);

    img = lv_img_create(screen);
    lv_obj_align(img, LV_ALIGN_TOP_LEFT, 0, 0);
    lv_img_set_src(img, &img_dsc);

    lv_timer_create(tick, TICK_MS, NULL);
    return screen;
}
