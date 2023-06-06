# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.
# Default build configurations for the USDPluginExamples project.

# By default, build for release.
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

# Check if CTest should be enabled.
if (BUILD_TESTING)
    enable_testing()

    # Be very verbose on test failure.
    list(APPEND CMAKE_CTEST_ARGUMENTS "--output-on-failure")
endif()
