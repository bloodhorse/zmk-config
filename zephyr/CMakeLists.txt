if(CONFIG_ZMK_DISPLAY AND CONFIG_ZMK_DISPLAY_STATUS_SCREEN_CUSTOM)
    target_include_directories(app PRIVATE ${CMAKE_CURRENT_LIST_DIR}/../oled/fw)
    target_sources(app PRIVATE ${CMAKE_CURRENT_LIST_DIR}/../oled/fw/stars.c ${CMAKE_CURRENT_LIST_DIR}/../oled/fw/star_frames.c)
endif()
