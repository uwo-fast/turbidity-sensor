cmake_minimum_required(VERSION 3.16)
project(turbidity VERSION 0.2.0 LANGUAGES C)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

option(BUILD_TESTS "Build the test suite" ON)
option(BUILD_TOOLS "Build command-line tools" ON)
option(BUILD_EXAMPLES "Build host examples" ON)
option(TURBIDITY_WARNINGS_AS_ERRORS "Treat compiler warnings as errors" OFF)
option(TURBIDITY_REGENERATE_CALIBRATION "Regenerate calibration artifacts from vendor data during the build" OFF)

if(TURBIDITY_REGENERATE_CALIBRATION)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)

    add_custom_target(turbidity_generate_calibration
        COMMAND ${Python3_EXECUTABLE} ${PROJECT_SOURCE_DIR}/tools/generate_vendor_calibration.py
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        BYPRODUCTS
            ${PROJECT_SOURCE_DIR}/data/calibration/tst10-calibration.csv
            ${PROJECT_SOURCE_DIR}/data/calibration/tsw10-calibration.csv
            ${PROJECT_SOURCE_DIR}/data/calibration/tst10-fit.txt
            ${PROJECT_SOURCE_DIR}/data/calibration/tsw10-fit.txt
            ${PROJECT_SOURCE_DIR}/src/turbidity_model_data.generated.h
        DEPENDS
            ${PROJECT_SOURCE_DIR}/tools/generate_vendor_calibration.py
            ${PROJECT_SOURCE_DIR}/data/calibration/vendor-data/tst10-high.csv
            ${PROJECT_SOURCE_DIR}/data/calibration/vendor-data/tst10-low.csv
            ${PROJECT_SOURCE_DIR}/data/calibration/vendor-data/tsw10-high.csv
            ${PROJECT_SOURCE_DIR}/data/calibration/vendor-data/tsw10-low.csv
        COMMENT "Regenerating vendor-derived calibration artifacts"
        VERBATIM
    )
endif()

if(MSVC)
    set(TURBIDITY_WARNING_FLAGS /W4)
    if(TURBIDITY_WARNINGS_AS_ERRORS)
        list(APPEND TURBIDITY_WARNING_FLAGS /WX)
    endif()
else()
    set(TURBIDITY_WARNING_FLAGS -Wall -Wextra -Wpedantic -Wshadow -Wconversion)
    if(TURBIDITY_WARNINGS_AS_ERRORS)
        list(APPEND TURBIDITY_WARNING_FLAGS -Werror)
    endif()
endif()

add_library(turbidity STATIC
    src/turbidity.c
)
add_library(turbidity::turbidity ALIAS turbidity)

set_target_properties(turbidity PROPERTIES
    OUTPUT_NAME turbidity
    EXPORT_NAME turbidity
)

target_compile_features(turbidity PUBLIC c_std_99)

target_include_directories(turbidity
    PUBLIC
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    PRIVATE
        ${PROJECT_SOURCE_DIR}/src
)

if(TURBIDITY_REGENERATE_CALIBRATION)
    add_dependencies(turbidity turbidity_generate_calibration)
endif()

target_compile_options(turbidity PRIVATE ${TURBIDITY_WARNING_FLAGS})
if(NOT MSVC)
    target_link_libraries(turbidity PUBLIC m)
endif()

if(BUILD_TOOLS OR BUILD_TESTS)
    add_executable(turbidity_calibrate
        tools/turbidity_calibrate.c
    )
    target_link_libraries(turbidity_calibrate PRIVATE turbidity)
    target_compile_options(turbidity_calibrate PRIVATE ${TURBIDITY_WARNING_FLAGS})
endif()

if(BUILD_EXAMPLES OR BUILD_TESTS)
    add_executable(turbidity_stream
        examples/posix/turbidity_stream.c
    )
    target_include_directories(turbidity_stream PRIVATE
        ${PROJECT_SOURCE_DIR}/examples/common
    )
    target_link_libraries(turbidity_stream PRIVATE turbidity)
    target_compile_options(turbidity_stream PRIVATE ${TURBIDITY_WARNING_FLAGS})
endif()

install(TARGETS turbidity
    EXPORT turbidityTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

if(BUILD_TOOLS)
    install(TARGETS turbidity_calibrate
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    )
endif()

if(BUILD_EXAMPLES)
    install(TARGETS turbidity_stream
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    )
endif()

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

write_basic_package_version_file(
    ${PROJECT_BINARY_DIR}/turbidityConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    ${PROJECT_SOURCE_DIR}/cmake/turbidityConfig.cmake.in
    ${PROJECT_BINARY_DIR}/turbidityConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/turbidity
)

install(FILES
    ${PROJECT_BINARY_DIR}/turbidityConfig.cmake
    ${PROJECT_BINARY_DIR}/turbidityConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/turbidity
)

install(EXPORT turbidityTargets
    FILE turbidityTargets.cmake
    NAMESPACE turbidity::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/turbidity
)

if(BUILD_TESTS)
    enable_testing()

    add_executable(turbidity_test_core
        tests/test_turbidity.c
    )
    target_include_directories(turbidity_test_core PRIVATE
        ${PROJECT_SOURCE_DIR}/src
    )
    target_link_libraries(turbidity_test_core PRIVATE turbidity)
    target_compile_options(turbidity_test_core PRIVATE ${TURBIDITY_WARNING_FLAGS})
    add_test(NAME turbidity_core COMMAND turbidity_test_core)

    add_executable(turbidity_test_cli_contracts
        tests/test_cli_contracts.c
    )
    target_link_libraries(turbidity_test_cli_contracts PRIVATE turbidity)
    target_compile_options(turbidity_test_cli_contracts PRIVATE ${TURBIDITY_WARNING_FLAGS})
    add_test(
        NAME turbidity_cli_contracts
        COMMAND turbidity_test_cli_contracts
            $<TARGET_FILE:turbidity_stream>
            $<TARGET_FILE:turbidity_calibrate>
    )

    configure_file(
        ${PROJECT_SOURCE_DIR}/tests/package_smoke/run_package_smoke.cmake.in
        ${PROJECT_BINARY_DIR}/tests/package_smoke/run_package_smoke.cmake
        @ONLY
    )
    add_test(
        NAME turbidity_package_smoke
        COMMAND ${CMAKE_COMMAND} -P ${PROJECT_BINARY_DIR}/tests/package_smoke/run_package_smoke.cmake
    )
endif()
