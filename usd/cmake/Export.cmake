# This module is for exporting targets and installing CMake package
# files which are used to import _this_ project into _other_ projects
# in a robust manner.
#
# Note For developers using USDPluginExamples as a template:
# Depending on the nature of your project, this module is optional.

# Install exported library targets.
install(
    EXPORT ${CMAKE_PROJECT_NAME}-targets
    NAMESPACE USDPluginExamples::
    FILE ${CMAKE_PROJECT_NAME}Targets.cmake
    DESTINATION cmake
)

# Configure and write <Project>Config.cmake to provide package import entry point.
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/Config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}Config.cmake
    @ONLY
)

# Configure and write  <Project>ConfigVersion.cmake for version compatibility management.
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}ConfigVersion.cmake
    VERSION ${CMAKE_PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Install the package configuration files.
install(
    FILES
        ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}Config.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}ConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_PREFIX}
)
