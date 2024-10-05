# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.
# Discovery of the dependencies of USDPluginExamples.

# Boost & python.
if (ENABLE_PYTHON_SUPPORT)
    find_package (Python3 COMPONENTS Interpreter Development Development.Module)
    find_package (Boost CONFIG COMPONENTS python REQUIRED)
endif()

# USD & TBB
set(Python3_LIBRARY ${Python3_LIBRARIES})
set(Python3_INCLUDE_DIR ${Python3_INCLUDE_DIRS})

list (APPEND CMAKE_PREFIX_PATH ${USD_ROOT}/lib/cmake)
list (APPEND CMAKE_PREFIX_PATH ${USD_ROOT}/lib64/cmake)

include(${USD_ROOT}/pxrConfig.cmake)
find_package(TBB REQUIRED)
