# Simple module to find USD.
# Expects USD_ROOT to be defined.
# Will define:
# USD_INCLUDE_DIR 
# USD_LIBRARY_DIR 

message(STATUS ${USD_ROOT})

set(PXR_LIB_PREFIX "lib")

if (MSVC)
    # MSVC does not use prefixes for libs
    set(PXR_LIB_PREFIX "")
endif()

find_path(USD_INCLUDE_DIR pxr/pxr.h
          PATHS ${USD_ROOT}/include
                $ENV{USD_ROOT}/include
          DOC "USD Include directory"
          NO_DEFAULT_PATH
          NO_SYSTEM_ENVIRONMENT_PATH)

find_path(USD_LIBRARY_DIR
          NAMES "${PXR_LIB_PREFIX}usd${CMAKE_SHARED_LIBRARY_SUFFIX}"
          PATHS ${USD_ROOT}/lib
                $ENV{USD_ROOT}/lib
          DOC "USD Libraries directory"
          NO_DEFAULT_PATH
          NO_SYSTEM_ENVIRONMENT_PATH)
set(USD_LIBRARY_MONOLITHIC FALSE)

if(USD_INCLUDE_DIR AND EXISTS "${USD_INCLUDE_DIR}/pxr/pxr.h")
    foreach(_usd_comp MAJOR MINOR PATCH)
        file(STRINGS
            "${USD_INCLUDE_DIR}/pxr/pxr.h"
            _usd_tmp
            REGEX "#define PXR_${_usd_comp}_VERSION .*$")
        string(REGEX MATCHALL "[0-9]+" USD_${_usd_comp}_VERSION ${_usd_tmp})
    endforeach()
    set(USD_VERSION ${USD_MAJOR_VERSION}.${USD_MINOR_VERSION}.${USD_PATCH_VERSION})
endif()

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(USD
    REQUIRED_VARS
        USD_INCLUDE_DIR
        USD_LIBRARY_DIR
    VERSION_VAR
        USD_VERSION
)
