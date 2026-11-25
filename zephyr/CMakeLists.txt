if(CONFIG_ZMK_DISPLAY AND CONFIG_ZMK_DISPLAY_STATUS_SCREEN_CUSTOM)
    target_include_directories(app PRIVATE ${CMAKE_CURRENT_LIST_DIR}/../oled/fw)
    target_sources(app PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}/../oled/fw/screen.c
        ${CMAKE_CURRENT_LIST_DIR}/../oled/fw/frames.c
        ${CMAKE_CURRENT_LIST_DIR}/../oled/fw/behavior_screen_next.c)
endif()
