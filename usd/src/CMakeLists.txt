# A top-level name used as the root directory for public headers
# installation, and the root python module.
# This is optional.  See ./usdTri/CMakeLists.txt for how it's used.
set(ORGANIZATION "usdpluginexamples")

# Build & install libraries.
add_subdirectory(usdTri)
add_subdirectory(usdviewTri)

# Build & install plugins.
add_subdirectory(usdTriImaging)
add_subdirectory(usdTriFileFormat)
add_subdirectory(hdTri)

# Install top-level plugInfo for including per-library plugInfo(s).
install(
    FILES plugInfo.json
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/${USD_PLUG_INFO_ROOT_DIR}
)

# Install top-level plugInfo for including per-plugin plugInfo(s).
install(
    FILES plugInfo.json
    DESTINATION ${USD_PLUGIN_DIR}/${USD_PLUG_INFO_ROOT_DIR}
)

# Install top level python __init__.py
install(
    FILES __init__.py
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/${USD_PYTHON_DIR}/${ORGANIZATION}
)

# Mirror installation structure in intermediate binary dir for running tests against.
if (BUILD_TESTING)
    file(
        COPY plugInfo.json
        DESTINATION ${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}/${USD_PLUG_INFO_ROOT_DIR}
    )

    file(
        COPY plugInfo.json
        DESTINATION ${PROJECT_BINARY_DIR}/${USD_PLUGIN_DIR}/${USD_PLUG_INFO_ROOT_DIR}
    )

    file(
        COPY __init__.py
        DESTINATION ${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}/${USD_PYTHON_DIR}/${ORGANIZATION}
    )
endif()

