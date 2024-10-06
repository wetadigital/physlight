# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.
# 3.13 for target_link_directories.
cmake_minimum_required(VERSION 3.13)

# Define project.
project(
    PhysLightUSDPlugins
    VERSION 0.0.0
    DESCRIPTION "A collection of schema plugins for Pixar's USD (Universal Scene Description)."
    LANGUAGES CXX
)

# Discover cmake modules.
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH}
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/packages
)

# Exposes build options (with default values) for this project.
include(Options)

# Set project defaults.
include(Defaults)

# Import the package dependencies (USD, TBB, ...).
include(Packages)

# Include USD plugin building CMake utilities.
include(USDPluginTools)

# Recurse into source tree.
# A top-level name used as the root directory for public headers
# installation, and the root python module.
# This is optional.  See ./physAreaLight/CMakeLists.txt for how it's used.
set(ORGANIZATION "weta")

# Build & install libraries.
#add_subdirectory(physAreaLight)

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

# Export targets and install package files.
# This must come after source tree recursion as exporting targets
# requires the targets to be defined in the first place!

# include(Export)   # TODO
