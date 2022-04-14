# ============================================================================
# Public-facing convenience functions & macros for building USD plugin(s).
# ============================================================================

# To gain access to standard install directory variables such as CMAKE_INSTALL_LIBDIR.
include(GNUInstallDirs)

# Exposed USD variable(s) for installation.
# XXX: We can hide these if we provide a more convenient way to install the
# root plugInfo.json(s) and __init__.py files.
set(USD_PLUGIN_DIR "plugin")
set(USD_PYTHON_DIR "python")
set(USD_PLUG_INFO_RESOURCES_DIR "resources")
set(USD_PLUG_INFO_ROOT_DIR "usd")

#
# Public entry point for building a C++ based USD shared library.
#
function(usd_library NAME)
    set(options)

    set(oneValueArgs
    )

    set(multiValueArgs
        PUBLIC_HEADERS_INSTALL_PREFIX
        PUBLIC_HEADERS
        PUBLIC_CLASSES
        CPPFILES
        LIBRARIES
        INCLUDE_DIRS
        RESOURCE_FILES
        PYTHON_INSTALL_PREFIX
        PYTHON_FILES
        PYTHON_CPPFILES
        PYMODULE_CPPFILES
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    _usd_cpp_library(${NAME}
        TYPE
            SHARED
        PUBLIC_HEADERS_INSTALL_PREFIX
            ${args_PUBLIC_HEADERS_INSTALL_PREFIX}
        PUBLIC_HEADERS
            ${args_PUBLIC_HEADERS}
        PUBLIC_CLASSES
            ${args_PUBLIC_CLASSES}
        CPPFILES
            ${args_CPPFILES}
        LIBRARIES
            ${args_LIBRARIES}
        INCLUDE_DIRS
            ${args_INCLUDE_DIRS}
        PYTHON_CPPFILES
            ${args_PYTHON_CPPFILES}
    )

    _usd_install_resource_files(${NAME}
        TYPE
            SHARED
        RESOURCE_FILES
            ${args_RESOURCE_FILES}
    )

    if (ENABLE_PYTHON_SUPPORT)
        _usd_python_module(${NAME}
            PYTHON_INSTALL_PREFIX
                ${args_PYTHON_INSTALL_PREFIX}
            LIBRARIES
                ${args_LIBRARIES}
            INCLUDE_DIRS
                ${args_INCLUDE_DIRS}
            PYMODULE_CPPFILES
                ${args_PYMODULE_CPPFILES}
            PYTHON_FILES
                ${args_PYTHON_FILES}
        )
    endif()

endfunction()

#
# Public entry point for building a C++ based USD plugin.
#
function(usd_plugin NAME)
    set(options)

    set(oneValueArgs
    )

    set(multiValueArgs
        CPPFILES
        LIBRARIES
        INCLUDE_DIRS
        RESOURCE_FILES
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    _usd_cpp_library(${NAME}
        TYPE
            "PLUGIN"
        PUBLIC_HEADERS_INSTALL_PREFIX
            ${args_PUBLIC_HEADERS_INSTALL_PREFIX}
        PUBLIC_HEADERS
            ${args_PUBLIC_HEADERS}
        PUBLIC_CLASSES
            ${args_PUBLIC_CLASSES}
        CPPFILES
            ${args_CPPFILES}
        LIBRARIES
            ${args_LIBRARIES}
        INCLUDE_DIRS
            ${args_INCLUDE_DIRS}
    )

    _usd_install_resource_files(${NAME}
        TYPE
            "PLUGIN"
        RESOURCE_FILES
            ${args_RESOURCE_FILES}
    )
endfunction()

# Public entry point for building python-and-resource-files only library.
# This was _specifically_ exposed to produce plugins for usdview, but can be useful
# for deploying python plugins in general that adhere to the installation structure
# prescribed by USDPluginTools.
#
function(usd_python_library NAME)
    set(options)

    set(oneValueArgs
    )

    set(multiValueArgs
        PYTHON_INSTALL_PREFIX
        PYTHON_FILES
        RESOURCE_FILES
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    if (ENABLE_PYTHON_SUPPORT)
        _usd_python_module(${NAME}
            PYTHON_INSTALL_PREFIX
                ${args_PYTHON_INSTALL_PREFIX}
            PYTHON_FILES
                ${args_PYTHON_FILES}
        )

        _usd_install_resource_files(${NAME}
            TYPE
                SHARED
            RESOURCE_FILES
                ${args_RESOURCE_FILES}
        )
    endif()
endfunction()

# Adds a USD-based C++ executable application.
function(usd_executable EXECUTABLE_NAME)

    set(options)

    set(oneValueArgs
    )

    set(multiValueArgs
        CPPFILES
        LIBRARIES
        INCLUDE_DIRS
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    # Define a new executable.
    add_executable(${EXECUTABLE_NAME}
        ${args_CPPFILES}
    )

    # Apply properties.
    _usd_target_properties(${EXECUTABLE_NAME}
        INCLUDE_DIRS
            ${args_INCLUDE_DIRS}
        LIBRARIES
            ${args_LIBRARIES}
    )

    # Install built executable.
    install(
        TARGETS ${EXECUTABLE_NAME}
        DESTINATION ${CMAKE_INSTALL_BINDIR}
    )

endfunction() # usd_executable

# Adds a USD-based cpp test which is executed by CTest.
function(usd_test TEST_TARGET)

    if (NOT BUILD_TESTING)
        return()
    endif()

    set(options)

    set(oneValueArgs
    )

    set(multiValueArgs
        CPPFILES
        LIBRARIES
        INCLUDE_DIRS
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    # Define a new executable.
    add_executable(${TEST_TARGET}
        ${args_CPPFILES}
    )

    # Apply properties.
    _usd_target_properties(${TEST_TARGET}
        INCLUDE_DIRS
            ${args_INCLUDE_DIRS}
        LIBRARIES
            ${args_LIBRARIES}
    )

    # Add the test target.
    add_test(
        NAME ${TEST_TARGET}
        COMMAND $<TARGET_FILE:${TEST_TARGET}>
    )

    # Set-up runtime environment variables for the test.
    _usd_set_test_properties(${TEST_TARGET} OFF)

endfunction()

# Adds a USD-based python test which is executed by CTest.
# The python file is simply executed by the python interpreter
# with no special arguments.
function(usd_python_test TEST_TARGET PYTHON_FILE)
    if (NOT ENABLE_PYTHON_SUPPORT)
        message(STATUS "ENABLE_PYTHON_SUPPORT is OFF, skipping python test: ${TEST_PREFIX} ${PYTHON_FILE}")
        return()
    endif()

    if (NOT BUILD_TESTING)
        return()
    endif()

    # Add a new test target.
    add_test(
        NAME ${TEST_TARGET}
        COMMAND ${PYTHON_EXECUTABLE} ${PYTHON_FILE}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )

    # Set-up runtime environment variables for the test.
    _usd_set_test_properties(${TEST_TARGET} ON)

endfunction()

#
# Internal function for building a USD-based C++ library.
#
function(_usd_cpp_library NAME)
    set(options)

    set(oneValueArgs
        TYPE
    )

    set(multiValueArgs
        PUBLIC_HEADERS_INSTALL_PREFIX
        PUBLIC_HEADERS
        PUBLIC_CLASSES
        CPPFILES
        LIBRARIES
        INCLUDE_DIRS
        PYTHON_CPPFILES
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    #
    # Resolve build variables.
    #

    # Check desired library type is supported.
    if (NOT args_TYPE STREQUAL "PLUGIN" AND NOT args_TYPE STREQUAL "SHARED")
        message(FATAL_ERROR
                "Building library type '${args_TYPE}' not supported.")
    endif()

    # Plugins do not provide public headers (nor public classes).
    if (args_TYPE STREQUAL "PLUGIN" AND (args_PUBLIC_HEADERS OR args_PUBLIC_CLASSES))
        message(FATAL_ERROR
                "'${args_TYPE}' library type does not support public headers nor classes.")
    endif()

    # Does not make sense to build a companion python module for a "plugin".
    if (args_TYPE STREQUAL "PLUGIN" AND args_PYMODULE_CPPFILES)
        message(FATAL_ERROR
                "'${args_TYPE}' library type does not support associated python module.")
    endif()

    # Expand class names to .cpp & .h files.
    foreach(className ${args_PUBLIC_CLASSES})
        list(APPEND args_CPPFILES ${className}.cpp)
        list(APPEND args_PUBLIC_HEADERS ${className}.h)
    endforeach()

    # If python support is enabled, then merge PYTHON_CPPFILES into CPPFILES.
    if (ENABLE_PYTHON_SUPPORT)
        if (args_PYTHON_CPPFILES)
            list(APPEND args_CPPFILES ${args_PYTHON_CPPFILES})
        endif()
    endif()


    # Determine public header install location.
    if (args_PUBLIC_HEADERS_INSTALL_PREFIX)
        set(PUBLIC_HEADERS_INSTALL_PREFIX ${args_PUBLIC_HEADERS_INSTALL_PREFIX}/${NAME})
    else()
        set(PUBLIC_HEADERS_INSTALL_PREFIX ${NAME})
    endif()

    # Copy public headers into build tree.
    file(
        COPY ${args_PUBLIC_HEADERS}
        DESTINATION ${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_INCLUDEDIR}/${PUBLIC_HEADERS_INSTALL_PREFIX}
    )

    # Install public headers.
    install(
        FILES ${args_PUBLIC_HEADERS}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PUBLIC_HEADERS_INSTALL_PREFIX}
    )

    # Convert "PLUGIN" into "MODULE".
    # (MODULE is CMake terminology for a dynamic lib only intended to be dlopen'ed at runtime).
    if (args_TYPE STREQUAL "PLUGIN")
        set(LIBRARY_TYPE "MODULE")
    else()
        set(LIBRARY_TYPE ${args_TYPE})
    endif()

    # Add a new library target.
    add_library(${NAME}
        ${LIBRARY_TYPE}
    )

    # Add sources for building the target.
    target_sources(${NAME}
        PRIVATE
            ${args_CPPFILES}
            ${args_PUBLIC_HEADERS}
    )

    # Apply common compiler properties, and include path properties.
    _usd_target_properties(${NAME}
        INCLUDE_DIRS
            ${args_INCLUDE_DIRS}
        LIBRARIES
            ${args_LIBRARIES}
    )

    _usd_compute_library_install_and_file_prefix(${args_TYPE}
        LIBRARY_INSTALL_PREFIX
        LIBRARY_FILE_PREFIX
    )

    if (args_TYPE STREQUAL "PLUGIN")
        # Install the plugin.
        # We do not need to export the target because plugins are _not_
        # meant to be built against.
        install(
            TARGETS ${NAME}
            LIBRARY DESTINATION ${LIBRARY_INSTALL_PREFIX}
        )
    else()
        # Setup SOVERSION & VERSION properties to create
        # NAMELINK, SONAME, and actual library with full version suffix.
        set_target_properties(${NAME}
            PROPERTIES
                SOVERSION ${CMAKE_PROJECT_VERSION_MAJOR}
                VERSION ${CMAKE_PROJECT_VERSION}
        )

        # Install the library and export it as an public target.
        install(
            TARGETS ${NAME}
            EXPORT ${CMAKE_PROJECT_NAME}-targets
            LIBRARY DESTINATION ${LIBRARY_INSTALL_PREFIX}
            RUNTIME DESTINATION ${LIBRARY_INSTALL_PREFIX}
        )
    endif()

    # Mirror installation structure in PROJECT_BINARY_DIR - for running tests against.
    if (BUILD_TESTING)
        add_custom_command(
            TARGET ${NAME}
            POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E create_symlink $<TARGET_FILE:${NAME}> ${PROJECT_BINARY_DIR}/${LIBRARY_INSTALL_PREFIX}/$<TARGET_FILE_NAME:${NAME}>
        )
    endif()

    # Update the target properties.
    set_target_properties(${NAME}
        PROPERTIES
            PREFIX "${LIBRARY_FILE_PREFIX}"
    )

endfunction() # _usd_cpp_library

#
# Internal function for build a C++ python module with python files.
#
function(_usd_python_module NAME)
    set(options)

    set(oneValueArgs
        TYPE
    )

    set(multiValueArgs
        LIBRARIES
        INCLUDE_DIRS
        PYTHON_INSTALL_PREFIX
        PYTHON_FILES
        PYMODULE_CPPFILES
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    # Public module name (example: UsdTri)
    _usd_get_python_module_name(${NAME} PYTHON_MODULE_NAME)

    # Construct the installation prefix for the python modules & files.
    if (args_PYTHON_INSTALL_PREFIX)
        set(PYTHON_INSTALL_PREFIX ${CMAKE_INSTALL_LIBDIR}/${USD_PYTHON_DIR}/${args_PYTHON_INSTALL_PREFIX}/${PYTHON_MODULE_NAME})
    else()
        set(PYTHON_INSTALL_PREFIX ${CMAKE_INSTALL_LIBDIR}/${USD_PYTHON_DIR}/${PYTHON_MODULE_NAME})
    endif()

    #
    # Python module / bindings.
    #

    if (args_PYMODULE_CPPFILES)

        # Target name.
        set(PYLIB_NAME "_${NAME}")

        # Add a library target.
        add_library(${PYLIB_NAME}
            MODULE
        )

        # Add sources for building the target.
        target_sources(${PYLIB_NAME}
            PRIVATE
                ${args_PYMODULE_CPPFILES}
        )

        # Lose the library prefix.
        if (MSVC)
            set_target_properties(${PYLIB_NAME}
                PROPERTIES
                    PREFIX ""
                    SUFFIX ".pyd"
            )
        else()
            set_target_properties(${PYLIB_NAME}
                PROPERTIES
                    PREFIX ""
            )
        endif()

        # Apply common compilation properties, and include path properties.
        _usd_target_properties(${PYLIB_NAME}
            INCLUDE_DIRS
                ${args_INCLUDE_DIRS}
            DEFINES
                MFB_PACKAGE_NAME=${NAME}
                MFB_ALT_PACKAGE_NAME=${NAME}
                MFB_PACKAGE_MODULE=${PYTHON_MODULE_NAME}
            LIBRARIES
                ${args_LIBRARIES}
                ${NAME}
        )

        # Mirror installation structure in PROJECT_BINARY_DIR - for running tests against.
        if (BUILD_TESTING)
            add_custom_command(
                TARGET ${PYLIB_NAME}
                POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E create_symlink $<TARGET_FILE:${PYLIB_NAME}> ${PROJECT_BINARY_DIR}/${PYTHON_INSTALL_PREFIX}/$<TARGET_FILE_NAME:${PYLIB_NAME}>
            )
        endif()

        # Install python module library.
        install(
            TARGETS
                ${PYLIB_NAME}
            RENAME
                ${PYLIB_NAME}${CMAKE_SHARED_LIBRARY_SUFFIX}
            DESTINATION
                ${PYTHON_INSTALL_PREFIX}
        )
    endif()

    #
    # Install python files.
    #

    if (args_PYTHON_FILES)

        # If tests are enabled - copy these files into project binary dir
        # _mirroring_ the install structure, such that we can run tests against
        # them.
        if (BUILD_TESTING)
            foreach(pythonFile ${args_PYTHON_FILES})
                file(
                    COPY ${CMAKE_CURRENT_SOURCE_DIR}/${pythonFile}
                    DESTINATION ${PROJECT_BINARY_DIR}/${PYTHON_INSTALL_PREFIX}
                )
            endforeach()
        endif()

        # Install python files.
        install(
            FILES
                ${args_PYTHON_FILES}
            DESTINATION
                ${PYTHON_INSTALL_PREFIX}
        )
    endif()
endfunction() # _usd_python_module

#
# Internal function for installing resource files (plugInfo, etc).
#
function(_usd_install_resource_files NAME)
    set(options)

    set(oneValueArgs
        TYPE
    )

    set(multiValueArgs
        RESOURCE_FILES
    )

    cmake_parse_arguments(args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    _usd_compute_library_install_and_file_prefix(${args_TYPE}
        LIBRARY_INSTALL_PREFIX
        LIBRARY_FILE_PREFIX
    )

    # Compose the full name of the library.
    # This will be used when performing variable substition on the plugInfo.json resource file.
    set(LIBRARY_FILE_NAME ${LIBRARY_FILE_PREFIX}${NAME}${CMAKE_SHARED_LIBRARY_SUFFIX})

    # Plugin resources will be installed as a 'usd' subdir under the library install location.
    set(RESOURCES_INSTALL_PREFIX ${LIBRARY_INSTALL_PREFIX}/${USD_PLUG_INFO_ROOT_DIR})

    foreach(resourceFile ${args_RESOURCE_FILES})

        # Apply string substitution to plugInfo.json, copy to binary dir.
        if (${resourceFile} STREQUAL "plugInfo.json")
            file(RELATIVE_PATH
                RESOURCE_TO_LIBRARY_PATH
                ${CMAKE_INSTALL_PREFIX}/${RESOURCES_INSTALL_PREFIX}/${NAME}
                ${CMAKE_INSTALL_PREFIX}/${LIBRARY_INSTALL_PREFIX}/${LIBRARY_FILE_NAME})

            _usd_plug_info_subst(${NAME} ${RESOURCE_TO_LIBRARY_PATH} ${resourceFile})

            # Update resourceFile var to path of substituted file.
            set(resourceFile "${CMAKE_CURRENT_BINARY_DIR}/${resourceFile}")
        endif()

        # Install into project binary dir (for tests)
        if (BUILD_TESTING)
            file(
                COPY ${resourceFile}
                DESTINATION ${PROJECT_BINARY_DIR}/${RESOURCES_INSTALL_PREFIX}/${NAME}/${USD_PLUG_INFO_RESOURCES_DIR}
            )
        endif()

        # Install resource file.
        install(
            FILES
                ${resourceFile}
            DESTINATION
                ${RESOURCES_INSTALL_PREFIX}/${NAME}/${USD_PLUG_INFO_RESOURCES_DIR}
        )
    endforeach()
endfunction() # _usd_install_resource_files

# Internal utility for differentiating between  "shared library" vs "plugin".
#
# Outputs:
#   LIBRARY_INSTALL_PREFIX: The sub-directory under installation root where the
#       shared library will be deployed.
#   LIBRARY_FILE_PREFIX: The filename prefix of the shared library. ("lib" on Linux)
function(_usd_compute_library_install_and_file_prefix
    TYPE
    LIBRARY_INSTALL_PREFIX
    LIBRARY_FILE_PREFIX
)
    if (TYPE STREQUAL "PLUGIN")
        set(${LIBRARY_INSTALL_PREFIX} ${USD_PLUGIN_DIR} PARENT_SCOPE)
        set(${LIBRARY_FILE_PREFIX} "" PARENT_SCOPE)
    else()
        set(${LIBRARY_INSTALL_PREFIX} ${CMAKE_INSTALL_LIBDIR} PARENT_SCOPE)
        set(${LIBRARY_FILE_PREFIX} ${CMAKE_SHARED_LIBRARY_PREFIX} PARENT_SCOPE)
    endif()
endfunction()

# Converts a library name, such as _tf.so to the internal module name given
# our naming conventions, e.g. Tf
function(_usd_get_python_module_name
    LIBRARY_FILENAME
    MODULE_NAME
)
    # Library names are either something like tf.so for shared libraries
    # or _tf.pyd/_tf_d.pyd for Python module libraries.
    # We want to strip off the leading "_" and the trailing "_d".
    set(LIBNAME ${LIBRARY_FILENAME})
    string(REGEX REPLACE "^_" "" LIBNAME ${LIBNAME})
    string(SUBSTRING ${LIBNAME} 0 1 LIBNAME_FL)
    string(TOUPPER ${LIBNAME_FL} LIBNAME_FL)
    string(SUBSTRING ${LIBNAME} 1 -1 LIBNAME_SUFFIX)
    set(${MODULE_NAME}
        "${LIBNAME_FL}${LIBNAME_SUFFIX}"
        PARENT_SCOPE
    )
endfunction() # _usd_get_python_module_name

# Performs variable substitution in a plugInfo.json file.
function(_usd_plug_info_subst
    LIBRARY_TARGET
    RESOURCE_TO_LIBRARY_PATH
    PLUG_INFO_PATH
)
    set(PLUG_INFO_ROOT "..")
    set(PLUG_INFO_LIBRARY_PATH ${RESOURCE_TO_LIBRARY_PATH})
    set(PLUG_INFO_RESOURCE_PATH ${USD_PLUG_INFO_RESOURCES_DIR})
    configure_file(
        ${PLUG_INFO_PATH}
        ${CMAKE_CURRENT_BINARY_DIR}/${PLUG_INFO_PATH}
    )
endfunction() # _usd_plug_info_subst

# Common target-specific properties to apply to library targets.
function(_usd_target_properties
    TARGET_NAME
)
    set(options)
    set(oneValueArgs)
    set(multiValueArgs
        INCLUDE_DIRS
        DEFINES
        LIBRARIES
    )

    cmake_parse_arguments(
        args
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    # Add additional platform-speific compile definitions
    set (platform_definitions)
    if (MSVC)
        # Depending on which parts of USD the project uses, additional definitions for windows may need
        # to be added. A explicit list of MSVC definitions USD builds with can be found in the USD source at:
        #   cmake/defaults/CXXDefaults.cmake
        #   cmake/defaults/msvcdefaults.cmake
        list(APPEND platform_definitions NOMINMAX)
    endif()

    target_compile_definitions(${TARGET_NAME}
        PRIVATE
            ${args_DEFINES}
            ${platform_definitions}
    )

    target_compile_features(${TARGET_NAME}
        PRIVATE
            cxx_std_14
    )

    # Exported include paths for this target.
    target_include_directories(${TARGET_NAME}
        INTERFACE
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )

    # Project includes for building against.
    target_include_directories(${TARGET_NAME}
        PRIVATE
            $<BUILD_INTERFACE:${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_INCLUDEDIR}>
    )

    # Setup include path for binary dir.
    # We set external includes as SYSTEM so that their warnings are muted.
    set(_INCLUDE_DIRS "")
    list(APPEND _INCLUDE_DIRS ${args_INCLUDE_DIRS} ${USD_INCLUDE_DIR} ${TBB_INCLUDE_DIRS})
    if (ENABLE_PYTHON_SUPPORT)
        list(APPEND _INCLUDE_DIRS ${PYTHON_INCLUDE_DIR} ${Boost_INCLUDE_DIR})
    endif()
    target_include_directories(${TARGET_NAME}
        SYSTEM
        PRIVATE
            ${_INCLUDE_DIRS}
    )

    # Set-up library search path.
    target_link_directories(${TARGET_NAME}
        PRIVATE
            ${USD_LIBRARY_DIR}
    )

    # Link to libraries.
    set(_LINK_LIBRARIES "")
    list(APPEND _LINK_LIBRARIES ${args_LIBRARIES} ${TBB_LIBRARIES})
    if (ENABLE_PYTHON_SUPPORT)
        list(APPEND _LINK_LIBRARIES ${Boost_PYTHON_LIBRARY} ${PYTHON_LIBRARIES})
    endif()
    target_link_libraries(${TARGET_NAME}
        PRIVATE
            ${_LINK_LIBRARIES}
    )
endfunction() # _usd_target_properties

# Set-up runtime environment variables for the test.
# When USE_PYTHONPATH is one, will include project python libraries
function(_usd_set_test_properties
    TARGET_NAME
    USE_PYTHONPATH
)
    # The paths refer to the build tree (which mirrors the final installation).
    # The first path for an env var needs the 'VARNAME=' prepended.
    # On windows, calls to "$ENV{}" must be sanitized to replace back slashes with forward slashes
    # Env vars after the first must be prepended with a double escaped semicolon to be recognized. 

    set(TEST_ENV_VARS "")

    # Building the PXR_PLUGINPATH_NAME environment variable
    set(TEST_PXR_PLUGINPATH_NAME "$ENV{PXR_PLUGINPATH_NAME}")
    if (MSVC)
        string(REGEX REPLACE "\\\\" "/" TEST_PXR_PLUGINPATH_NAME "${TEST_PXR_PLUGINPATH_NAME}")
    endif()
    string(PREPEND TEST_PXR_PLUGINPATH_NAME "PXR_PLUGINPATH_NAME=")
    list(APPEND TEST_PXR_PLUGINPATH_NAME
        "${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}/${USD_PLUG_INFO_ROOT_DIR}"
        "${PROJECT_BINARY_DIR}/${USD_PLUGIN_DIR}/${USD_PLUG_INFO_ROOT_DIR}"
    )
    list(APPEND TEST_ENV_VARS "${TEST_PXR_PLUGINPATH_NAME}")

    # Building the PYTHONPATH  environment variable
    if (USE_PYTHONPATH)
        set(TEST_PYTHON_PATH "$ENV{PYTHONPATH}")
        if (MSVC)
            string(REGEX REPLACE "\\\\" "/" TEST_PYTHON_PATH "${TEST_PYTHON_PATH}")
        endif()
        string(PREPEND TEST_PYTHON_PATH "PYTHONPATH=")
        string(PREPEND TEST_PYTHON_PATH "\\;")
        list(APPEND TEST_PYTHON_PATH 
            "${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}/python"
            "${USD_ROOT}/${CMAKE_INSTALL_LIBDIR}/python"
        )

        list(APPEND TEST_ENV_VARS "${TEST_PYTHON_PATH}")
    endif()

    # Add MSVC-required paths
    if (MSVC)
        # Building the PATH  environment variable
        set(TEST_PATH "$ENV{PATH}")
        string(REGEX REPLACE "\\\\" "/" TEST_PATH "${TEST_PATH}")
        string(PREPEND TEST_PATH "PATH=")
        string(PREPEND TEST_PATH "\\;")
        list(APPEND TEST_PATH 
            "${PROJECT_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}"
            "${USD_ROOT}/${CMAKE_INSTALL_LIBDIR}"
            "${USD_ROOT}/${CMAKE_INSTALL_BINDIR}"
        )

        list(APPEND TEST_ENV_VARS "${TEST_PATH}")
    endif()


    if (MSVC)
        list(JOIN TEST_ENV_VARS "\\;" TEST_ENV_VARS)
    else()
        list(JOIN TEST_ENV_VARS ":" TEST_ENV_VARS)
    endif()

    set_tests_properties(${TARGET_NAME}
        PROPERTIES
            ENVIRONMENT
            "${TEST_ENV_VARS}"
    )

endfunction() # _usd_set_test_properties
