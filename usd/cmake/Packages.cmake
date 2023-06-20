# Discovery of the dependencies of USDPluginExamples.

# Boost & python.
if (ENABLE_PYTHON_SUPPORT)
    # Find python libraries.
    if (USE_PYTHON_3)
        find_package(PythonInterp 3.0 REQUIRED)
        find_package(PythonLibs 3.0 REQUIRED)
    else()
        find_package(PythonInterp 2.7 REQUIRED)
        find_package(PythonLibs 2.7 REQUIRED)
    endif()

    # Pick up boost version variables.
    find_package(Boost REQUIRED)

    # We can use Boost_VERSION_STRING in CMake 3.14+.
    set(boost_version_string "${Boost_MAJOR_VERSION}.${Boost_MINOR_VERSION}.${Boost_SUBMINOR_VERSION}")

    # Boost provided cmake files in 1.70 and above causes inconsistent failures.
    if (${boost_version_string} VERSION_GREATER_EQUAL "1.70")
        option(Boost_NO_BOOST_CMAKE "Disable boost-provided cmake config" ON)
        if (Boost_NO_BOOST_CMAKE)
            message(STATUS "Disabling boost-provided cmake config")
        endif()
    endif()

    if (${boost_version_string} VERSION_GREATER_EQUAL "1.67")
        # In boost-1.67 and greater, the boost python component includes the
        # python major and minor version as part of its name.
        set(PYTHON_VERSION_DOTLESS "${PYTHON_VERSION_MAJOR}${PYTHON_VERSION_MINOR}")
        find_package(Boost
            COMPONENTS
                python${PYTHON_VERSION_DOTLESS}
            REQUIRED
        )
        set(Boost_PYTHON_LIBRARY "${Boost_PYTHON${PYTHON_VERSION_DOTLESS}_LIBRARY}")
    else()
        find_package(Boost
            COMPONENTS
                python
            REQUIRED
        )
    endif()
endif()

# USD & TBB
include(${USD_ROOT}/pxrConfig.cmake)
find_package(TBB REQUIRED)
